<div align="center">

# nbox

**Деликатное нейросетевое улучшение видео и масштабирование в реальном времени (240p -> 2K / 4K)**  
*Нулевая нагрузка на CPU • Аппаратное ускорение Tensor Core • Интеграция с браузерами и медиаплеерами*

[![English](https://img.shields.io/badge/Language-English-blue.svg)](README.md)
[![Simplified Chinese](https://img.shields.io/badge/Language-Simplified_Chinese-red.svg)](README.zh-CN.md)
[![Russian](https://img.shields.io/badge/Language-Russian-lightgrey.svg)](#)

<br/>

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![CUDA 12+](https://img.shields.io/badge/CUDA-100%25_GPU-76B900?style=flat-square&logo=nvidia&logoColor=white)](https://developer.nvidia.com/cuda-toolkit)
[![NVENC](https://img.shields.io/badge/NVENC-Zero_CPU_Encode-00F0A0?style=flat-square)](https://developer.nvidia.com/video-codec-sdk)
[![PyQt6 Studio UI](https://img.shields.io/badge/UI-Obsidian_Studio-0F172A?style=flat-square)](https://riverbankcomputing.com/software/pyqt/)
[![License MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

[English](README.md) • [Simplified Chinese](README.zh-CN.md) • [Russian](README.ru.md)

</div>

---

## Обзор проекта

nbox — это легковесный инструмент для нейронного улучшения качества и апскейла видео в реальном времени. В отличие от агрессивной интерполяции или генеративных моделей, создающих неестественные артефакты и ореолы, nbox ориентирован на тонкое восстановление микротекстур (волосы, текстура ткани, поры кожи, читаемость мелкого шрифта), сохраняя оригинальную кинематографическую зернистость.

Инструмент масштабирует низкокачественные видеопотоки (240p / 360p / 480p / 720p) до четкого разрешения 1080p, 2K (1440p) или 4K. Весь пайплайн выполняется на NVIDIA GPU без нагрузки на центральный процессор, обеспечивая запуск в популярных плеерах (KMPlayer, MPC-HC, PotPlayer, VLC, MPV) и веб-браузерах.

### Ключевые возможности
- 100% GPU-пайплайн: Инференс в FP16 на ядрах Tensor Core и аппаратное кодирование через NVIDIA NVENC (h264_nvenc / hevc_nvenc).
- Прямая интеграция в браузер: Расширение Manifest V3 для Chrome и Edge улучшает видеопотоки на YouTube, Twitch, Кинопоиске и любых HTML5-плеерах с помощью WebGL CAS.
- Интерактивный индикатор: Водяной знак в углу видео позволяет переключать улучшение в один клик или полностью скрывать его в настройках.
- Мгновенный запуск в медиаплеерах: Автоопределение и поддержка KMPlayer, MPC-HC, MPC-BE, PotPlayer, VLC, MPV или любого пользовательского исполняемого файла.
- Obsidian Studio GUI: Графический интерфейс на PyQt6 со сплит-слайдером сравнения, мониторингом FPS в реальном времени и пакетной очередью.

---

## Сравнение качества

Кадры, полученные во время работы алгоритма nbox:

### Пример 1: Низкое разрешение стрима (240p -> 2K Нейросеть)

| Исходный кадр (Улучшение ВЫКЛ) | nbox Деликатное улучшение (ВКЛ) |
| :---: | :---: |
| ![Пример 1 ВЫКЛ](assets/screenshots/off1.png) | ![Пример 1 ВКЛ](assets/screenshots/on1.png) |

### Пример 2: Сложная кинематографическая сцена (Без ореолов и размытия)

| Исходный кадр (Улучшение ВЫКЛ) | nbox Деликатное улучшение (ВКЛ) |
| :---: | :---: |
| ![Пример 2 ВЫКЛ](assets/screenshots/off2.png) | ![Пример 2 ВКЛ](assets/screenshots/on2.png) |

---

## Производительность и тесты

Тестовая конфигурация: Windows 11, CUDA 12.4, PyTorch 2.3+cu121, кодировщик NVENC H.264:

| Видеокарта | Входное разрешение | Целевое разрешение | Архитектура модели | Скорость (FPS) | VRAM |
| :--- | :---: | :---: | :--- | :---: | :---: |
| RTX 4090 (24GB) | 240p / 480p | 2K (1440p) | Compact Real-Time VGG | 145+ FPS | ~1.8 GB |
| RTX 4080 SUPER (16GB) | 240p / 480p | 2K (1440p) | Compact Real-Time VGG | 120+ FPS | ~1.6 GB |
| RTX 4070 Ti (12GB) | 480p | 2K (1440p) | Compact Real-Time VGG | 95+ FPS | ~1.4 GB |
| RTX 3080 (10GB) | 480p | 1080p / 2K | Compact Real-Time VGG | 72+ FPS | ~1.4 GB |
| RTX 3060 (12GB) | 240p / 360p | 1080p | Compact Real-Time VGG | 60+ FPS | ~1.1 GB |
| RTX 4080 SUPER | 720p | 4K UHD (2160p) | RRDBNet 23B (Кинематографичный) | 38 FPS | ~3.9 GB |

---

## Архитектура системы

```
                       +-------------------------------+
                       |     Входное видео / Стрим     |
                       |     (240p / 480p / 720p)      |
                       +---------------+---------------+
                                       |
                        Direct Pipe / WebGL Захват
                                       |
                                       v
    +---------------------------------------------------------------------+
    |                       Нейронное ядро nbox                           |
    |  - Инференс CUDA FP16 Tensor Cores (SRVGGNetCompact / RRDBNet)      |
    |  - Адаптивное субпиксельное восстановление (параметр alpha: 0.35)   |
    |  - Динамический тайлинг VRAM (защита от Out-Of-Memory)              |
    +------------------+-------------------------------+------------------+
                       |                               |
                       v                               v
    +----------------------------------+   +------------------------------+
    |       Аппаратный энкодер NVENC   |   |   Телеметрия Studio HUD      |
    |  - Пайпы с нулевым копированием  |   |  - Слайдер сравнения кадра   |
    |  - Аппаратное H.264 / HEVC сжатие|   |  - Мониторинг FPS и времени  |
    +------------------+---------------+   +------------------------------+
                       |
                       v
    +---------------------------------------------------------------------+
    |                 Мост с внешними видеоплеерами                       |
    |      KMPlayer  •  MPC-HC  •  MPC-BE  •  PotPlayer  •  VLC  •  MPV   |
    +---------------------------------------------------------------------+
```

---

## Быстрый старт

### 1. Системные требования
- Windows 10 / 11 64-бит
- Видеокарта NVIDIA GeForce RTX (серии 20, 30, 40 или 50)
- Python 3.10 или новее
- Установленный FFmpeg, добавленный в системный PATH

### 2. Запуск настольного приложения

```bash
# Клонирование репозитория
git clone https://github.com/mohmedmm/nbox.git
cd nbox

# Установка зависимостей
pip install -r requirements.txt

# Запуск приложения
python main.py
```

### 3. Установка расширения для браузера (Chrome / Edge)

1. Откройте в браузере страницу расширений:
   - Chrome: `chrome://extensions`
   - Edge: `edge://extensions`
2. Активируйте переключатель Режим разработчика (Developer Mode).
3. Нажмите кнопку Загрузить распакованное (Load unpacked) и укажите папку `browser_extension` из репозитория.
4. Откройте YouTube, Twitch или любой веб-плеер: видео активирует нейросетевой фильтр.

### 4. Пользовательский скрипт Tampermonkey

Для Firefox, Brave или Safari установите файл `nbox_browser.user.js` через менеджер Tampermonkey или Violentmonkey.

---

## Поддерживаемые плееры

Приложение автоматически находит установленные видеоплееры и позволяет запускать видео в один клик:
- KMPlayer (KMPlayer 64X и Classic)
- MPC-HC (Media Player Classic - Home Cinema)
- MPC-BE (Media Player Classic - Black Edition)
- Daum PotPlayer
- VLC Media Player
- mpv / mpv.net
- Любой плеер (можно указать путь к любому `.exe` в настройках)

---

## Тестирование

Запуск тестов с помощью pytest:

```bash
pytest -v
```

---

## Лицензия

Проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).
