from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.mainWindow.MainWindows import *

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("src/assets/logo_minus.png"))
    window = MainWindow()

    window.show()
    sys.exit(app.exec())