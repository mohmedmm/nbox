# nbox 🚀

<p align="center">
  <img src="assets/icons/app.png" width="128" height="128" alt="nbox Logo" />
</p>

<p align="center">
  <b>Subtle Neural Video Enhancer & Real-Time Studio (240p → 2K / 4K) with Native Browser & Media Player Integration</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/CUDA-100%25_GPU-76B900?style=for-the-badge&logo=nvidia&logoColor=white" alt="CUDA" />
  <img src="https://img.shields.io/badge/NVENC-Hardware_Encode-00E599?style=for-the-badge" alt="NVENC" />
  <img src="https://img.shields.io/badge/PyQt6-Modern_Dark_UI-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt6" />
  <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License" />
</p>

---

## ⚡ What is nbox?

**nbox** delivers subtle, natural neural video enhancement and upscaling directly to your desktop videos and web browser streams. Rather than harsh artificial sharpening or blurry interpolation, **nbox** employs refined contrast-adaptive sub-pixel kernels and neural super-resolution to recover micro-textures (hair, fine text, fabrics, skin clarity) gracefully.

Transform low-resolution footage (**240p / 360p / 480p / 720p**) into crisp **1080p, 2K (1440p), or 4K UHD** in real-time, completely accelerated on your **NVIDIA GPU** with zero CPU overhead, with direct media player integration (**KMPlayer, MPC-HC, VLC, PotPlayer, MPV**) and native in-browser support.

---

## ✨ Key Features

- **⚡ 100% Pure GPU Pipeline**:
  - Neural inference executed in **FP16 (Half Precision)** utilizing GPU Tensor Cores.
  - Video encoding delegated to **NVIDIA NVENC** (`h264_nvenc` / `hevc_nvenc`) — zero CPU stutter.
- **🌐 Native In-Browser Extension (Chrome & Edge)**:
  - Runs directly inside your browser on **YouTube, Twitch, Netflix, or any video site** with zero extra windows.
  - **Customizable Watermark `[ ■ nbox: ON ]`**: Click on-screen to toggle enhancement on/off anytime.
  - **Watermark Hide Option**: Disable the on-screen badge completely from extension settings for clean, distraction-free playback.
- **🔬 Subtle Contrast-Adaptive Neural Tuning**:
  - Sub-pixel edge reconstruction and micro-contrast synthesis with zero halo artifacts.
  - Gentle, natural clarity rather than aggressive oversharpening.
- **🎬 Interactive Split-Slider Live Preview**:
  - Watch the neural reconstruction happen frame-by-frame in real-time.
  - Interactive draggable slider compares original low-res against upscaled high-res side-by-side.
- **🎮 Seamless Media Player Integration**:
  - Auto-detects installed players: **KMPlayer, MPC-HC, MPC-BE, PotPlayer, VLC, mpv**.
  - One-click launch: play the upscaled video immediately upon processing or preview.
  - Add any custom media player executable via the intuitive GUI.
- **🧠 Zero-Dependency Neural Architectures**:
  - Self-contained implementation of **SRVGGNetCompact** and **RRDBNet**.
  - No bloated or fragile compilation toolchains required.
- **📋 Batch Processing Queue**:
  - Add multiple episodes, anime clips, or legacy videos to the queue with automatic resolution scaling.
- **🖥️ Dynamic VRAM Tiling Engine**:
  - Auto-detects your GPU's VRAM (e.g. 8GB, 12GB, 16GB) and automatically selects optimal tile sizes (256, 512, 1024) to avoid Out-Of-Memory errors.

---

## 🏗️ Architecture Pipeline

```
[ Input Video (240p) ]
          │
          ▼
   ffmpeg Demuxer (Raw BGR24 Stream)
          │
          ▼
   NVIDIA Tensor Cores (FP16 Neural Pass: SRVGGNetCompact / RRDBNet)
          │
          ├─────────────────────────┐
          ▼                         ▼
   ffmpeg NVENC Encoder    Interactive GUI Split-Slider
   (h264_nvenc / hevc_nvenc)  (Real-Time Frame HUD)
          │
          ▼
[ Enhanced 2K Video File ]
          │
          ▼
[ Instant Launch: KMPlayer / MPC-HC / VLC ]
```

---

## 🚀 Quick Start

### 1. Requirements
- Windows 10/11 64-bit
- NVIDIA GeForce RTX GPU (RTX 20, 30, 40, or 50 series recommended)
- Python 3.10 or higher
- [FFmpeg](https://ffmpeg.org/download.html) installed and in your system `PATH`

### 2. Installation

```bash
git clone https://github.com/your-username/NeuralUpscale.git
cd NeuralUpscale

pip install -r requirements.txt
```

### 3. Run

```bash
python main.py
```

---

## 🎯 Model Options

| Model | Architecture | Scale | Best For | Speed |
|---|---|---|---|---|
| **RealESR-AnimeVideo-v3** | Compact VGG | 4x | Anime, Cartoons, High-FPS Video | ⚡ Blazing (Real-time) |
| **Real-ESRGAN x4+** | RRDBNet (23B) | 4x | Real-world movies, vintage clips | 💎 Cinematic Quality |
| **RealESRNet x4+** | RRDBNet (23B) | 4x | Natural footage with reduced artifacts | ⚖️ Balanced |
| **Real-ESRGAN x4+ Anime** | RRDBNet (6B) | 4x | Sharp line-art and illustrated media | 🎨 High Detail Anime |
| **Real-ESRGAN x2+** | RRDBNet (23B) | 2x | 480p → 1080p / 1080p → 4K | 🚀 Fast 2x Pass |

---

## 📺 Supported Media Players

- **KMPlayer** (KMPlayer 64X & Classic)
- **MPC-HC** (Media Player Classic - Home Cinema)
- **MPC-BE** (Media Player Classic - Black Edition)
- **Daum PotPlayer**
- **VLC Media Player**
- **mpv / mpv.net**
- **Custom Player** (Browse and link any custom video player or emulator)

---

## 🧪 Running Tests

```bash
pytest -v
```

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.
