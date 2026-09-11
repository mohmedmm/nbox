"""Tests for standalone neural upscaling models."""

import pytest
import torch
from core.models import RRDBNet, SRVGGNetCompact


def test_compact_forward_shape():
    """Verify SRVGGNetCompact (AnimeVideo-v3) upscales 4x accurately."""
    net = SRVGGNetCompact(num_in_ch=3, num_out_ch=3, num_feat=32, num_conv=4, upscale=4)
    x = torch.randn(1, 3, 32, 32)
    with torch.no_grad():
        y = net(x)
    assert y.shape == (1, 3, 128, 128)


def test_rrdbnet_forward_shape():
    """Verify RRDBNet upscales 4x accurately."""
    net = RRDBNet(in_nc=3, out_nc=3, nf=32, nb=2, gc=16, scale=4)
    x = torch.randn(1, 3, 16, 16)
    with torch.no_grad():
        y = net(x)
    assert y.shape == (1, 3, 64, 64)


def test_rrdbnet_scale_2():
    """Verify RRDBNet with 2x scale."""
    net = RRDBNet(in_nc=3, out_nc=3, nf=32, nb=1, gc=16, scale=2)
    x = torch.randn(1, 3, 16, 16)
    with torch.no_grad():
        y = net(x)
    assert y.shape == (1, 3, 32, 32)
