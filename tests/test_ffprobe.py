import json
from unittest.mock import patch
import pytest
from utils.ffprobe import probe


def test_probe_handles_valid_stream():
    sample_json = json.dumps({
        "streams": [
            {
                "codec_type": "video",
                "width": 1920,
                "height": 1080,
                "r_frame_rate": "60/1",
                "nb_frames": "1800",
                "codec_name": "h264",
            }
        ],
        "format": {"duration": "30.0", "bit_rate": "5000000"},
    }).encode("utf-8")

    with patch("subprocess.check_output", return_value=sample_json):
        info = probe("mock.mp4")

    assert info.width == 1920
    assert info.height == 1080
    assert info.fps == 60.0
    assert info.frame_count == 1800
    assert info.duration == 30.0
    assert info.bitrate == 5000


def test_probe_handles_na_frame_count_and_zero_framerate():
    sample_json = json.dumps({
        "streams": [
            {
                "codec_type": "video",
                "width": 1280,
                "height": 720,
                "r_frame_rate": "0/0",
                "avg_frame_rate": "24/1",
                "nb_frames": "N/A",
                "codec_name": "vp9",
            }
        ],
        "format": {"duration": "10.0"},
    }).encode("utf-8")

    with patch("subprocess.check_output", return_value=sample_json):
        info = probe("mock.webm")

    assert info.fps == 24.0
    assert info.frame_count == 240
    assert info.codec == "vp9"


def test_probe_raises_on_audio_only():
    sample_json = json.dumps({
        "streams": [{"codec_type": "audio", "codec_name": "aac"}],
        "format": {"duration": "60.0"},
    }).encode("utf-8")

    with patch("subprocess.check_output", return_value=sample_json):
        with pytest.raises(ValueError, match="No video stream found"):
            probe("audio_only.m4a")
