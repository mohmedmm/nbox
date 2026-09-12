"""Video neural upscaling pipeline engine with real-time frame streaming."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Callable

import cv2
import numpy as np
import torch

from core.hardware import detect as detect_hardware
from core.models import NeuralUpsampler
from utils.ffmpeg_pipe import frame_pipe, read_frame, write_frame
from utils.ffprobe import VideoInfo, probe


@dataclass
class ProgressUpdate:
    frame_idx: int
    total_frames: int
    percent: float
    fps: float
    eta_seconds: float
    original_frame: np.ndarray | None = None
    upscaled_frame: np.ndarray | None = None


@dataclass
class UpscaleConfig:
    input_path: str
    output_path: str
    model_id: str = "realesr-animevideov3"
    target_resolution: tuple[int, int] | None = None  # (width, height) or None for native model scale
    tile_size: int = 512
    use_nvenc: bool = True
    crf: int = 18
    preview_interval: int = 1  # Emit preview every N frames (1 = every frame for real-time smoothness)
    enable_temporal: bool = True
    enable_wavelet: bool = True



class VideoUpscaler:
    """Core GPU-accelerated video upscaler with real-time frame streaming."""

    def __init__(self, config: UpscaleConfig) -> None:
        self.config = config
        self._is_cancelled = False
        self._is_paused = False

    def cancel(self) -> None:
        self._is_cancelled = True

    def pause(self) -> None:
        self._is_paused = True

    def resume(self) -> None:
        self._is_paused = False

    def run(
        self,
        progress_cb: Callable[[ProgressUpdate], None] | None = None,
        model_download_cb: Callable[[int], None] | None = None,
    ) -> str:
        """Run the upscale pipeline and return output file path."""
        self._is_cancelled = False
        self._is_paused = False

        if not os.path.exists(self.config.input_path):
            raise FileNotFoundError(f"Input video not found: {self.config.input_path}")

        # Probe video streams
        info: VideoInfo = probe(self.config.input_path)

        # Hardware backend setup (Pure GPU priority)
        hw = detect_hardware()
        device = torch.device("cuda" if hw.backend == "cuda" and torch.cuda.is_available() else "cpu")
        tile = self.config.tile_size or hw.recommended_tile

        # Load Neural Model & DLSS5 Generative Sharpener
        upsampler = NeuralUpsampler(
            model_id=self.config.model_id,
            device=device,
            tile=tile,
            half=device.type == "cuda",
            progress_cb=model_download_cb,
        )
        from core.neural_sharpener import DLSS5NeuralSharpener
        from core.temporal_engine import TemporalWarpEngine
        from core.wavelet_engine import WaveletFrequencySynthesizer

        sharpener = DLSS5NeuralSharpener(mode="ultra_sharp", device=device)
        temporal_engine = TemporalWarpEngine() if self.config.enable_temporal else None
        wavelet_engine = WaveletFrequencySynthesizer(device=device) if self.config.enable_wavelet else None

        # Calculate output dimensions
        native_out_w = info.width * upsampler.scale
        native_out_h = info.height * upsampler.scale

        if self.config.target_resolution:
            final_w, final_h = self.config.target_resolution
        else:
            final_w, final_h = native_out_w, native_out_h

        # Ensure dimensions are even for video encoders
        final_w = final_w + (final_w % 2)
        final_h = final_h + (final_h % 2)

        os.makedirs(os.path.dirname(os.path.abspath(self.config.output_path)), exist_ok=True)

        start_time = time.time()
        frames_processed = 0
        fps_ema = 0.0

        with frame_pipe(
            info=info,
            out_path=self.config.output_path,
            out_width=final_w,
            out_height=final_h,
            crf=self.config.crf,
            use_nvenc=self.config.use_nvenc and (hw.backend == "cuda"),
        ) as (reader, writer):
            while not self._is_cancelled:
                while self._is_paused and not self._is_cancelled:
                    time.sleep(0.1)

                frame_start = time.time()
                raw_frame = read_frame(reader, info.width, info.height)
                if raw_frame is None:
                    break  # End of video stream

                # Neural upscaling pass + nbox subtle detail injection
                enhanced = upsampler.enhance(raw_frame)
                enhanced = sharpener.enhance(enhanced, intensity=0.35)

                if wavelet_engine is not None:
                    enhanced = wavelet_engine.synthesize(raw_frame, enhanced, hf_boost=1.12)

                if temporal_engine is not None:
                    enhanced = temporal_engine.process_frame(raw_frame, enhanced)



                # Resize if user selected custom target resolution (e.g. strict 2K / 1440p)
                if (enhanced.shape[1] != final_w) or (enhanced.shape[0] != final_h):
                    enhanced = cv2.resize(
                        enhanced,
                        (final_w, final_h),
                        interpolation=cv2.INTER_LANCZOS4,
                    )

                # Write upscaled frame into video encoder pipe
                write_frame(writer, enhanced)

                frames_processed += 1
                frame_duration = max(time.time() - frame_start, 1e-4)
                instant_fps = 1.0 / frame_duration
                fps_ema = instant_fps if fps_ema == 0.0 else (0.85 * fps_ema + 0.15 * instant_fps)

                total = max(info.frame_count, 1)
                percent = min((frames_processed / total) * 100.0, 100.0)
                remaining_frames = max(total - frames_processed, 0)
                eta = remaining_frames / fps_ema if fps_ema > 0 else 0.0

                if progress_cb and (frames_processed % self.config.preview_interval == 0):
                    progress_cb(
                        ProgressUpdate(
                            frame_idx=frames_processed,
                            total_frames=total,
                            percent=percent,
                            fps=fps_ema,
                            eta_seconds=eta,
                            original_frame=raw_frame,
                            upscaled_frame=enhanced,
                        )
                    )

        if self._is_cancelled:
            if os.path.exists(self.config.output_path):
                try:
                    os.remove(self.config.output_path)
                except OSError:
                    pass
            raise InterruptedError("Upscaling process cancelled by user.")

        return self.config.output_path
