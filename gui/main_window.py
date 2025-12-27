from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout
from gui.copy_screen import CopyScreen
from gui.select_screen import SelectScreen
from gui.burn_screen import BurnScreen
from gui.log_screen import LogScreen

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thiết bị trích xuất & ghi đĩa camera")

        self.copy_screen = None
        self.select_screen = None
        self.burn_screen = None
        self.log_screen = None

        layout = QGridLayout()

        btns = [
            ("Copy file", self.open_copy),
            ("Chọn file / thời gian", self.open_select),
            ("Ghi đĩa", self.open_burn),
            ("Nhật ký", self.open_log),
        ]

        for i, (text, cb) in enumerate(btns):
            b = QPushButton(text)
            b.setMinimumHeight(120)
            b.clicked.connect(cb)
            layout.addWidget(b, i // 2, i % 2)

        self.setLayout(layout)

    def open_copy(self):
        self.copy_screen = CopyScreen()
        self.copy_screen.show()

    def open_select(self):
        self.select_screen = SelectScreen()
        self.select_screen.show()

    def open_burn(self):
        self.burn_screen = BurnScreen()
        self.burn_screen.show()

    def open_log(self):
        self.log_screen = LogScreen()
        self.log_screen.show()
