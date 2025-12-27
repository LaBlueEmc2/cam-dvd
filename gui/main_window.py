from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QPushButton, QLabel,
    QGridLayout, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QApplication
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtCore import Qt

from gui.copy_screen import CopyScreen
from gui.select_screen import SelectScreen
from gui.burn_screen import BurnScreen
from gui.log_screen import LogScreen


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thiết bị trích xuất & ghi đĩa camera")

        # ===== STACK =====
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # ===== ESC shortcut: quay về Home =====
        esc = QShortcut(QKeySequence(Qt.Key_Escape), self)
        esc.activated.connect(self.go_home)


        # ===== SCREENS =====
        self.menu_screen = self.create_menu()
        self.copy_screen = CopyScreen(self.go_home)
        self.select_screen = SelectScreen(self.go_home)
        self.burn_screen = BurnScreen(self.go_home)
        self.log_screen = LogScreen(self.go_home)

        self.stack.addWidget(self.menu_screen)    # index 0
        self.stack.addWidget(self.copy_screen)    # index 1
        self.stack.addWidget(self.select_screen)  # index 2
        self.stack.addWidget(self.burn_screen)    # index 3
        self.stack.addWidget(self.log_screen)     # index 4

        self.stack.setCurrentIndex(0)

    # ===== MAIN MENU =====
    def create_menu(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        # Top bar (Exit)
        top = QHBoxLayout()
        top_bar = QWidget()
        top_bar.setObjectName("TopBar")

        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(12, 8, 12, 8)   # margin nhẹ
        top_bar_layout.setSpacing(0)

        title = QLabel("DATA EXTRACTION DEVICE")
        title.setStyleSheet("font-size:18px; font-weight:bold;")

        btn_exit = QPushButton("X")
        btn_exit.setObjectName("ExitButton")
        btn_exit.setFixedSize(50, 40)
        btn_exit.clicked.connect(QApplication.quit)

        # Đẩy X sang phải
        top_bar_layout.addWidget(title)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(btn_exit, alignment=Qt.AlignRight | Qt.AlignTop)

        layout.addWidget(top_bar)
        layout.addLayout(top)


        # Grid buttons
        grid = QGridLayout()
        layout.addLayout(grid)

        buttons = [
            ("Copy file", lambda: self.stack.setCurrentIndex(1)),
            ("Chọn file / thời gian", lambda: self.stack.setCurrentIndex(2)),
            ("Ghi đĩa", lambda: self.stack.setCurrentIndex(3)),
            ("Nhật ký", lambda: self.stack.setCurrentIndex(4)),
        ]

        for i, (text, cb) in enumerate(buttons):
            b = QPushButton(text)
            b = QPushButton(text)
            b.setMinimumHeight(140)

            if text == "Copy file":
                b.setObjectName("BtnCopy")
            elif text == "Chọn file / thời gian":
                b.setObjectName("BtnSelect")
            elif text == "Ghi đĩa":
                b.setObjectName("BtnBurn")
            elif text == "Nhật ký":
                b.setObjectName("BtnLog")
            b.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    font-weight: bold;
                }
            """)
            b.clicked.connect(cb)
            grid.addWidget(b, i // 2, i % 2)

        return w

    def go_home(self):
        self.stack.setCurrentIndex(0)
