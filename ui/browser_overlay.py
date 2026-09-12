"""Interactive floating browser overlay with clickable DLSS 5 green square watermark."""

from __future__ import annotations

import cv2
import numpy as np
import torch
from PyQt6.QtCore import QPoint, QRect, QSize, Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QCursor,
    QFont,
    QImage,
    QMouseEvent,
    QPainter,
    QPen,
    QPixmap,
)
from PyQt6.QtWidgets import QMenu, QWidget

from core.browser_hook import grab_screen_region
from core.hardware import detect as detect_hardware
from core.models import NeuralUpsampler
from core.neural_sharpener import DLSS5NeuralSharpener


class BrowserCaptureThread(QThread):
    """Worker capturing screen region under overlay and generating DLSS 5 frames."""

    frame_ready = pyqtSignal(np.ndarray)

    def __init__(self, rect_getter, enabled_getter, sharpness: float = 1.2) -> None:
        super().__init__()
        self.rect_getter = rect_getter
        self.enabled_getter = enabled_getter
        self.sharpness = sharpness
        self._running = True

        hw = detect_hardware()
        device = torch.device("cuda" if hw.backend == "cuda" and torch.cuda.is_available() else "cpu")

        # Compact video model for ultra-low latency real-time streaming
        self.upsampler = NeuralUpsampler(
            model_id="realesr-animevideov3",
            device=device,
            tile=512,
            half=device.type == "cuda",
        )
        self.sharpener = DLSS5NeuralSharpener(mode="ultra_sharp", device=device)

    def stop(self) -> None:
        self._running = False
        self.wait(500)

    def run(self) -> None:
        while self._running:
            if not self.enabled_getter():
                self.msleep(80)
                continue

            try:
                rect: QRect = self.rect_getter()
                if rect.width() < 64 or rect.height() < 64:
                    self.msleep(100)
                    continue

                # Grab screen under overlay
                raw_bgr = grab_screen_region(rect.x(), rect.y(), rect.width(), rect.height())
                if raw_bgr is None:
                    self.msleep(50)
                    continue

                # Downsample preview if large, run DLSS 5 generative neural synthesis
                in_h, in_w = raw_bgr.shape[:2]
                target_proc_w = min(in_w, 640)
                target_proc_h = min(in_h, 360)

                small_in = cv2.resize(raw_bgr, (target_proc_w, target_proc_h), interpolation=cv2.INTER_AREA)

                # Neural upscaling pass
                enhanced = self.upsampler.enhance(small_in)

                # DLSS 5 generative detail injection
                enhanced = self.sharpener.enhance(enhanced, intensity=self.sharpness)

                # Scale back to overlay dimensions
                if enhanced.shape[1] != in_w or enhanced.shape[0] != in_h:
                    enhanced = cv2.resize(enhanced, (in_w, in_h), interpolation=cv2.INTER_LANCZOS4)

                self.frame_ready.emit(enhanced)
            except Exception:
                pass
            self.msleep(16)  # ~60 FPS loop


