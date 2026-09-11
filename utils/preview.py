"""Interactive Before / After split-view comparison widget."""

from __future__ import annotations

import cv2
import numpy as np
from PyQt6.QtCore import QPoint, QRect, Qt
from PyQt6.QtGui import QColor, QFont, QImage, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QWidget


class ComparisonSliderWidget(QWidget):
    """Real-time split slider widget comparing original vs upscaled video frames."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(480, 270)
        self.setMouseTracking(True)

        self._split_ratio: float = 0.5  # 0.0 to 1.0
        self._dragging: bool = False

        self._orig_pixmap: QPixmap | None = None
        self._upscaled_pixmap: QPixmap | None = None

        self._orig_label: str = "ORIGINAL (Input)"
        self._upscaled_label: str = "DLSS5 / NEURAL (2K)"

    def set_labels(self, orig_label: str, upscaled_label: str) -> None:
        self._orig_label = orig_label
        self._upscaled_label = upscaled_label
        self.update()

    def update_frames(self, orig_bgr: np.ndarray, upscaled_bgr: np.ndarray) -> None:
        """Receive BGR numpy arrays, convert to QPixmap and refresh view."""
        self._orig_pixmap = self._numpy_to_pixmap(orig_bgr)
        self._upscaled_pixmap = self._numpy_to_pixmap(upscaled_bgr)
        self.update()

    @staticmethod
    def _numpy_to_pixmap(bgr: np.ndarray) -> QPixmap:
        h, w, c = bgr.shape
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        bytes_per_line = c * w
        q_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(q_img)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._update_slider_pos(event.pos().x())

    def mouseMoveEvent(self, event) -> None:
        if self._dragging:
            self._update_slider_pos(event.pos().x())
        else:
            # Change cursor if hovering near slider line
            slider_x = int(self.width() * self._split_ratio)
            if abs(event.pos().x() - slider_x) < 8:
                self.setCursor(Qt.CursorShape.SplitHCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False

    def _update_slider_pos(self, x: int) -> None:
        self._split_ratio = max(0.02, min(0.98, x / max(self.width(), 1)))
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w = self.width()
        h = self.height()

        # Background
        painter.fillRect(0, 0, w, h, QColor(18, 20, 24))

        if not self._orig_pixmap and not self._upscaled_pixmap:
            painter.setPen(QColor(110, 118, 129))
            font = QFont("Segoe UI", 11)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(
                QRect(0, 0, w, h),
                Qt.AlignmentFlag.AlignCenter,
                "Ready — Drop video or click Upscale to watch real-time neural enhancement",
            )
            return

        split_x = int(w * self._split_ratio)

        # Draw Upscaled side (Full background)
        if self._upscaled_pixmap:
            scaled_up = self._upscaled_pixmap.scaled(
                w, h,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.drawPixmap(0, 0, scaled_up)

        # Draw Original side (Clipped to left of slider)
        if self._orig_pixmap:
            painter.save()
            painter.setClipRect(0, 0, split_x, h)
            scaled_orig = self._orig_pixmap.scaled(
                w, h,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.drawPixmap(0, 0, scaled_orig)
            painter.restore()

        # Draw divider line
        pen = QPen(QColor(0, 220, 130), 2)
        painter.setPen(pen)
        painter.drawLine(split_x, 0, split_x, h)

        # Draw handle circle
        painter.setBrush(QColor(0, 220, 130))
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawEllipse(QPoint(split_x, h // 2), 12, 12)

        # Draw badges
        self._draw_badge(painter, self._orig_label, 14, 14, is_accent=False)
        self._draw_badge(painter, self._upscaled_label, w - 180, 14, is_accent=True)

    @staticmethod
    def _draw_badge(painter: QPainter, text: str, x: int, y: int, is_accent: bool) -> None:
        painter.save()
        bg_color = QColor(0, 200, 115, 200) if is_accent else QColor(30, 35, 45, 190)
        fg_color = QColor(0, 0, 0) if is_accent else QColor(240, 246, 252)

        font = QFont("Segoe UI", 9)
        font.setBold(True)
        painter.setFont(font)

        badge_rect = QRect(x, y, 160, 26)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(badge_rect, 6, 6)

        painter.setPen(fg_color)
        painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, text)
        painter.restore()
