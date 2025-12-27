from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QHBoxLayout
from services.copy_service import CopyService

class LogScreen(QWidget):
    def __init__(self, go_back):
        super().__init__()
        self.go_back = go_back

        self.setWindowTitle("Nhật ký")

        layout = QVBoxLayout()

        # Top bar
        top = QHBoxLayout()
        btn_back = QPushButton("← Back")
        btn_back.clicked.connect(self.go_back)
        top.addWidget(btn_back)
        top.addStretch()
        layout.addLayout(top)
        
        self.text = QTextEdit()
        self.text.setReadOnly(True)

        try:
            with open("data/logs/log.json") as f:
                self.text.setText(f.read())
        except:
            self.text.setText("Chưa có nhật ký")

        layout.addWidget(self.text)
        self.setLayout(layout)
