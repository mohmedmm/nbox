import os
import cv2
from ui.styles import THEME_STYLESHEET


def test_screenshot_assets():
    expected_assets = ["off1.png", "on1.png", "off2.png", "on2.png"]
    for name in expected_assets:
        path = os.path.join("assets", "screenshots", name)
        assert os.path.exists(path), f"Missing screenshot asset: {path}"
        img = cv2.imread(path)
        assert img is not None and img.size > 0


def test_obsidian_theme_tokens():
    assert "#0a0d12" in THEME_STYLESHEET
    assert "#00ff88" in THEME_STYLESHEET
    assert "#25334c" in THEME_STYLESHEET


def test_multilingual_docs_presence():
    docs = ["README.md", "README.zh-CN.md", "README.ru.md"]
    for doc in docs:
        assert os.path.exists(doc), f"Missing doc: {doc}"
        with open(doc, "r", encoding="utf-8") as f:
            content = f.read()
            assert "off1.png" in content
            assert "on1.png" in content
            assert "off2.png" in content
            assert "on2.png" in content
