"""GPU/hardware detection for NeuralUpscale."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from typing import Literal

Backend = Literal["cuda", "directml", "cpu"]


@dataclass
class GPUInfo:
    name: str
    vram_mb: int
    backend: Backend


@dataclass
class HardwareProfile:
    backend: Backend
    gpus: list[GPUInfo] = field(default_factory=list)
    recommended_tile: int = 512

    @property
    def primary_gpu(self) -> GPUInfo | None:
        return self.gpus[0] if self.gpus else None

    def tile_for_vram(self) -> int:
        if not self.gpus:
            return 256
        vram = self.gpus[0].vram_mb
        if vram >= 8192:
            return 1024
        if vram >= 4096:
            return 512
        return 256


def _torch_cuda_gpus() -> list[GPUInfo]:
    try:
        import torch

        if not torch.cuda.is_available():
            return []
        gpus = []
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            gpus.append(
                GPUInfo(
                    name=props.name,
                    vram_mb=props.total_memory // (1024 * 1024),
                    backend="cuda",
                )
            )
        return gpus
    except Exception:
        return []


def _directml_gpus() -> list[GPUInfo]:
    try:
        import torch_directml  # type: ignore[import-untyped]

        count = torch_directml.device_count()
        gpus = []
        for i in range(count):
            gpus.append(
                GPUInfo(
                    name=torch_directml.device_name(i),
                    vram_mb=0,  # DirectML doesn't expose VRAM easily
                    backend="directml",
                )
            )
        return gpus
    except Exception:
        return []


def _nvml_gpus() -> list[GPUInfo]:
    """Fallback VRAM query via nvidia-smi when torch is absent."""
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            timeout=5,
        )
        gpus = []
        for line in out.strip().splitlines():
            name, vram = line.split(",")
            gpus.append(GPUInfo(name=name.strip(), vram_mb=int(vram.strip()), backend="cuda"))
        return gpus
    except Exception:
        return []


def detect() -> HardwareProfile:
    cuda_gpus = _torch_cuda_gpus() or _nvml_gpus()
    if cuda_gpus:
        profile = HardwareProfile(backend="cuda", gpus=cuda_gpus)
        profile.recommended_tile = profile.tile_for_vram()
        return profile

    dml_gpus = _directml_gpus()
    if dml_gpus:
        return HardwareProfile(backend="directml", gpus=dml_gpus, recommended_tile=512)

    return HardwareProfile(backend="cpu", recommended_tile=256)
