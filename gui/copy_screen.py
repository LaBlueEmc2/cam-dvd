from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from services.copy_service import CopyService

class CopyScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Copy dữ liệu")

        layout = QVBoxLayout()
        self.label = QLabel("Copy từ /mnt/source → data/staging")
        self.btn = QPushButton("Bắt đầu Copy")

        self.btn.clicked.connect(self.run)

        layout.addWidget(self.label)
        layout.addWidget(self.btn)
        self.setLayout(layout)

    def run(self):
        try:
            CopyService.copy("/mnt/source", "data/staging")
            self.label.setText("✅ Copy hoàn tất")
        except Exception as e:
            self.label.setText(f"❌ Lỗi: {e}")
