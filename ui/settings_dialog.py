"""Settings dialog for advanced GPU, encoder and neural parameters."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
)

from core.hardware import detect as detect_hardware
from core.models import REGISTRY


class SettingsDialog(QDialog):
    """Settings modal for configuring GPU execution, tile sizes and encoder."""

    def __init__(self, parent=None, current_settings=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("NeuralUpscale — Settings & Hardware Engine")
        self.resize(520, 380)
        self.setModal(True)

        self._settings = current_settings or {
            "tile_size": 1024,
            "use_nvenc": True,
            "crf": 18,
            "preview_interval": 1,
            "model_id": "realesr-animevideov3",
        }

        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(18)

        form = QFormLayout()
        form.setSpacing(12)

        # Hardware display
        hw = detect_hardware()
        gpu_name = hw.primary_gpu.name if hw.primary_gpu else "CPU Mode"
        vram_str = f"{hw.primary_gpu.vram_mb} MB" if hw.primary_gpu else "N/A"
        hw_label = QLabel(f"<b>{gpu_name}</b> ({vram_str}) — Backend: <b>{hw.backend.upper()}</b>")
        hw_label.setStyleSheet("color: #00ff88; font-size: 13px;")
        form.addRow("Active Hardware:", hw_label)

        # Neural Model
        self.model_combo = QComboBox()
        for mid, spec in REGISTRY.items():
            self.model_combo.addItem(f"{spec.label} ({spec.scale}x)", mid)
        idx = self.model_combo.findData(self._settings.get("model_id"))
        if idx >= 0:
            self.model_combo.setCurrentIndex(idx)
        form.addRow("Default Model:", self.model_combo)

        # Tile Size
        self.tile_combo = QComboBox()
        self.tile_combo.addItem("Auto (Optimized for VRAM)", 0)
        self.tile_combo.addItem("1024x1024 (High VRAM >= 12GB)", 1024)
        self.tile_combo.addItem("512x512 (Standard VRAM >= 6GB)", 512)
        self.tile_combo.addItem("256x256 (Safe / Low VRAM)", 256)
        t_idx = self.tile_combo.findData(self._settings.get("tile_size", 1024))
        if t_idx >= 0:
            self.tile_combo.setCurrentIndex(t_idx)
        form.addRow("VRAM Tile Splitter:", self.tile_combo)

        # Hardware NVENC Encoder
        self.nvenc_check = QCheckBox("Enable NVIDIA NVENC (Zero CPU Load)")
        self.nvenc_check.setChecked(self._settings.get("use_nvenc", True))
        form.addRow("Hardware Acceleration:", self.nvenc_check)

        # CRF / Quality Slider
        crf_layout = QHBoxLayout()
        self.crf_slider = QSlider(Qt.Orientation.Horizontal)
        self.crf_slider.setRange(10, 30)
        self.crf_slider.setValue(self._settings.get("crf", 18))
        self.crf_val_lbl = QLabel(str(self.crf_slider.value()))
        self.crf_val_lbl.setStyleSheet("font-weight: bold; color: #58a6ff;")
        self.crf_slider.valueChanged.connect(lambda v: self.crf_val_lbl.setText(str(v)))
        crf_layout.addWidget(self.crf_slider)
        crf_layout.addWidget(self.crf_val_lbl)
        form.addRow("CRF Quality (Lower = Higher):", crf_layout)

        # Preview Frame Interval
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 10)
        self.interval_spin.setValue(self._settings.get("preview_interval", 1))
        self.interval_spin.setSuffix(" frame(s)")
        form.addRow("Preview Refresh Interval:", self.interval_spin)

        main_layout.addLayout(form)
        main_layout.addStretch()

        # Dialog buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("PrimaryBtn")
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        main_layout.addLayout(btn_layout)

    def _on_save(self) -> None:
        self._settings["model_id"] = self.model_combo.currentData()
        self._settings["tile_size"] = self.tile_combo.currentData()
        self._settings["use_nvenc"] = self.nvenc_check.isChecked()
        self._settings["crf"] = self.crf_slider.value()
        self._settings["preview_interval"] = self.interval_spin.value()
        self.accept()

    def get_settings(self) -> dict:
        return self._settings
