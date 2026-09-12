"""Temporal motion estimation and feature warping stabilization engine."""

from __future__ import annotations

import cv2
import numpy as np


class TemporalWarpEngine:
    """Motion-vector guided temporal stabilizer eliminating video flickering artifacts."""

    def __init__(
        self,
        history_blend: float = 0.75,
        disocclusion_threshold: float = 28.0,
        flow_scale: float = 0.5,
    ) -> None:
        self.history_blend = history_blend
        self.disocclusion_threshold = disocclusion_threshold
        self.flow_scale = flow_scale

        self._opt_flow = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_ULTRAFAST)
        self._prev_gray: np.ndarray | None = None
        self._prev_enhanced: np.ndarray | None = None

    def reset(self) -> None:
        """Clear temporal history on scene cuts or manual restarts."""
        self._prev_gray = None
        self._prev_enhanced = None

    def process_frame(self, current_raw_bgr: np.ndarray, current_enhanced_bgr: np.ndarray) -> np.ndarray:
        """Stabilize current enhanced frame using backward motion-warped temporal history."""
        curr_gray = cv2.cvtColor(current_raw_bgr, cv2.COLOR_BGR2GRAY)

        if self._prev_gray is None or self._prev_enhanced is None:
            self._prev_gray = curr_gray
            self._prev_enhanced = current_enhanced_bgr
            return current_enhanced_bgr

        # Compute backward optical flow at reduced resolution for real-time speed
        h_low, w_low = curr_gray.shape[:2]
        proc_w = max(int(w_low * self.flow_scale), 64)
        proc_h = max(int(h_low * self.flow_scale), 64)

        small_curr = cv2.resize(curr_gray, (proc_w, proc_h), interpolation=cv2.INTER_AREA)
        small_prev = cv2.resize(self._prev_gray, (proc_w, proc_h), interpolation=cv2.INTER_AREA)

        # Backward flow: small_curr -> small_prev
        flow_small = self._opt_flow.calc(small_curr, small_prev, None)

        target_h, target_w = current_enhanced_bgr.shape[:2]
        scale_x = target_w / proc_w
        scale_y = target_h / proc_h

        flow_x = cv2.resize(flow_small[:, :, 0] * scale_x, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
        flow_y = cv2.resize(flow_small[:, :, 1] * scale_y, (target_w, target_h), interpolation=cv2.INTER_LINEAR)

        # Backward warp previous enhanced frame
        grid_x, grid_y = np.meshgrid(np.arange(target_w), np.arange(target_h))
        map_x = (grid_x + flow_x).astype(np.float32)
        map_y = (grid_y + flow_y).astype(np.float32)

        warped_prev = cv2.remap(
            self._prev_enhanced,
            map_x,
            map_y,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT,
        )

        # Compute disocclusion / scene cut detection mask
        curr_upscaled_gray = cv2.cvtColor(current_enhanced_bgr, cv2.COLOR_BGR2GRAY)
        warped_prev_gray = cv2.cvtColor(warped_prev, cv2.COLOR_BGR2GRAY)
        diff = np.abs(curr_upscaled_gray.astype(np.float32) - warped_prev_gray.astype(np.float32))

        # Scene cut detection: if average frame difference is massive, reset history
        mean_diff = float(np.mean(diff))
        if mean_diff > (self.disocclusion_threshold * 2.5):
            self.reset()
            self._prev_gray = curr_gray
            self._prev_enhanced = current_enhanced_bgr
            return current_enhanced_bgr

        # Weight mask: 1.0 where flow matches well, decays to 0.0 at disocclusions
        weight_mask = np.clip(1.0 - (diff / max(self.disocclusion_threshold, 1.0)), 0.0, 1.0)
        weight_mask = cv2.GaussianBlur(weight_mask, (5, 5), 0)[:, :, np.newaxis]

        # Blend stabilized history with current fresh upscale
        effective_blend = self.history_blend * weight_mask
        stabilized = (warped_prev.astype(np.float32) * effective_blend +
                      current_enhanced_bgr.astype(np.float32) * (1.0 - effective_blend))
        stabilized = np.clip(stabilized, 0, 255).astype(np.uint8)

        self._prev_gray = curr_gray
        self._prev_enhanced = stabilized
        return stabilized
