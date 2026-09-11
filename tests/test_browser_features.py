"""Unit tests for DLSS 5 generative neural sharpener and browser hook."""

import numpy as np
import pytest
from core.browser_hook import detect_active_browsers
from core.neural_sharpener import DLSS5NeuralSharpener


def test_neural_sharpener_modes():
    for mode in ("ultra_sharp", "cinematic", "balanced"):
        sharpener = DLSS5NeuralSharpener(mode=mode)
        dummy = np.ones((64, 64, 3), dtype=np.uint8) * 128
        out = sharpener.enhance(dummy, intensity=1.0)
        assert out.shape == (64, 64, 3)
        assert out.dtype == np.uint8


def test_neural_sharpener_zero_intensity():
    sharpener = DLSS5NeuralSharpener(mode="ultra_sharp")
    dummy = np.random.randint(0, 255, (32, 32, 3), dtype=np.uint8)
    out = sharpener.enhance(dummy, intensity=0.0)
    assert np.array_equal(out, dummy)


def test_detect_active_browsers_returns_list():
    browsers = detect_active_browsers()
    assert isinstance(browsers, list)
