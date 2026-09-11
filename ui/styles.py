"""Modern dark glassmorphism stylesheet for NeuralUpscale."""

THEME_STYLESHEET = """
QMainWindow, QDialog {
    background-color: #0b0e14;
    color: #e6edf3;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
}

QWidget {
    font-size: 13px;
    color: #c9d1d9;
}

/* Group Boxes / Cards */
QGroupBox {
    background-color: #121721;
    border: 1px solid #232a3b;
    border-radius: 10px;
    margin-top: 14px;
    padding: 16px;
    font-weight: 600;
    font-size: 13px;
    color: #58a6ff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 10px;
    background-color: #1b2333;
    border: 1px solid #2f3b52;
    border-radius: 5px;
    color: #58a6ff;
}

/* Primary Action Buttons */
QPushButton#PrimaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00c873, stop:1 #00e599);
    color: #05140c;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: bold;
}

QPushButton#PrimaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00df81, stop:1 #26f0aa);
}

QPushButton#PrimaryBtn:pressed {
    background-color: #00a65e;
}

QPushButton#PrimaryBtn:disabled {
    background-color: #1b2620;
    color: #486352;
}

/* Secondary Buttons */
QPushButton {
    background-color: #1a2233;
    border: 1px solid #2d3a54;
    border-radius: 7px;
    padding: 8px 16px;
    color: #e6edf3;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #242f47;
    border-color: #3b4d6e;
}

QPushButton:pressed {
    background-color: #161c2b;
}

QPushButton:disabled {
    background-color: #10141d;
    color: #4b5563;
    border-color: #1a202c;
}

/* Combo Boxes */
QComboBox {
    background-color: #131926;
    border: 1px solid #27334a;
    border-radius: 6px;
    padding: 6px 12px;
    color: #e6edf3;
    min-height: 24px;
}

QComboBox:hover {
    border-color: #3d5075;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #131926;
    border: 1px solid #27334a;
    selection-background-color: #233047;
    selection-color: #00ffaa;
    outline: none;
}

/* Line Edits */
QLineEdit {
    background-color: #0f1420;
    border: 1px solid #253147;
    border-radius: 6px;
    padding: 7px 12px;
    color: #f0f6fc;
    selection-background-color: #00c873;
    selection-color: #000000;
}

QLineEdit:focus {
    border-color: #00c873;
}

/* Progress Bar */
QProgressBar {
    background-color: #131926;
    border: 1px solid #222c3f;
    border-radius: 6px;
    text-align: center;
    color: #e6edf3;
    font-weight: bold;
    min-height: 20px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #009955, stop:1 #00e599);
    border-radius: 5px;
}

/* Status Labels & Metrics */
QLabel#MetricValue {
    font-size: 18px;
    font-weight: bold;
    color: #00e599;
}

QLabel#MetricTitle {
    font-size: 11px;
    color: #8b949e;
    text-transform: uppercase;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #0b0e14;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #253147;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #3b4d6e;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
