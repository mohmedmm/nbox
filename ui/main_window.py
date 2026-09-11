"""Flagship PyQt6 Main Window for NeuralUpscale."""

from __future__ import annotations

import os
import sys
from PyQt6.QtCore import QThread, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QDragEnterEvent, QDropEvent, QFont, QIcon
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.browser_hook import detect_active_browsers
from core.hardware import detect as detect_hardware
from core.models import REGISTRY
from core.player_bridge import launch_player
from core.upscaler import ProgressUpdate, UpscaleConfig, VideoUpscaler
from ui.browser_overlay import BrowserVideoOverlay
from ui.player_tab import PlayerSelectorWidget
from ui.queue_tab import QueueWidget
from ui.settings_dialog import SettingsDialog
from ui.styles import THEME_STYLESHEET
from utils.ffprobe import VideoInfo, probe
from utils.preview import ComparisonSliderWidget


class UpscaleWorker(QThread):
    """Background worker thread running the neural upscaler."""

    progress_updated = pyqtSignal(ProgressUpdate)
    model_download_progress = pyqtSignal(int)
    completed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, config: UpscaleConfig) -> None:
        super().__init__()
        self.config = config
        self.upscaler = VideoUpscaler(config)

    def run(self) -> None:
        try:
            out_file = self.upscaler.run(
                progress_cb=self._on_progress,
                model_download_cb=self._on_model_download,
            )
            self.completed.emit(out_file)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def _on_progress(self, update: ProgressUpdate) -> None:
        self.progress_updated.emit(update)

    def _on_model_download(self, percent: int) -> None:
        self.model_download_progress.emit(percent)

    def pause(self) -> None:
        self.upscaler.pause()

    def resume(self) -> None:
        self.upscaler.resume()

    def cancel(self) -> None:
        self.upscaler.cancel()


