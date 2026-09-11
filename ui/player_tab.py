"""Player configuration and launcher selector widget."""

from __future__ import annotations

import os
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.player_bridge import (
    DetectedPlayer,
    SUPPORTED_PLAYERS,
    detect_installed_players,
    launch_player,
)


class PlayerSelectorWidget(QWidget):
    """Widget allowing user to pick between KMPlayer, MPC-HC, VLC, PotPlayer, or custom exe."""

    player_changed = pyqtSignal(str)  # Emits executable path

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._detected_players: list[DetectedPlayer] = []
        self._custom_player_path: str | None = None
        self._init_ui()
        self.refresh_players()

    def _init_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        label = QLabel("Target Media Player:")
        label.setStyleSheet("font-weight: bold; color: #e6edf3;")
        layout.addWidget(label)

        self.combo = QComboBox()
        self.combo.setMinimumWidth(220)
        self.combo.currentIndexChanged.connect(self._on_combo_index_changed)
        layout.addWidget(self.combo)

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._on_browse_custom)
        layout.addWidget(self.browse_btn)

        self.refresh_btn = QPushButton("Detect")
        self.refresh_btn.setToolTip("Scan system for installed media players")
        self.refresh_btn.clicked.connect(self.refresh_players)
        layout.addWidget(self.refresh_btn)

    def refresh_players(self) -> None:
        self.combo.blockSignals(True)
        self.combo.clear()

        self._detected_players = detect_installed_players()

        if self._detected_players:
            for p in self._detected_players:
                self.combo.addItem(f"🎬 {p.spec.name}", p.exe_path)
        else:
            self.combo.addItem("⚠️ No default player found", "")

        # Always add Custom Player option
        if self._custom_player_path:
            self.combo.addItem(f"📁 Custom: {os.path.basename(self._custom_player_path)}", self._custom_player_path)
        else:
            self.combo.addItem("➕ Add Custom Player...", "__custom__")

        self.combo.blockSignals(False)
        self._on_combo_index_changed(self.combo.currentIndex())

    def _on_browse_custom(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Media Player Executable",
            "",
            "Executables (*.exe);;All Files (*.*)",
        )
        if file_path:
            self._custom_player_path = file_path
            self.refresh_players()
            # Select the custom item
            idx = self.combo.findData(file_path)
            if idx >= 0:
                self.combo.setCurrentIndex(idx)

    def _on_combo_index_changed(self, index: int) -> None:
        path = self.combo.currentData()
        if path == "__custom__":
            self._on_browse_custom()
        elif path:
            self.player_changed.emit(path)

    def get_selected_player_path(self) -> str | None:
        path = self.combo.currentData()
        return path if (path and path != "__custom__") else None

    def launch_with_video(self, video_path: str) -> None:
        exe = self.get_selected_player_path()
        if not exe or not os.path.exists(exe):
            # Fallback to default Windows player associated with mp4
            os.startfile(video_path)
            return
        launch_player(exe, video_path)
