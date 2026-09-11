"""Blackmagic Neon Mint Studio palette stylesheet for nbox."""

THEME_STYLESHEET = """
QMainWindow, QDialog {
    background-color: #0a0d12;
    color: #f1f5f9;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
}

QWidget {
    font-size: 13px;
    color: #94a3b8;
}

/* Studio Titanium Cards */
QGroupBox {
    background-color: #121824;
    border: 1px solid #25334c;
    border-radius: 10px;
    margin-top: 14px;
    padding: 16px;
    font-weight: 700;
    font-size: 13px;
    color: #00ff88;
}

QGroupBox:hover {
    border-color: #354769;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 3px 12px;
    background-color: #182233;
    border: 1px solid #2f4263;
    border-radius: 6px;
    color: #00ff88;
    font-weight: 700;
}

/* High-Contrast Neon Mint Action Buttons */
QPushButton#PrimaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00e676, stop:1 #00ff88);
    color: #01170b;
    border: 1px solid #33ff99;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.3px;
}

QPushButton#PrimaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1aff8c, stop:1 #66ffb2);
    border-color: #66ffb2;
}

QPushButton#PrimaryBtn:pressed {
    background-color: #00c853;
}

QPushButton#PrimaryBtn:disabled {
    background-color: #121b16;
    color: #344d3d;
    border-color: #1a2920;
}

/* Secondary Studio Titanium Buttons */
QPushButton {
    background-color: #162030;
    border: 1px solid #2d3e5c;
    border-radius: 7px;
    padding: 8px 16px;
    color: #f1f5f9;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #1e2c44;
    border-color: #00ff88;
    color: #00ff88;
}

QPushButton:pressed {
    background-color: #111a27;
}

QPushButton:disabled {
    background-color: #0d121c;
    color: #475569;
    border-color: #182232;
}

/* Combo Boxes */
QComboBox {
    background-color: #101520;
    border: 1px solid #26354f;
    border-radius: 6px;
    padding: 6px 12px;
    color: #f1f5f9;
    min-height: 24px;
    font-weight: 500;
}

QComboBox:hover {
    border-color: #00ff88;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #121824;
    border: 1px solid #2f4263;
    selection-background-color: #1c2a42;
    selection-color: #00ff88;
    outline: none;
    padding: 4px;
}

/* Line Edits */
QLineEdit {
    background-color: #0c1018;
    border: 1px solid #24344e;
    border-radius: 6px;
    padding: 7px 12px;
    color: #ffffff;
    selection-background-color: #00e676;
    selection-color: #01170b;
}

QLineEdit:focus {
    border: 1px solid #00ff88;
}

/* Tab Bar */
QTabWidget::pane {
    border: 1px solid #25334c;
    background: #0a0d12;
    border-radius: 8px;
}

QTabBar::tab {
    background: #121824;
    color: #7f95b3;
    padding: 9px 22px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 700;
    font-size: 13px;
    border: 1px solid #1e283c;
    border-bottom: none;
}

QTabBar::tab:selected {
    background: #182233;
    color: #00ff88;
    border: 1px solid #2f4263;
    border-bottom: 3px solid #00ff88;
}

QTabBar::tab:hover:!selected {
    background: #151d2b;
    color: #d0dbe8;
    border-color: #2b3952;
}

/* Progress Bar */
QProgressBar {
    background-color: #0d121c;
    border: 1px solid #202b3e;
    border-radius: 6px;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
    min-height: 22px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00a854, stop:1 #00ff88);
    border-radius: 5px;
}

/* Status Labels & Metrics */
QLabel#MetricValue {
    font-size: 19px;
    font-weight: 800;
    color: #00ff88;
    font-family: "Consolas", "Segoe UI", monospace;
}

QLabel#MetricTitle {
    font-size: 11px;
    color: #7f95b3;
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 0.7px;
}

/* Studio Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #0a0d12;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #25334c;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #00ff88;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
