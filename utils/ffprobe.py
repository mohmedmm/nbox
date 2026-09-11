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

    video_stream = next(s for s in data["streams"] if s["codec_type"] == "video")
    audio_streams = [s for s in data["streams"] if s["codec_type"] == "audio"]

    fps_num, fps_den = (int(x) for x in video_stream["r_frame_rate"].split("/"))
    fps = fps_num / fps_den

    duration = float(data["format"].get("duration", 0))
    frame_count = int(video_stream.get("nb_frames", 0)) or int(duration * fps)

    return VideoInfo(
        path=path,
        width=int(video_stream["width"]),
        height=int(video_stream["height"]),
        fps=fps,
        duration=duration,
        frame_count=frame_count,
        codec=video_stream["codec_name"],
        audio_codec=audio_streams[0]["codec_name"] if audio_streams else None,
        bitrate=int(data["format"].get("bit_rate", 0)) // 1000,
    )
