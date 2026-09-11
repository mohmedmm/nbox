<div align="center">

# nbox

**轻量级微质感神经视频画质增强与实时超分辨率工作室 (240p -> 2K / 4K)**  
*零 CPU 负担 • Tensor Core 硬件加速 • 浏览器原生扩展与全能播放器联动*

[![English](https://img.shields.io/badge/Language-English-blue.svg)](README.md)
[![Simplified Chinese](https://img.shields.io/badge/Language-Simplified_Chinese-red.svg)](#)
[![Russian](https://img.shields.io/badge/Language-Russian-lightgrey.svg)](README.ru.md)

<br/>

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![CUDA 12+](https://img.shields.io/badge/CUDA-100%25_GPU-76B900?style=flat-square&logo=nvidia&logoColor=white)](https://developer.nvidia.com/cuda-toolkit)
[![NVENC](https://img.shields.io/badge/NVENC-Zero_CPU_Encode-00F0A0?style=flat-square)](https://developer.nvidia.com/video-codec-sdk)
[![PyQt6 Studio UI](https://img.shields.io/badge/UI-Obsidian_Studio-0F172A?style=flat-square)](https://riverbankcomputing.com/software/pyqt/)
[![License MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

[English](README.md) • [简体中文](README.zh-CN.md) • [Русский](README.ru.md)

</div>

---

## 项目简介

nbox 是一款专为视频画面打造的轻量级神经画质增强与实时超分辨率工具。不同于传统生硬锐化算法带来的白边光晕，也不同于过度生成的失真模型，nbox 专注于微质感重塑（毛发细丝、皮肤纹理、远景文本、织物细节），在自然细腻的基调下还原画面清晰度。

可将低分辨率网络流、老电影或番剧动画（240p / 360p / 480p / 720p）实时提升至 1080p、2K (1440p) 乃至 4K。全程运行于 NVIDIA GPU，享受零 CPU 占用的疾速流转，并深度适配 KMPlayer、MPC-HC、PotPlayer、VLC、MPV 以及各类 Chromium 浏览器。

### 核心特性
- 纯 GPU 硬件管线：CUDA FP16 结合 Tensor Core 推理，搭载 NVIDIA NVENC（h264_nvenc / hevc_nvenc）硬件极速压制，零掉帧。
- 浏览器原生实时挂载：专为 Chrome / Edge 设计的 Manifest V3 扩展，利用 WebGL CAS 算法实时作用于 Bilibili、YouTube、Twitch 等所有 video 播放器。
- 可交互绿色小方块水印：直接点击屏幕角落图标即可随时切换增强开关；亦可在扩展弹窗中一键隐藏水印。
- 专业播放器无缝串联：自动探测本机安装的 KMPlayer、MPC-HC、MPC-BE、PotPlayer、VLC、MPV，超分完成即可自动唤起播放。
- 黑曜石专业工作室界面：高格调深色 Glassmorphism 设计，内置实时动态分屏对比滑块与帧率监控仪表盘。

---

## 画质对比

来自 nbox 实时超分与画质增强的抓帧对比：

### 样例 1：低分辨率番剧视频 (240p -> 2K 神经细节增强)

| 原始画面 (增强关闭) | nbox 神经画质增强 (增强开启) |
| :---: | :---: |
| ![样例 1 OFF](assets/screenshots/off1.png) | ![样例 1 ON](assets/screenshots/on1.png) |

### 样例 2：复杂电影场景 (无光晕、无涂抹、边缘自然锐利)

| 原始画面 (增强关闭) | nbox 神经画质增强 (增强开启) |
| :---: | :---: |
| ![样例 2 OFF](assets/screenshots/off2.png) | ![样例 2 ON](assets/screenshots/on2.png) |

---

## 性能基准测试

测试平台环境：Windows 11, CUDA 12.4, PyTorch 2.3+cu121, NVENC H.264：

| 显卡型号 | 输入分辨率 | 目标分辨率 | 模型架构 | 运行帧率 (FPS) | 显存占用 |
| :--- | :---: | :---: | :--- | :---: | :---: |
| RTX 4090 (24GB) | 240p / 480p | 2K (1440p) | Compact Real-Time VGG | 145+ FPS | ~1.8 GB |
| RTX 4080 SUPER (16GB) | 240p / 480p | 2K (1440p) | Compact Real-Time VGG | 120+ FPS | ~1.6 GB |
| RTX 4070 Ti (12GB) | 480p | 2K (1440p) | Compact Real-Time VGG | 95+ FPS | ~1.4 GB |
| RTX 3080 (10GB) | 480p | 1080p / 2K | Compact Real-Time VGG | 72+ FPS | ~1.4 GB |
| RTX 3060 (12GB) | 240p / 360p | 1080p | Compact Real-Time VGG | 60+ FPS | ~1.1 GB |
| RTX 4080 SUPER | 720p | 4K UHD (2160p) | RRDBNet 23B (影院级) | 38 FPS | ~3.9 GB |

---

## 系统架构

```
                       +-------------------------------+
                       |      输入视频流 / 网页视频      |
                       |     (240p / 480p / 720p)      |
                       +---------------+---------------+
                                       |
                        直接管道 / WebGL 像素捕获
                                       |
                                       v
    +---------------------------------------------------------------------+
    |                       nbox 神经计算引擎                             |
    |  - CUDA FP16 Tensor Core 推理 (SRVGGNetCompact / RRDBNet)          |
    |  - 对比度自适应亚像素重塑核 (自然轻度 0.35 系数)                    |
    |  - 动态显存分块分配器 (彻底告别 CUDA Out-Of-Memory)                |
    +------------------+-------------------------------+------------------+
                       |                               |
                       v                               v
    +----------------------------------+   +------------------------------+
    |       NVIDIA NVENC 硬件压制      |   |     实时 Studio 监控仪表盘   |
    |  - 零拷贝内存共享管道            |   |  - 动态拖拽分屏对比滑块      |
    |  - 硬件极速 H.264 / HEVC 编码    |   |  - FPS 实时遥测与渲染进度    |
    +------------------+---------------+   +------------------------------+
                       |
                       v
    +---------------------------------------------------------------------+
    |                       外部播放器一键唤醒                            |
    |      KMPlayer  •  MPC-HC  •  MPC-BE  •  PotPlayer  •  VLC  •  MPV   |
    +---------------------------------------------------------------------+
```

---

## 快速上手

### 1. 系统要求
- Windows 10 / 11 64位
- NVIDIA GeForce RTX 独立显卡（推荐 RTX 20/30/40/50 系列）
- Python 3.10 或更高版本
- 系统已安装并配置 FFmpeg 环境变量

### 2. 桌面客户端安装

```bash
# 克隆仓库
git clone https://github.com/mohmedmm/nbox.git
cd nbox

# 安装依赖项
pip install -r requirements.txt

# 启动 nbox 工作室
python main.py
```

### 3. Chrome / Edge 浏览器扩展安装

1. 打开浏览器并访问扩展管理页：
   - Chrome：`chrome://extensions`
   - Edge：`edge://extensions`
2. 开启右上角的 开发者模式 (Developer Mode)。
3. 点击 加载已解压的扩展程序 (Load unpacked)，并选择项目根目录下的 `browser_extension` 文件夹。
4. 打开 Bilibili、YouTube 或任意视频网站，画面将自动激活神经超清渲染。

### 4. Tampermonkey 油猴脚本

在 Tampermonkey 中直接导入 `nbox_browser.user.js` 即可实现全浏览器通用画质增强。

---

## 支持的本地播放器

软件自动检测并支持一键唤起：
- KMPlayer（KMPlayer 64X 及经典版）
- MPC-HC（Media Player Classic - Home Cinema）
- MPC-BE（Media Player Classic - Black Edition）
- Daum PotPlayer
- VLC Media Player
- mpv / mpv.net
- 自定义播放器（可在界面中指定任意第三方播放器可执行文件）

---

## 单元测试

执行测试套件确认系统环境完整度：

```bash
pytest -v
```

---

## 开源许可

本项目基于 MIT License 开源。详情参阅 [LICENSE](LICENSE)。
