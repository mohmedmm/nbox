"""Tests for player bridge and detection."""

import pytest
from core.player_bridge import SUPPORTED_PLAYERS, detect_installed_players, launch_player


def test_supported_players_registry():
    assert "kmplayer" in SUPPORTED_PLAYERS
    assert "mpc-hc" in SUPPORTED_PLAYERS
    assert "vlc" in SUPPORTED_PLAYERS
    assert "potplayer" in SUPPORTED_PLAYERS


def test_detect_installed_players_returns_list():
    players = detect_installed_players()
    assert isinstance(players, list)


def test_launch_nonexistent_raises():
    with pytest.raises(FileNotFoundError):
        launch_player("non_existent_player.exe", "fake_video.mp4")
