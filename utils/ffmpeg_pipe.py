"""Real-time ffmpeg frame pipe: read raw frames in, write upscaled frames out."""

from __future__ import annotations

import subprocess
from contextlib import contextmanager
from typing import Generator

import numpy as np

from utils.ffprobe import VideoInfo


def _reader_cmd(info: VideoInfo) -> list[str]:
    return [
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-i", info.path,
        "-f", "rawvideo",
        "-pix_fmt", "bgr24",
        "-vf", f"scale={info.width}:{info.height}",
        "pipe:1",
    ]


def _writer_cmd(
    out_path: str,
    width: int,
    height: int,
    fps: float,
    audio_src: str | None,
    crf: int = 18,
    use_nvenc: bool = True,
) -> list[str]:
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "bgr24",
        "-r", str(fps),
        "-i", "pipe:0",
    ]
    if audio_src:
        cmd += ["-i", audio_src, "-c:a", "copy", "-shortest"]

    if use_nvenc:
        cmd += [
            "-c:v", "h264_nvenc",
            "-preset", "p5",
            "-cq", str(crf),
            "-pix_fmt", "yuv420p",
            out_path,
        ]
    else:
        cmd += [
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", str(crf),
            "-pix_fmt", "yuv420p",
            out_path,
        ]
    return cmd


@contextmanager
def frame_pipe(
    info: VideoInfo,
    out_path: str,
    out_width: int,
    out_height: int,
    crf: int = 18,
    use_nvenc: bool = True,
) -> Generator[tuple[subprocess.Popen, subprocess.Popen], None, None]:
    """Yields (reader, writer) processes. Caller feeds frames through the writer stdin."""
    frame_bytes = info.width * info.height * 3

    reader = subprocess.Popen(
        _reader_cmd(info),
        stdout=subprocess.PIPE,
        bufsize=frame_bytes * 4,
    )
    writer = subprocess.Popen(
        _writer_cmd(out_path, out_width, out_height, info.fps, info.path, crf, use_nvenc=use_nvenc),
        stdin=subprocess.PIPE,
        bufsize=out_width * out_height * 3 * 4,
    )
    try:
        yield reader, writer
    finally:
        if writer.stdin:
            try:
                writer.stdin.close()
            except (BrokenPipeError, OSError):
                pass
        reader.wait()
        writer.wait()


def read_frame(reader: subprocess.Popen, width: int, height: int) -> np.ndarray | None:
    raw = reader.stdout.read(width * height * 3)
    if len(raw) < width * height * 3:
        return None
    return np.frombuffer(raw, dtype=np.uint8).reshape((height, width, 3)).copy()


def write_frame(writer: subprocess.Popen, frame: np.ndarray) -> None:
    writer.stdin.write(frame.tobytes())
