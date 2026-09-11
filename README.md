<div align="center">

# nbox

**Subtle Neural Video Enhancer & Real-Time Upscaler (240p -> 2K / 4K)**  
*Zero CPU Load • Tensor Core Acceleration • Native Browser & Media Player Integration*

[![English](https://img.shields.io/badge/Language-English-blue.svg)](#)
[![Simplified Chinese](https://img.shields.io/badge/Language-Simplified_Chinese-red.svg)](README.zh-CN.md)
[![Russian](https://img.shields.io/badge/Language-Russian-lightgrey.svg)](README.ru.md)

<br/>

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![CUDA 12+](https://img.shields.io/badge/CUDA-100%25_GPU-76B900?style=flat-square&logo=nvidia&logoColor=white)](https://developer.nvidia.com/cuda-toolkit)
[![NVENC](https://img.shields.io/badge/NVENC-Zero_CPU_Encode-00F0A0?style=flat-square)](https://developer.nvidia.com/video-codec-sdk)
[![PyQt6 Studio UI](https://img.shields.io/badge/UI-Obsidian_Studio-0F172A?style=flat-square)](https://riverbankcomputing.com/software/pyqt/)
[![License MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

[English](README.md) • [Simplified Chinese](README.zh-CN.md) • [Russian](README.ru.md)

</div>

---

## Overview

nbox is a lightweight, real-time neural video enhancer designed for video upscaling without artificial hallucinations, ringing, or excessive cartoon lines. It transforms low-resolution web streams, vintage footage, and anime (240p / 360p / 480p / 720p) into crisp 1080p, 2K, or 4K video.

Unlike brute-force bicubic scaling or aggressive hallucination models, nbox focuses on subtle micro-texture restoration (fine facial hair, skin pores, distant text, textile textures) while preserving original cinematic grain.

### Key Highlights
- Hardware Accelerated: Pure CUDA FP16 tensor core execution paired with zero-CPU NVENC hardware encoding.
- In-Browser Real-Time Hook: Native Chrome/Edge Manifest V3 extension runs on YouTube, Twitch, Netflix, and HTML5 video players with WebGL CAS.
- Watermark Badge: Toggle enhancement on the fly or hide the badge in settings.
- Media Player Bridge: One-click launch into KMPlayer, MPC-HC, MPC-BE, VLC, PotPlayer, or MPV.
- Studio GUI: Dark-mode UI with live split-screen comparison slider, FPS telemetry HUD, and batch queue.

---

## Visual Comparisons

Captured live from nbox real-time neural processing:

### Sample 1: Low-Resolution Anime Stream (240p -> 2K Neural)

| Original Stream (Enhancement OFF) | nbox Neural Detail (Enhancement ON) |
| :---: | :---: |
| ![Sample 1 OFF](assets/screenshots/off1.png) | ![Sample 1 ON](assets/screenshots/on1.png) |

### Sample 2: Complex Cinematic Scene (Clean Edges, Zero Halo)

| Original Stream (Enhancement OFF) | nbox Neural Detail (Enhancement ON) |
| :---: | :---: |
| ![Sample 2 OFF](assets/screenshots/off2.png) | ![Sample 2 ON](assets/screenshots/on2.png) |

---

## Performance Benchmarks

Tested on Windows 11 (CUDA 12.4, PyTorch 2.3+cu121, NVENC H.264 high-quality profile):

| GPU | Input Resolution | Output Target | Model Architecture | Speed (FPS) | VRAM Usage |
| :--- | :---: | :---: | :--- | :---: | :---: |
| RTX 4090 (24GB) | 240p / 480p | 2K (1440p) | Compact Real-Time VGG | 145+ FPS | ~1.8 GB |
| RTX 4080 SUPER (16GB) | 240p / 480p | 2K (1440p) | Compact Real-Time VGG | 120+ FPS | ~1.6 GB |
| RTX 4070 Ti (12GB) | 480p | 2K (1440p) | Compact Real-Time VGG | 95+ FPS | ~1.4 GB |
| RTX 3080 (10GB) | 480p | 1080p / 2K | Compact Real-Time VGG | 72+ FPS | ~1.4 GB |
| RTX 3060 (12GB) | 240p / 360p | 1080p | Compact Real-Time VGG | 60+ FPS | ~1.1 GB |
| RTX 4080 SUPER | 720p | 4K UHD (2160p) | RRDBNet 23B (Quality) | 38 FPS | ~3.9 GB |

---

## Architecture

```
                       +-------------------------------+
                       |     Input Video / Stream      |
                       |     (240p / 480p / 720p)      |
                       +---------------+---------------+
                                       |
                        Direct Pipe / WebGL Capture
                                       |
                                       v
    +---------------------------------------------------------------------+
    |                       nbox Neural Engine                            |
    |  - CUDA FP16 Tensor Core Inference (SRVGGNetCompact / RRDBNet)     |
    |  - Contrast-Adaptive Sub-Pixel Reconstruction (Gentle 0.35 Alpha)   |
    |  - Dynamic VRAM Tile Allocator (Zero Out-Of-Memory)                 |
    +------------------+-------------------------------+------------------+
                       |                               |
                       v                               v
    +----------------------------------+   +------------------------------+
    |        NVIDIA NVENC Engine       |   |  Real-Time Studio HUD        |
    |  - Zero-copy memory pipes        |   |  - Split Comparison Slider   |
    |  - Hardware H.264 / HEVC encode  |   |  - Live FPS / ETA Telemetry  |
    +------------------+---------------+   +------------------------------+
                       |
                       v
    +---------------------------------------------------------------------+
    |                 Instant Playback Bridge                             |
    |      KMPlayer  •  MPC-HC  •  MPC-BE  •  PotPlayer  •  VLC  •  MPV   |
    +---------------------------------------------------------------------+
```

---

## Quick Start

### 1. Requirements
- Windows 10 / 11 64-bit
- NVIDIA GPU (RTX 20, 30, 40, or 50 series)
- Python 3.10+
- FFmpeg installed and in your system PATH

### 2. Desktop Application Setup

```bash
# Clone the repository
git clone https://github.com/mohmedmm/nbox.git
cd nbox

# Install dependencies
pip install -r requirements.txt

# Launch nbox Studio
python main.py
```

### 3. Chrome / Edge In-Browser Extension Setup

1. Open your browser and navigate to:
   - Chrome: `chrome://extensions`
   - Edge: `edge://extensions`
2. Enable Developer Mode (toggle in top right corner).
3. Click Load unpacked and select the `browser_extension` folder inside this repository.
4. Videos on YouTube, Twitch, Netflix, or any HTML5 web player will receive real-time neural sharpening with the on-screen badge.

### 4. Tampermonkey Userscript

Install `nbox_browser.user.js` directly into Tampermonkey or Violentmonkey for cross-browser userscript support.

---

## Supported Media Players

nbox automatically detects installed media players on your system and provides one-click launching:

- KMPlayer (KMPlayer 64X & Classic)
- MPC-HC (Media Player Classic - Home Cinema)
- MPC-BE (Media Player Classic - Black Edition)
- Daum PotPlayer
- VLC Media Player
- mpv / mpv.net
- Custom Executables (Link any custom player binary via the GUI)

---

## Testing

Run the test suite with pytest:

```bash
pytest -v
```

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
