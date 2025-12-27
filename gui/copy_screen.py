from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QProgressBar, QApplication
from services.copy_service import CopyService
import time

class CopyScreen(QWidget):
    def __init__(self, go_back):
        super().__init__()
        self.go_back = go_back

        layout = QVBoxLayout(self)

        # Top bar
        top = QHBoxLayout()
        btn_back = QPushButton("← Back")
        btn_back.clicked.connect(self.go_back)
        top.addWidget(btn_back)
        top.addStretch()
        layout.addLayout(top)

        # Content
        self.label = QLabel("Copy từ /mnt/source → data/staging")
        btn = QPushButton("Bắt đầu Copy")
        btn.clicked.connect(self.run)

        layout.addWidget(self.label)
        layout.addWidget(btn)

        self.progress = QProgressBar()
        self.progress.setObjectName("ProgressCopy")
        self.progress.setValue(0)

        layout.addWidget(self.progress)


    def run(self):
        try:
            for i in range(0, 101, 10):
                self.progress.setValue(i)
                QApplication.processEvents()
                time.sleep(0.2)

            CopyService.copy("/mnt/source", "data/staging")
            self.label.setText("✅ Copy hoàn tất")
        except Exception as e:
            self.label.setText(f"❌ Lỗi: {e}")