class BrowserVideoOverlay(QWidget):
    """Floating transparent overlay window with clickable DLSS 5 green square badge."""

    def __init__(self, initial_rect: QRect | None = None) -> None:
        super().__init__()
        # Frameless, stays on top, tool window so it doesn't clutter taskbar
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

        rect = initial_rect or QRect(150, 150, 854, 480)
        self.setGeometry(rect)

        # Exclude overlay itself from screen capture to prevent recursive feedback loops
        try:
            import sys
            if sys.platform == "win32":
                import ctypes
                from ctypes import wintypes
                u32 = ctypes.windll.user32
                u32.SetWindowDisplayAffinity.argtypes = [wintypes.HWND, wintypes.DWORD]
                u32.SetWindowDisplayAffinity.restype = wintypes.BOOL
                hwnd_val = int(self.winId())
                if not u32.SetWindowDisplayAffinity(wintypes.HWND(hwnd_val), 0x00000011):
                    u32.SetWindowDisplayAffinity(wintypes.HWND(hwnd_val), 0x00000001)
        except Exception:
            pass


        # State
        self.dlss_enabled: bool = True  # Green when True, Red/Gray when False
        self._current_pixmap: QPixmap | None = None

        # Dragging & Resizing handles
        self._dragging_window = False
        self._resizing_window = False
        self._drag_pos = QPoint()

        # Watermark badge geometry (Top-Right)
        self._badge_rect = QRect()

        # Start capture thread
        self.worker = BrowserCaptureThread(
            rect_getter=self.geometry,
            enabled_getter=lambda: self.dlss_enabled,
        )
        self.worker.frame_ready.connect(self._on_frame_ready)
        self.worker.start()

    def closeEvent(self, event) -> None:
        self.worker.stop()
        super().closeEvent(event)

    def _on_frame_ready(self, bgr_frame: np.ndarray) -> None:
        if not self.dlss_enabled:
            return
        h, w, c = bgr_frame.shape
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        q_img = QImage(rgb.data, w, h, c * w, QImage.Format.Format_RGB888)
        self._current_pixmap = QPixmap.fromImage(q_img)
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        # Check if user clicked on the DLSS 5 Watermark Square
        if self._badge_rect.contains(event.pos()):
            # Toggle DLSS 5 ON / OFF
            self.dlss_enabled = not self.dlss_enabled
            if not self.dlss_enabled:
                self._current_pixmap = None  # Clear overlay so original browser video shows through
            self.update()
            return

        # Check for bottom-right corner resize handle (30x30)
        br_rect = QRect(self.width() - 25, self.height() - 25, 25, 25)
        if br_rect.contains(event.pos()):
            self._resizing_window = True
            return

        # Otherwise move window
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging_window = True
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._resizing_window:
            new_w = max(320, event.pos().x())
            new_h = max(180, event.pos().y())
            self.resize(new_w, new_h)
            return

        if self._dragging_window:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            return

        # Cursor icon update
        br_rect = QRect(self.width() - 25, self.height() - 25, 25, 25)
        if self._badge_rect.contains(event.pos()):
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        elif br_rect.contains(event.pos()):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.SizeAllCursor)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._dragging_window = False
        self._resizing_window = False

        # Context menu action to hide/show watermark
        self.show_watermark = True

    def contextMenuEvent(self, event) -> None:
        menu = QMenu(self)
        toggle_action = menu.addAction("Toggle nbox Enhancement (On/Off)")
        toggle_action.triggered.connect(lambda: self._toggle_dlss())
        wm_action = menu.addAction("Hide/Show Watermark Badge")
        wm_action.triggered.connect(lambda: self._toggle_watermark())
        menu.addSeparator()
        close_action = menu.addAction("Close Overlay [✕]")
        close_action.triggered.connect(self.close)
        menu.exec(event.globalPos())

    def _toggle_watermark(self) -> None:
        self.show_watermark = not self.show_watermark
        self.update()

    def _toggle_dlss(self) -> None:
        self.dlss_enabled = not self.dlss_enabled
        if not self.dlss_enabled:
            self._current_pixmap = None
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w = self.width()
        h = self.height()

        # 1. Render enhanced frame when active
        if self.dlss_enabled and self._current_pixmap:
            painter.drawPixmap(0, 0, w, h, self._current_pixmap)
        else:
            # Transparent see-through window when OFF so original browser video is visible
            painter.fillRect(0, 0, w, h, QColor(0, 0, 0, 10))

        # 2. Outer glowing bounding border
        border_color = QColor(0, 229, 153, 200) if self.dlss_enabled else QColor(248, 81, 73, 160)
        painter.setPen(QPen(border_color, 2, Qt.PenStyle.DashLine if not self.dlss_enabled else Qt.PenStyle.SolidLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(1, 1, w - 2, h - 2)

        # 3. WATERMARK SQUARE BADGE (Top-Right)
        if self.show_watermark:
            badge_w, badge_h = 148, 32
            badge_x = w - badge_w - 14
            badge_y = 14
            self._badge_rect = QRect(badge_x, badge_y, badge_w, badge_h)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(15, 20, 28, 220))
            painter.drawRoundedRect(self._badge_rect, 7, 7)

            painter.setPen(QPen(border_color, 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(self._badge_rect, 7, 7)

            square_size = 14
            square_rect = QRect(badge_x + 10, badge_y + (badge_h - square_size) // 2, square_size, square_size)

            if self.dlss_enabled:
                painter.setPen(QPen(QColor(255, 255, 255), 1))
                painter.setBrush(QColor(0, 255, 150))
                painter.drawRoundedRect(square_rect, 2.5, 2.5)

                painter.setPen(QColor(0, 255, 150))
                font = QFont("Segoe UI", 10, QFont.Weight.Bold)
                painter.setFont(font)
                painter.drawText(
                    QRect(badge_x + 30, badge_y, badge_w - 34, badge_h),
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                    "nbox: ON",
                )
            else:
                painter.setPen(QPen(QColor(140, 140, 140), 1))
                painter.setBrush(QColor(248, 81, 73))
                painter.drawRoundedRect(square_rect, 2.5, 2.5)

                painter.setPen(QColor(248, 81, 73))
                font = QFont("Segoe UI", 10, QFont.Weight.Bold)
                painter.setFont(font)
                painter.drawText(
                    QRect(badge_x + 30, badge_y, badge_w - 34, badge_h),
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                    "nbox: OFF",
                )
        else:
            self._badge_rect = QRect()

        # 4. Corner Resize Handle (Bottom-Right)
        painter.setPen(QPen(border_color, 2))
        painter.drawLine(w - 18, h - 6, w - 6, h - 18)
        painter.drawLine(w - 12, h - 6, w - 6, h - 12)
