from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from services.burn_service import BurnService

class BurnScreen(QWidget):
    def __init__(self, go_back):
        super().__init__()
        self.go_back = go_back

        self.setWindowTitle("Ghi đĩa")

        layout = QVBoxLayout()

        # Top bar
        top = QHBoxLayout()
        btn_back = QPushButton("← Back")
        btn_back.clicked.connect(self.go_back)
        top.addWidget(btn_back)
        top.addStretch()
        layout.addLayout(top)

        self.label = QLabel("Ghi data/staging ra CD/DVD")
        btn = QPushButton("Ghi đĩa")

        btn.clicked.connect(self.run)

        layout.addWidget(self.label)
        layout.addWidget(btn)
        self.setLayout(layout)

    def run(self):
        try:
            BurnService.burn("data/staging")
            self.label.setText("✅ Ghi đĩa hoàn tất")
        except Exception as e:
            self.label.setText(f"❌ Lỗi: {e}")
