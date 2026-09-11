"""Browser video window discovery and real-time screen grabber engine."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from typing import Callable

import cv2
import numpy as np
import psutil
from PyQt6.QtGui import QGuiApplication, QImage


@dataclass
class BrowserTarget:
    name: str
    pid: int
    exe: str


SUPPORTED_BROWSER_EXES = {
    "chrome.exe": "Google Chrome",
    "msedge.exe": "Microsoft Edge",
    "firefox.exe": "Mozilla Firefox",
    "brave.exe": "Brave Browser",
    "opera.exe": "Opera",
    "vivaldi.exe": "Vivaldi",
}


def detect_active_browsers() -> list[BrowserTarget]:
    """Return a list of currently running web browser processes."""
    found: dict[str, BrowserTarget] = {}
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            name = proc.info["name"]
            if name and name.lower() in SUPPORTED_BROWSER_EXES:
                clean_name = SUPPORTED_BROWSER_EXES[name.lower()]
                if clean_name not in found:
                    found[clean_name] = BrowserTarget(
                        name=clean_name,
                        pid=proc.info["pid"],
                        exe=name,
                    )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return list(found.values())


def grab_screen_region(x: int, y: int, width: int, height: int) -> np.ndarray | None:
    """Fast native screen capture using primary Qt compositor device."""
    screen = QGuiApplication.primaryScreen()
    if not screen:
        return None

    pix = screen.grabWindow(0, x, y, width, height)
    if pix.isNull():
        return None

    img = pix.toImage().convertToFormat(QImage.Format.Format_BGR888)
    ptr = img.bits()
    ptr.setsize(img.sizeInBytes())
    bpl = img.bytesPerLine()
    arr = np.frombuffer(ptr, np.uint8).reshape((img.height(), bpl))[:, : img.width() * 3]
    return arr.reshape((img.height(), img.width(), 3)).copy()

