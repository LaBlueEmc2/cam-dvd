from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class SelectScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chọn file / thời gian")

        layout = QVBoxLayout()
        layout.addWidget(QLabel(
            "Bước này dùng để:\n"
            "- Chọn file video\n"
            "- Cắt theo thời gian (sẽ tích hợp ffmpeg)"
        ))
        self.setLayout(layout)
