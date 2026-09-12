"""Tests for Wavelet frequency synthesis and Temporal motion stabilization engines."""

import cv2
import numpy as np
import pytest
import torch

from core.temporal_engine import TemporalWarpEngine
from core.wavelet_engine import WaveletFrequencySynthesizer, dwt2, idwt2


def test_wavelet_perfect_reconstruction():
    """Verify DWT2 and IDWT2 exact invertibility with zero information loss."""
    x = torch.randn(2, 3, 64, 64)
    ll, lh, hl, hh = dwt2(x)

    assert ll.shape == (2, 3, 32, 32)
    assert lh.shape == (2, 3, 32, 32)
    assert hl.shape == (2, 3, 32, 32)
    assert hh.shape == (2, 3, 32, 32)

    reconstructed = idwt2(ll, lh, hl, hh)
    max_error = torch.max(torch.abs(x - reconstructed)).item()
    assert max_error < 1e-5


def test_wavelet_synthesizer_preserves_shape_and_range():
    """Verify WaveletFrequencySynthesizer preserves image geometry and uint8 range."""
    synthesizer = WaveletFrequencySynthesizer(device=torch.device("cpu"))
    base = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
    upscaled = np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)

    out = synthesizer.synthesize(base, upscaled, hf_boost=1.15)
    assert out.shape == upscaled.shape
    assert out.dtype == np.uint8
    assert np.min(out) >= 0
    assert np.max(out) <= 255


def test_temporal_engine_motion_warping():
    """Verify backward motion warping aligns shifted features across frames."""
    engine = TemporalWarpEngine(history_blend=0.8, flow_scale=1.0)

    # Frame 1: center square
    f1_raw = np.zeros((120, 160, 3), dtype=np.uint8)
    f1_raw[40:80, 50:110] = 180
    f1_enhanced = cv2.resize(f1_raw, (320, 240))

    out1 = engine.process_frame(f1_raw, f1_enhanced)
    assert np.array_equal(out1, f1_enhanced)

    # Frame 2: square translated right by 6 pixels
    f2_raw = np.zeros((120, 160, 3), dtype=np.uint8)
    f2_raw[40:80, 56:116] = 180
    f2_enhanced = cv2.resize(f2_raw, (320, 240))

    out2 = engine.process_frame(f2_raw, f2_enhanced)
    assert out2.shape == f2_enhanced.shape
    assert out2.dtype == np.uint8


def test_temporal_engine_scene_cut_reset():
    """Verify temporal history resets cleanly on abrupt scene cuts."""
    engine = TemporalWarpEngine()

    f1_raw = np.zeros((64, 64, 3), dtype=np.uint8)
    f1_up = np.zeros((128, 128, 3), dtype=np.uint8)
    engine.process_frame(f1_raw, f1_up)

    # Abrupt cut to pure white
    f2_raw = np.ones((64, 64, 3), dtype=np.uint8) * 255
    f2_up = np.ones((128, 128, 3), dtype=np.uint8) * 255

    out2 = engine.process_frame(f2_raw, f2_up)
    # On scene cut, should not ghost back to black
    assert np.mean(out2) > 200
