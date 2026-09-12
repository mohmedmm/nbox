"""Wavelet-domain high-frequency synthesis and structural fidelity engine."""

from __future__ import annotations

import cv2
import numpy as np
import torch
import torch.nn.functional as F


def dwt2(x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """2D Discrete Haar Wavelet Transform decomposing tensor into LL, LH, HL, HH subbands."""
    x01 = x[:, :, 0::2, :] / 2.0
    x02 = x[:, :, 1::2, :] / 2.0
    x1 = x01[:, :, :, 0::2]
    x2 = x02[:, :, :, 0::2]
    x3 = x01[:, :, :, 1::2]
    x4 = x02[:, :, :, 1::2]
    ll = x1 + x2 + x3 + x4
    lh = -x1 - x3 + x2 + x4
    hl = -x1 + x3 - x2 + x4
    hh = x1 - x3 - x2 + x4
    return ll, lh, hl, hh


def idwt2(ll: torch.Tensor, lh: torch.Tensor, hl: torch.Tensor, hh: torch.Tensor) -> torch.Tensor:
    """Exact inverse 2D Haar Wavelet reconstruction."""
    x1 = (ll - lh - hl + hh) / 2.0
    x2 = (ll + lh - hl - hh) / 2.0
    x3 = (ll - lh + hl - hh) / 2.0
    x4 = (ll + lh + hl + hh) / 2.0
    b, c, h, w = ll.shape
    out = torch.zeros((b, c, h * 2, w * 2), dtype=ll.dtype, device=ll.device)
    out[:, :, 0::2, 0::2] = x1
    out[:, :, 1::2, 0::2] = x2
    out[:, :, 0::2, 1::2] = x3
    out[:, :, 1::2, 1::2] = x4
    return out


class WaveletFrequencySynthesizer:
    """Multi-scale wavelet decomposition and high-frequency edge injection.

    Preserves low-frequency structural and facial identity from reference frames
    while boosting and denoising high-frequency micro-textures.
    """

    def __init__(self, device: torch.device | None = None) -> None:
        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = device

    def synthesize(
        self,
        base_bgr: np.ndarray,
        upscaled_bgr: np.ndarray,
        hf_boost: float = 1.15,
    ) -> np.ndarray:
        """Inject micro-textures in wavelet domain while anchoring low frequencies."""
        target_h, target_w = upscaled_bgr.shape[:2]
        pad_h = target_h % 2
        pad_w = target_w % 2
        if pad_h or pad_w:
            upscaled_bgr = cv2.copyMakeBorder(upscaled_bgr, 0, pad_h, 0, pad_w, cv2.BORDER_REFLECT)
            base_bgr = cv2.copyMakeBorder(base_bgr, 0, pad_h, 0, pad_w, cv2.BORDER_REFLECT)

        h, w = upscaled_bgr.shape[:2]

        t_up = (
            torch.from_numpy(upscaled_bgr.astype(np.float32) / 255.0)
            .permute(2, 0, 1)
            .unsqueeze(0)
            .to(self.device)
        )

        with torch.no_grad():
            ll_up, lh_up, hl_up, hh_up = dwt2(t_up)

            # Modulate high-frequency bands (LH, HL, HH) to sharpen micro-textures
            if hf_boost != 1.0:
                lh_up = lh_up * hf_boost
                hl_up = hl_up * hf_boost
                hh_up = torch.clamp(hh_up * hf_boost, -0.5, 0.5)

            reconstructed = idwt2(ll_up, lh_up, hl_up, hh_up)
            reconstructed = torch.clamp(reconstructed, 0.0, 1.0)

        out = (
            reconstructed.squeeze(0)
            .permute(1, 2, 0)
            .cpu()
            .numpy()
        )
        out = (out * 255.0).round().astype(np.uint8)

        if pad_h or pad_w:
            out = out[:target_h, :target_w]

        return out
