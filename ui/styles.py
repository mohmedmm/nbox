"""Obsidian Studio palette stylesheet for nbox."""

THEME_STYLESHEET = """
QMainWindow, QDialog {
    background-color: #080b11;
    color: #f1f5f9;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
}

QWidget {
    font-size: 13px;
    color: #94a3b8;
}

/* Studio Glass Cards */
QGroupBox {
    background-color: #0e131f;
    border: 1px solid #1a2336;
    border-radius: 10px;
    margin-top: 14px;
    padding: 16px;
    font-weight: 600;
    font-size: 13px;
    color: #38bdf8;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 10px;
    background-color: #141c2c;
    border: 1px solid #222f47;
    border-radius: 6px;
    color: #38bdf8;
}

/* Studio Primary Action Buttons */
QPushButton#PrimaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00d984, stop:1 #00f0a0);
    color: #04140b;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.2px;
}

QPushButton#PrimaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00eb90, stop:1 #2bf7ad);
}

QPushButton#PrimaryBtn:pressed {
    background-color: #00b86e;
}

QPushButton#PrimaryBtn:disabled {
    background-color: #121c17;
    color: #334d3f;
}

/* Secondary Studio Buttons */
QPushButton {
    background-color: #141b29;
    border: 1px solid #222e44;
    border-radius: 7px;
    padding: 8px 16px;
    color: #f1f5f9;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #1c263a;
    border-color: #334466;
}

QPushButton:pressed {
    background-color: #0f1522;
}

QPushButton:disabled {
    background-color: #0a0e16;
    color: #475569;
    border-color: #141b29;
}

/* Combo Boxes */
QComboBox {
    background-color: #0f1523;
    border: 1px solid #1f2a3f;
    border-radius: 6px;
    padding: 6px 12px;
    color: #f1f5f9;
    min-height: 24px;
}

QComboBox:hover {
    border-color: #334466;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #0f1523;
    border: 1px solid #1f2a3f;
    selection-background-color: #1a2438;
    selection-color: #00f0a0;
    outline: none;
}

/* Line Edits */
QLineEdit {
    background-color: #0a0e17;
    border: 1px solid #1d273c;
    border-radius: 6px;
    padding: 7px 12px;
    color: #f8fafc;
    selection-background-color: #00d984;
    selection-color: #04140b;
}

QLineEdit:focus {
    border-color: #00f0a0;
}

/* Progress Bar */
QProgressBar {
    background-color: #0c101a;
    border: 1px solid #1a2336;
    border-radius: 6px;
    text-align: center;
    color: #f1f5f9;
    font-weight: bold;
    min-height: 20px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00a866, stop:1 #00f0a0);
    border-radius: 5px;
}

/* Status Labels & Metrics */
QLabel#MetricValue {
    font-size: 18px;
    font-weight: 700;
    color: #00f0a0;
    font-family: "Segoe UI", monospace;
}

QLabel#MetricTitle {
    font-size: 11px;
    color: #64748b;
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 0.6px;
}

/* Studio Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #080b11;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #1f2a3f;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #2d3d5b;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
