from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit

class LogScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nhật ký")

        layout = QVBoxLayout()
        self.text = QTextEdit()
        self.text.setReadOnly(True)

        try:
            with open("data/logs/log.json") as f:
                self.text.setText(f.read())
        except:
            self.text.setText("Chưa có nhật ký")

        layout.addWidget(self.text)
        self.setLayout(layout)
