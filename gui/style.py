APP_STYLE = """
/* ===== GLOBAL ===== */
QMainWindow, QWidget {
    background-color: #f2f2f2;        /* nền xám rất nhạt */
    color: #1c1c1c;
    font-family: "DejaVu Sans";
    font-size: 15px;
}

/* ===== TOP BAR ===== */
#TopBar {
    background-color: #e0e0e0;
    border-bottom: 1px solid #c0c0c0;
}

/* ===== DEFAULT BUTTON ===== */
QPushButton {
    border-radius: 10px;
    padding: 16px;
    font-size: 18px;
    font-weight: bold;
    border: 1px solid #b0b0b0;
}

/* ===== COPY FILE (GREEN) ===== */
QPushButton#BtnCopy {
    background-color: #2ecc71;
    color: #ffffff;
}
QPushButton#BtnCopy:hover {
    background-color: #58d68d;
}
QPushButton#BtnCopy:pressed {
    background-color: #239b56;
}

/* ===== SELECT FILE / TIME (BLUE) ===== */
QPushButton#BtnSelect {
    background-color: #3498db;
    color: #ffffff;
}
QPushButton#BtnSelect:hover {
    background-color: #5dade2;
}
QPushButton#BtnSelect:pressed {
    background-color: #2e86c1;
}

/* ===== BURN DISC (ORANGE) ===== */
QPushButton#BtnBurn {
    background-color: #f39c12;
    color: #000000;
}
QPushButton#BtnBurn:hover {
    background-color: #f5b041;
}
QPushButton#BtnBurn:pressed {
    background-color: #d68910;
}

/* ===== LOG (YELLOW) ===== */
QPushButton#BtnLog {
    background-color: #f7dc6f;
    color: #000000;
}
QPushButton#BtnLog:hover {
    background-color: #f9e79f;
}
QPushButton#BtnLog:pressed {
    background-color: #d4ac0d;
}

/* ===== DISABLED ===== */
QPushButton:disabled {
    background-color: #dddddd;
    color: #888888;
    border: 1px solid #bbbbbb;
}

/* ===== EXIT BUTTON ===== */
QPushButton#ExitButton {
    background-color: #e74c3c;
    color: #ffffff;
}
QPushButton#ExitButton:hover {
    background-color: #ec7063;
}

/* ===== LABEL ===== */
QLabel {
    color: #2c2c2c;
    font-size: 15px;
}

/* ===== TEXT EDIT / LOG VIEW ===== */
QTextEdit {
    background-color: #ffffff;
    border: 1px solid #c0c0c0;
    color: #000000;
    font-family: monospace;
}

/* ===== PROGRESS BAR ===== */
QProgressBar {
    background-color: #eaeaea;
    border: 1px solid #b0b0b0;
    border-radius: 6px;
    text-align: center;
    color: #000000;
    height: 24px;
}

/* COPY PROGRESS (GREEN) */
QProgressBar#ProgressCopy::chunk {
    background-color: #2ecc71;
    border-radius: 6px;
}

/* BURN PROGRESS (ORANGE) */
QProgressBar#ProgressBurn::chunk {
    background-color: #f39c12;
    border-radius: 6px;
}
"""
