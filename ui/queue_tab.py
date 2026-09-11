"""Batch queue management widget for multi-video upscaling."""

from __future__ import annotations

import os
from dataclasses import dataclass
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


@dataclass
class QueueItem:
    input_path: str
    output_path: str
    resolution: str = "Pending"
    status: str = "Queued"


class QueueWidget(QWidget):
    """Batch queue manager supporting multiple video files."""

    item_selected = pyqtSignal(str)  # video path
    play_requested = pyqtSignal(str)  # video path to play

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._queue: list[QueueItem] = []
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Filename", "Input Path", "Scale Target", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        # Action buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Add Video(s)...")
        self.add_btn.clicked.connect(self._on_add_files)
        btn_layout.addWidget(self.add_btn)

        self.remove_btn = QPushButton("🗑️ Remove Selected")
        self.remove_btn.clicked.connect(self._on_remove_selected)
        btn_layout.addWidget(self.remove_btn)

        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_queue)
        btn_layout.addWidget(self.clear_btn)

        btn_layout.addStretch()

        self.play_btn = QPushButton("▶️ Play In Media Player")
        self.play_btn.clicked.connect(self._on_play_selected)
        btn_layout.addWidget(self.play_btn)

        layout.addLayout(btn_layout)

    def _on_add_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Videos to Upscale",
            "",
            "Videos (*.mp4 *.mkv *.avi *.mov *.webm *.flv);;All Files (*.*)",
        )
        for f in files:
            self.add_item(f)

    def add_item(self, path: str) -> None:
        dir_name = os.path.dirname(path)
        base, ext = os.path.splitext(os.path.basename(path))
        out_path = os.path.join(dir_name, f"{base}_nbox_2K{ext}")

        item = QueueItem(input_path=path, output_path=out_path)
        self._queue.append(item)

        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(os.path.basename(path)))
        self.table.setItem(row, 1, QTableWidgetItem(path))
        self.table.setItem(row, 2, QTableWidgetItem("240p/480p -> 2K/4K"))
        status_item = QTableWidgetItem("Queued")
        status_item.setForeground(Qt.GlobalColor.cyan)
        self.table.setItem(row, 3, status_item)

    def _on_remove_selected(self) -> None:
        selected_rows = sorted(set(idx.row() for idx in self.table.selectedIndexes()), reverse=True)
        for row in selected_rows:
            self.table.removeRow(row)
            if row < len(self._queue):
                self._queue.pop(row)

    def clear_queue(self) -> None:
        self.table.setRowCount(0)
        self._queue.clear()

    def _on_play_selected(self) -> None:
        selected = self.table.currentRow()
        if 0 <= selected < len(self._queue):
            item = self._queue[selected]
            target = item.output_path if os.path.exists(item.output_path) else item.input_path
            self.play_requested.emit(target)

    def get_items(self) -> list[QueueItem]:
        return self._queue
