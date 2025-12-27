import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from gui.style import APP_STYLE


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    win = MainWindow()
    win.showFullScreen()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
