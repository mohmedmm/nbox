"""Tests for hardware detection."""

from core.hardware import detect, HardwareProfile


def test_hardware_detect():
    profile = detect()
    assert isinstance(profile, HardwareProfile)
    assert profile.backend in ("cuda", "directml", "cpu")
    assert profile.recommended_tile in (256, 512, 1024)
