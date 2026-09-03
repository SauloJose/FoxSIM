import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QToolBar, QVBoxLayout, QWidget, QMessageBox
)
from PyQt6.QtGui import QIcon, QAction
from pyqode.core.api import CodeEdit
from pyqode.core.modes import PygmentsSyntaxHighlighter

if __name__ == "__main__":
    app = QApplication(sys.argv)

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("PyQode Python Editor (PyQt6)")
            self.resize(800, 600)
            # ...existing code...
            self.editor = CodeEdit()
            self.editor.modes.append(PygmentsSyntaxHighlighter(self.editor.document()))
            self.current_file = None
            # ...existing code...

            layout = QVBoxLayout()
            layout.addWidget(self.editor)
            container = QWidget()
            container.setLayout(layout)
            self.setCentralWidget(container)

            self.create_toolbar()

        def create_toolbar(self):
            toolbar = QToolBar("Main Toolbar")
            self.addToolBar(toolbar)

            new_action = QAction(QIcon(), "New", self)
            new_action.triggered.connect(self.new_file)
            toolbar.addAction(new_action)

            open_action = QAction(QIcon(), "Open", self)
            open_action.triggered.connect(self.open_file)
            toolbar.addAction(open_action)

            save_action = QAction(QIcon(), "Save", self)
            save_action.triggered.connect(self.save_file)
            toolbar.addAction(save_action)

            delete_action = QAction(QIcon(), "Delete", self)
            delete_action.triggered.connect(self.delete_file)
            toolbar.addAction(delete_action)

        def new_file(self):
            self.editor.setPlainText("", 'text/x-python', 'utf-8')
            self.current_file = None

        def open_file(self):
            file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Python Files (*.py);;Text Files (*.txt);;All Files (*)")
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.editor.setPlainText(f.read(), 'text/x-python', 'utf-8')
                self.current_file = file_path
                self.setWindowTitle(f"PyQode Python Editor - {file_path}")

        def save_file(self):
            if self.current_file is None:
                file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Python Files (*.py);;Text Files (*.txt);;All Files (*)")
                if not file_path:
                    return
                self.current_file = file_path
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            QMessageBox.information(self, "Saved", f"File saved: {self.current_file}")

        def delete_file(self):
            import os
            if self.current_file and os.path.exists(self.current_file):
                reply = QMessageBox.question(self, "Delete", f"Delete file {self.current_file}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    os.remove(self.current_file)
                    self.editor.setPlainText("", 'text/x-python', 'utf-8')
                    self.current_file = None
                    QMessageBox.information(self, "Deleted", "File deleted.")
            else:
                QMessageBox.warning(self, "Warning", "No file to delete.")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())