class MainWindow(QMainWindow):
    """Flagship desktop GUI for NeuralUpscale."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("nbox — AI Video Studio & Neural Enhancer")
        self.resize(1180, 840)
        self.setAcceptDrops(True)
        self.setStyleSheet(THEME_STYLESHEET)

        self._active_worker: UpscaleWorker | None = None
        self._input_video_path: str | None = None
        self._output_video_path: str | None = None
        self._video_info: VideoInfo | None = None

        self._settings = {
            "tile_size": 1024,
            "use_nvenc": True,
            "crf": 18,
            "preview_interval": 1,
            "model_id": "realesr-animevideov3",
        }

        self._init_ui()
        self._detect_and_display_hardware()

    def _init_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(18, 14, 18, 18)
        root_layout.setSpacing(12)

        # Header with GPU status badge
        root_layout.addLayout(self._create_header())

        # Main Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #1a2336; background: #080b11; border-radius: 8px; }
            QTabBar::tab { background: #0e131f; color: #64748b; padding: 8px 18px; margin-right: 4px; border-top-left-radius: 6px; border-top-right-radius: 6px; font-weight: 600; font-size: 13px; }
            QTabBar::tab:selected { background: #141b29; color: #00f0a0; border-bottom: 2px solid #00f0a0; }
            QTabBar::tab:hover:!selected { background: #111827; color: #94a3b8; }
        """)

        # Tab 1: Live Studio
        studio_tab = QWidget()
        studio_layout = QVBoxLayout(studio_tab)
        studio_layout.setContentsMargins(12, 12, 12, 12)
        studio_layout.setSpacing(12)

        studio_layout.addWidget(self._create_input_group())
        studio_layout.addWidget(self._create_preview_group(), stretch=1)
        studio_layout.addWidget(self._create_hud_metrics_group())
        studio_layout.addWidget(self._create_controls_group())

        self.tabs.addTab(studio_tab, "🎬 Real-Time Neural Studio")

        # Tab 2: Browser Video Live Upscaler
        self._browser_overlay = None
        self.tabs.addTab(self._create_browser_tab(), "🌐 Browser Live (nbox)")

        # Tab 3: Batch Queue
        self.queue_widget = QueueWidget()
        self.queue_widget.play_requested.connect(self._launch_in_player)
        self.tabs.addTab(self.queue_widget, "📋 Batch Queue")

        root_layout.addWidget(self.tabs, stretch=1)

    def _create_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setSpacing(12)

        title_lbl = QLabel("nbox")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: 800; color: #00f0a0; letter-spacing: -0.5px;")
        header.addWidget(title_lbl)

        sub_lbl = QLabel("Neural Video Enhancement & Super-Resolution Studio")
        sub_lbl.setStyleSheet("color: #64748b; font-size: 13px; margin-top: 4px;")
        header.addWidget(sub_lbl)

        header.addStretch()

        # Hardware Badge
        self.hw_badge = QLabel("⚡ Detecting GPU...")
        self.hw_badge.setStyleSheet(
            "background-color: #0b1d14; border: 1px solid #00d984; border-radius: 14px; "
            "color: #00f0a0; padding: 4px 14px; font-weight: 600; font-size: 12px;"
        )
        header.addWidget(self.hw_badge)

        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.clicked.connect(self._open_settings)
        header.addWidget(settings_btn)

        return header

    def _create_input_group(self) -> QGroupBox:
        grp = QGroupBox("1. Video Source & Resolution Target")
        layout = QVBoxLayout(grp)
        layout.setSpacing(8)

        file_row = QHBoxLayout()
        self.path_lbl = QLabel("No video selected. Drag & drop a video file here or click Browse.")
        self.path_lbl.setStyleSheet("color: #8b949e; font-style: italic;")
        file_row.addWidget(self.path_lbl, stretch=1)

        browse_btn = QPushButton("📂 Browse Video...")
        browse_btn.clicked.connect(self._browse_video)
        file_row.addWidget(browse_btn)

        layout.addLayout(file_row)

        # Meta & Scale target bar
        meta_row = QHBoxLayout()
        self.meta_lbl = QLabel("Input Info: N/A")
        self.meta_lbl.setStyleSheet("color: #58a6ff; font-weight: 500;")
        meta_row.addWidget(self.meta_lbl)

        meta_row.addStretch()

        meta_row.addWidget(QLabel("Target Output:"))
        self.res_combo = QComboBox()
        self.res_combo.addItem("4x Neural Scale (240p → 1704x960 / 2K)", "auto_4x")
        self.res_combo.addItem("2K Ultra HD (2560x1440)", (2560, 1440))
        self.res_combo.addItem("1080p Full HD (1920x1080)", (1920, 1080))
        self.res_combo.addItem("4K Extreme (3840x2160)", (3840, 2160))
        self.res_combo.addItem("2x Native Scale", "auto_2x")
        meta_row.addWidget(self.res_combo)

        layout.addLayout(meta_row)
        return grp

    def _create_preview_group(self) -> QGroupBox:
        grp = QGroupBox("2. Real-Time Neural Enhancement (Drag center slider to compare)")
        layout = QVBoxLayout(grp)
        layout.setContentsMargins(6, 14, 6, 6)

        self.preview_widget = ComparisonSliderWidget()
        layout.addWidget(self.preview_widget)
        return grp

    def _create_hud_metrics_group(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("background-color: #0e131f; border: 1px solid #1a2336; border-radius: 8px; padding: 8px;")
        grid = QGridLayout(frame)
        grid.setContentsMargins(12, 6, 12, 6)

        # Metrics: FPS, ETA, Frames, Progress
        self.fps_val = QLabel("0.0 FPS")
        self.fps_val.setObjectName("MetricValue")
        fps_title = QLabel("INFERENCE SPEED")
        fps_title.setObjectName("MetricTitle")
        grid.addWidget(fps_title, 0, 0)
        grid.addWidget(self.fps_val, 1, 0)

        self.eta_val = QLabel("--:--:--")
        self.eta_val.setObjectName("MetricValue")
        eta_title = QLabel("ESTIMATED TIME")
        eta_title.setObjectName("MetricTitle")
        grid.addWidget(eta_title, 0, 1)
        grid.addWidget(self.eta_val, 1, 1)

        self.frames_val = QLabel("0 / 0")
        self.frames_val.setObjectName("MetricValue")
        frames_title = QLabel("FRAMES PROCESSED")
        frames_title.setObjectName("MetricTitle")
        grid.addWidget(frames_title, 0, 2)
        grid.addWidget(self.frames_val, 1, 2)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        grid.addWidget(self.progress_bar, 0, 3, 2, 1)
        grid.setColumnStretch(3, 1)

        return frame

    def _create_controls_group(self) -> QGroupBox:
        grp = QGroupBox("3. AI Model & Media Player Pipeline")
        layout = QVBoxLayout(grp)
        layout.setSpacing(10)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Neural Model:"))
        self.model_combo = QComboBox()
        for mid, spec in REGISTRY.items():
            self.model_combo.addItem(f"⚡ {spec.label}", mid)
        row1.addWidget(self.model_combo, stretch=1)

        # Player Selector
        self.player_selector = PlayerSelectorWidget()
        row1.addWidget(self.player_selector, stretch=1)
        layout.addLayout(row1)

        # Action Buttons
        row2 = QHBoxLayout()
        self.start_btn = QPushButton("🚀 Start Neural Upscale")
        self.start_btn.setObjectName("PrimaryBtn")
        self.start_btn.clicked.connect(self._toggle_start_upscale)
        row2.addWidget(self.start_btn, stretch=2)

        self.pause_btn = QPushButton("⏸️ Pause")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self._toggle_pause)
        row2.addWidget(self.pause_btn)

        self.cancel_btn = QPushButton("⏹️ Stop")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel_upscale)
        row2.addWidget(self.cancel_btn)

        self.play_btn = QPushButton("🎬 Open in Player")
        self.play_btn.setEnabled(False)
        self.play_btn.clicked.connect(lambda: self._launch_in_player(self._output_video_path))
        row2.addWidget(self.play_btn, stretch=1)

        layout.addLayout(row2)
        return grp

    def _detect_and_display_hardware(self) -> None:
        hw = detect_hardware()
        if hw.backend == "cuda" and hw.primary_gpu:
            self.hw_badge.setText(f"⚡ {hw.primary_gpu.name} ({hw.primary_gpu.vram_mb} MB) | CUDA + NVENC Active")
            self.hw_badge.setStyleSheet(
                "background-color: #0b1d14; border: 1px solid #00d984; border-radius: 14px; "
                "color: #00f0a0; padding: 4px 14px; font-weight: 600; font-size: 12px;"
            )
        else:
            self.hw_badge.setText(f"🖥️ Backend: {hw.backend.upper()}")

    def _browse_video(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video to Upscale",
            "",
            "Video Files (*.mp4 *.mkv *.avi *.mov *.webm *.flv);;All Files (*.*)",
        )
        if file_path:
            self.load_video(file_path)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if os.path.exists(file_path):
                self.load_video(file_path)

    def load_video(self, path: str) -> None:
        try:
            self._input_video_path = path
            self.path_lbl.setText(path)
            self.path_lbl.setStyleSheet("color: #f0f6fc; font-weight: 600;")

            self._video_info = probe(path)
            meta = f"Input: {self._video_info.width}x{self._video_info.height} @ {self._video_info.fps:.2f}fps ({self._video_info.codec}) | {self._video_info.duration:.1f}s"
            self.meta_lbl.setText(meta)

            # Pre-populate default output path
            dir_name = os.path.dirname(path)
            base, ext = os.path.splitext(os.path.basename(path))
            self._output_video_path = os.path.join(dir_name, f"{base}_nbox_2K{ext}")

            # Update preview badges
            self.preview_widget.set_labels(
                orig_label=f"ORIGINAL ({self._video_info.width}x{self._video_info.height})",
                upscaled_label="NEURAL UPSCALE (2K / 4K)",
            )
            self.start_btn.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Video Load Error", f"Failed to read video file:\n{e}")

    def _toggle_start_upscale(self) -> None:
        if not self._input_video_path:
            QMessageBox.warning(self, "No Video", "Please select a video file first.")
            return

        if self._active_worker and self._active_worker.isRunning():
            return

        # Target resolution
        data = self.res_combo.currentData()
        target_res = data if isinstance(data, tuple) else None

        config = UpscaleConfig(
            input_path=self._input_video_path,
            output_path=self._output_video_path,
            model_id=self.model_combo.currentData(),
            target_resolution=target_res,
            tile_size=self._settings.get("tile_size", 1024),
            use_nvenc=self._settings.get("use_nvenc", True),
            crf=self._settings.get("crf", 18),
            preview_interval=self._settings.get("preview_interval", 1),
        )

        self._active_worker = UpscaleWorker(config)
        self._active_worker.progress_updated.connect(self._on_worker_progress)
        self._active_worker.model_download_progress.connect(self._on_model_download_progress)
        self._active_worker.completed.connect(self._on_worker_completed)
        self._active_worker.error_occurred.connect(self._on_worker_error)

        self._active_worker.start()

        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        self.play_btn.setEnabled(False)

    def _toggle_pause(self) -> None:
        if not self._active_worker:
            return
        if self.pause_btn.text() == "⏸️ Pause":
            self._active_worker.pause()
            self.pause_btn.setText("▶️ Resume")
        else:
            self._active_worker.resume()
            self.pause_btn.setText("⏸️ Pause")

    def _cancel_upscale(self) -> None:
        if self._active_worker and self._active_worker.isRunning():
            self._active_worker.cancel()
            self._reset_controls()

    def _on_worker_progress(self, u: ProgressUpdate) -> None:
        self.progress_bar.setValue(int(u.percent))
        self.fps_val.setText(f"{u.fps:.1f} FPS")
        self.frames_val.setText(f"{u.frame_idx} / {u.total_frames}")

        mins, secs = divmod(int(u.eta_seconds), 60)
        hrs, mins = divmod(mins, 60)
        self.eta_val.setText(f"{hrs:02d}:{mins:02d}:{secs:02d}")

        if u.original_frame is not None and u.upscaled_frame is not None:
            self.preview_widget.update_frames(u.original_frame, u.upscaled_frame)

    def _on_model_download_progress(self, percent: int) -> None:
        self.progress_bar.setValue(percent)
        self.eta_val.setText(f"Downloading Model... {percent}%")

    def _on_worker_completed(self, output_path: str) -> None:
        self._reset_controls()
        self.progress_bar.setValue(100)
        self.play_btn.setEnabled(True)

        reply = QMessageBox.information(
            self,
            "Upscale Complete! 🎉",
            f"Video successfully enhanced to 2K/4K!\n\nSaved to:\n{output_path}\n\nWould you like to play it now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._launch_in_player(output_path)

    def _on_worker_error(self, err_msg: str) -> None:
        self._reset_controls()
        QMessageBox.critical(self, "Upscale Error", f"An error occurred during upscaling:\n{err_msg}")

    def _reset_controls(self) -> None:
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("⏸️ Pause")
        self.cancel_btn.setEnabled(False)

    def _launch_in_player(self, video_path: str | None) -> None:
        if not video_path or not os.path.exists(video_path):
            QMessageBox.warning(self, "File Not Found", f"Video file not found: {video_path}")
            return
        self.player_selector.launch_with_video(video_path)

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self, self._settings)
        if dlg.exec():
            self._settings = dlg.get_settings()

    def _create_browser_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        # Header card
        info_grp = QGroupBox("🌐 In-Browser nbox Video Neural Enhancer")
        info_layout = QVBoxLayout(info_grp)
        info_layout.setSpacing(10)

        desc = QLabel(
            "<b>Runs directly inside your web browser</b> (Chrome, Edge, Brave, etc.) without opening any separate window!<br>"
            "Auto-detects any <code>&lt;video&gt;</code> element on <b>YouTube, Twitch, Netflix, or any video site</b>.<br>"
            "Injects a sleek <b>Green Square Watermark [ ■ nbox: ON ]</b> in the corner of the video. Click it to toggle enhancement on/off anytime!"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #94a3b8; font-size: 13px; line-height: 1.5;")
        info_layout.addWidget(desc)

        self.browser_status_lbl = QLabel("Detecting running web browsers...")
        self.browser_status_lbl.setStyleSheet("color: #00f0a0; font-weight: bold;")
        info_layout.addWidget(self.browser_status_lbl)

        layout.addWidget(info_grp)

        # Primary Option: Chrome / Edge Direct In-Browser Extension
        ext_grp = QGroupBox("Method 1: Direct In-Browser Extension (Recommended — Zero Windows, 60+ FPS)")
        ext_layout = QVBoxLayout(ext_grp)
        ext_layout.setSpacing(12)

        ext_steps = QLabel(
            "<b>To activate inside Google Chrome or Microsoft Edge:</b><br>"
            "1. Open your browser and navigate to: <code style='color: #38bdf8;'>chrome://extensions</code> (or <code style='color: #38bdf8;'>edge://extensions</code>).<br>"
            "2. Enable <b>Developer mode</b> (toggle switch in the top-right corner).<br>"
            "3. Click <b>Load unpacked</b> and select the <b>browser_extension</b> folder.<br>"
            "4. Done! Every video on YouTube or any site will now automatically have nbox neural detail and the clickable green square!"
        )
        ext_steps.setWordWrap(True)
        ext_steps.setStyleSheet("background: #0e131f; border: 1px solid #1a2336; border-radius: 8px; padding: 12px; color: #94a3b8; line-height: 1.4;")
        ext_layout.addWidget(ext_steps)

        btn_row1 = QHBoxLayout()
        open_ext_btn = QPushButton("📂 Open 'browser_extension' Folder")
        open_ext_btn.setObjectName("PrimaryBtn")
        open_ext_btn.setMinimumHeight(38)
        open_ext_btn.clicked.connect(self._open_extension_dir)
        btn_row1.addWidget(open_ext_btn)

        copy_userscript_btn = QPushButton("📋 Copy Tampermonkey Userscript")
        copy_userscript_btn.setMinimumHeight(38)
        copy_userscript_btn.clicked.connect(self._copy_userscript)
        btn_row1.addWidget(copy_userscript_btn)
        ext_layout.addLayout(btn_row1)

        layout.addWidget(ext_grp)

        # Secondary Option: Desktop Floating Overlay
        overlay_grp = QGroupBox("Method 2: External Floating Desktop Overlay (Optional)")
        overlay_layout = QVBoxLayout(overlay_grp)
        overlay_layout.setSpacing(10)

        overlay_desc = QLabel("Places an external floating borderless frame over any desktop window or video player.")
        overlay_desc.setStyleSheet("color: #8b949e;")
        overlay_layout.addWidget(overlay_desc)

        self.overlay_btn = QPushButton("🚀 Launch Floating Desktop Overlay")
        self.overlay_btn.setMinimumHeight(36)
        self.overlay_btn.clicked.connect(self._toggle_browser_overlay)
        overlay_layout.addWidget(self.overlay_btn)

        layout.addWidget(overlay_grp)
        layout.addStretch()

        self._refresh_active_browsers()
        return tab

    def _open_extension_dir(self) -> None:
        ext_dir = os.path.join(os.path.dirname(__file__), "..", "browser_extension")
        abs_path = os.path.abspath(ext_dir)
        if os.path.exists(abs_path):
            os.startfile(abs_path)

    def _copy_userscript(self) -> None:
        script_path = os.path.join(os.path.dirname(__file__), "..", "nbox_browser.user.js")
        if os.path.exists(script_path):
            with open(script_path, "r", encoding="utf-8") as f:
                content = f.read()
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(content)
            QMessageBox.information(
                self,
                "Userscript Copied! 📋",
                "The nbox Tampermonkey userscript has been copied to your clipboard!\n\nYou can paste it directly into Tampermonkey or Violentmonkey.",
            )

    def _refresh_active_browsers(self) -> None:
        browsers = detect_active_browsers()
        if browsers:
            names = ", ".join(f"<b>{b.name}</b> (PID {b.pid})" for b in browsers)
            self.browser_status_lbl.setText(f"Active Browser Detected: {names}")
        else:
            self.browser_status_lbl.setText("No supported browsers detected. Open Chrome, Edge, or Firefox.")

    def _toggle_browser_overlay(self) -> None:
        if self._browser_overlay and self._browser_overlay.isVisible():
            self._browser_overlay.close()
            self._browser_overlay = None
            self.overlay_btn.setText("🚀 Launch Floating Desktop Overlay")
        else:
            self._browser_overlay = BrowserVideoOverlay()
            self._browser_overlay.show()
            self.overlay_btn.setText("⏹️ Close Floating Desktop Overlay")


