"""Video player integration & discovery bridge for NeuralUpscale."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Sequence

try:
    import winreg
except ImportError:
    winreg = None  # type: ignore[assignment]



@dataclass
class PlayerSpec:
    id: str
    name: str
    executables: list[str]
    default_dirs: list[str]
    registry_keys: list[str]
    cli_flags: list[str]


SUPPORTED_PLAYERS: dict[str, PlayerSpec] = {
    "kmplayer": PlayerSpec(
        id="kmplayer",
        name="KMPlayer",
        executables=["KMPlayer64.exe", "KMPlayer.exe"],
        default_dirs=[
            r"C:\Program Files\KMPlayer 64X",
            r"C:\Program Files\KMPlayer",
            r"C:\Program Files (x86)\The KMPlayer",
            os.path.expandvars(r"%LOCALAPPDATA%\KMPlayer 64X"),
        ],
        registry_keys=[r"SOFTWARE\KMPlayer", r"SOFTWARE\KMPlayer64"],
        cli_flags=[],
    ),
    "mpc-hc": PlayerSpec(
        id="mpc-hc",
        name="MPC-HC (Media Player Classic)",
        executables=["mpc-hc64.exe", "mpc-hc.exe"],
        default_dirs=[
            r"C:\Program Files\MPC-HC",
            r"C:\Program Files (x86)\MPC-HC",
            r"C:\Program Files\K-Lite Codec Pack\MPC-HC64",
            r"C:\Program Files (x86)\K-Lite Codec Pack\MPC-HC",
        ],
        registry_keys=[r"SOFTWARE\MPC-HC\MPC-HC"],
        cli_flags=["/play"],
    ),
    "mpc-be": PlayerSpec(
        id="mpc-be",
        name="MPC-BE",
        executables=["mpc-be64.exe", "mpc-be.exe"],
        default_dirs=[
            r"C:\Program Files\MPC-BE x64",
            r"C:\Program Files (x86)\MPC-BE",
        ],
        registry_keys=[r"SOFTWARE\MPC-BE"],
        cli_flags=["/play"],
    ),
    "potplayer": PlayerSpec(
        id="potplayer",
        name="Daum PotPlayer",
        executables=["PotPlayer64.exe", "PotPlayerMini64.exe", "PotPlayer.exe"],
        default_dirs=[
            r"C:\Program Files\DAUM\PotPlayer",
            r"C:\Program Files (x86)\DAUM\PotPlayer",
        ],
        registry_keys=[r"SOFTWARE\DAUM\PotPlayer"],
        cli_flags=[],
    ),
    "vlc": PlayerSpec(
        id="vlc",
        name="VLC Media Player",
        executables=["vlc.exe"],
        default_dirs=[
            r"C:\Program Files\VideoLAN\VLC",
            r"C:\Program Files (x86)\VideoLAN\VLC",
        ],
        registry_keys=[r"SOFTWARE\VideoLAN\VLC"],
        cli_flags=["--play-and-exit"],
    ),
    "mpv": PlayerSpec(
        id="mpv",
        name="mpv.net / MPV",
        executables=["mpv.exe", "mpvnet.exe"],
        default_dirs=[
            r"C:\Program Files\mpv",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\mpv.net"),
        ],
        registry_keys=[],
        cli_flags=["--force-window=immediate"],
    ),
}


@dataclass
class DetectedPlayer:
    spec: PlayerSpec
    exe_path: str
    is_custom: bool = False


def _check_app_paths_registry(exe_name: str) -> str | None:
    if winreg is None or sys.platform != "win32":
        return None
    for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        key_path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{exe_name}"
        try:
            with winreg.OpenKey(root, key_path) as k:
                val, _ = winreg.QueryValueEx(k, "")
                if val and os.path.exists(val):
                    return val
        except (FileNotFoundError, OSError):
            continue
    return None



def detect_installed_players() -> list[DetectedPlayer]:
    detected: list[DetectedPlayer] = []

    for spec in SUPPORTED_PLAYERS.values():
        found_path: str | None = None

        # 1. PATH lookup
        for exe in spec.executables:
            p = shutil.which(exe)
            if p and os.path.exists(p):
                found_path = p
                break

        # 2. Registry App Paths
        if not found_path:
            for exe in spec.executables:
                p = _check_app_paths_registry(exe)
                if p:
                    found_path = p
                    break

        # 3. Known directory scan
        if not found_path:
            for d in spec.default_dirs:
                if os.path.isdir(d):
                    for exe in spec.executables:
                        candidate = os.path.join(d, exe)
                        if os.path.exists(candidate):
                            found_path = candidate
                            break
                    if found_path:
                        break

        if found_path:
            detected.append(DetectedPlayer(spec=spec, exe_path=found_path))

    return detected


def launch_player(
    player_path: str,
    video_path: str,
    extra_flags: Sequence[str] | None = None,
) -> subprocess.Popen:
    """Launch target player with specified video file."""
    if not os.path.exists(player_path):
        raise FileNotFoundError(f"Player executable not found: {player_path}")
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    cmd = [player_path]
    if extra_flags:
        cmd.extend(extra_flags)
    cmd.append(video_path)

    return subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.DETACHED_PROCESS if os.name == "nt" else 0,
    )
