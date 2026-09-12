"""ffprobe wrapper — extracts video metadata."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass


@dataclass
class VideoInfo:
    path: str
    width: int
    height: int
    fps: float
    duration: float      # seconds
    frame_count: int
    codec: str
    audio_codec: str | None
    bitrate: int         # kb/s


def probe(path: str) -> VideoInfo:
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams", "-show_format",
        path,
    ]
    raw = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=15)
    data = json.loads(raw)

    video_streams = [s for s in data.get("streams", []) if s.get("codec_type") == "video"]
    if not video_streams:
        raise ValueError(f"No video stream found in {path}")
    video_stream = video_streams[0]
    audio_streams = [s for s in data.get("streams", []) if s.get("codec_type") == "audio"]

    fps = 30.0
    for rate_key in ("r_frame_rate", "avg_frame_rate"):
        val = video_stream.get(rate_key, "")
        if "/" in val:
            try:
                num, den = (int(x) for x in val.split("/"))
                if den > 0 and num > 0:
                    fps = num / den
                    break
            except (ValueError, ZeroDivisionError):
                pass

    try:
        duration = float(data.get("format", {}).get("duration", 0) or 0)
    except (ValueError, TypeError):
        duration = 0.0

    raw_frames = video_stream.get("nb_frames")
    frame_count = 0
    if raw_frames is not None and str(raw_frames).isdigit():
        frame_count = int(raw_frames)
    if frame_count <= 0 and duration > 0 and fps > 0:
        frame_count = int(duration * fps)

    try:
        bitrate = int(data.get("format", {}).get("bit_rate", 0) or 0) // 1000
    except (ValueError, TypeError):
        bitrate = 0

    return VideoInfo(
        path=path,
        width=int(video_stream.get("width", 0)),
        height=int(video_stream.get("height", 0)),
        fps=fps,
        duration=duration,
        frame_count=frame_count,
        codec=video_stream.get("codec_name", "unknown"),
        audio_codec=audio_streams[0].get("codec_name") if audio_streams else None,
        bitrate=bitrate,
    )

