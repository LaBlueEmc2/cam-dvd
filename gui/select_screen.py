from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout

class SelectScreen(QWidget):
    def __init__(self, go_back):
        super().__init__()
        self.go_back = go_back
        
        self.setWindowTitle("Chọn file / thời gian")

        layout = QVBoxLayout()

        # Top bar
        top = QHBoxLayout()
        btn_back = QPushButton("← Back")
        btn_back.clicked.connect(self.go_back)
        top.addWidget(btn_back)
        top.addStretch()
        layout.addLayout(top)
        
        layout.addWidget(QLabel(
            "Bước này dùng để:\n"
            "- Chọn file video\n"
            "- Cắt theo thời gian (sẽ tích hợp ffmpeg)"
        ))
        self.setLayout(layout)
