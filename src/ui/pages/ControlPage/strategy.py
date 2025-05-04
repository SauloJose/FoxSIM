from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QWidget, QMessageBox,
    QSplitter, QTreeView
)
from PyQt6.QtGui import QIcon, QFont, QFileSystemModel
from PyQt6.QtCore import Qt, QDir, QSize, QSortFilterProxyModel
from pyqode.core.api import CodeEdit
from pyqode.core.modes import PygmentsSyntaxHighlighter
from pyqode.core.panels import LineNumberPanel
import os

from ui.pages.objects.pageObjects import *

class HidePycacheProxyModel(QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row, source_parent):
        index = self.sourceModel().index(source_row, 0, source_parent)
        name = self.sourceModel().fileName(index)
        # Oculta __pycache__
        if name == "__pycache__":
            return False
        return super().filterAcceptsRow(source_row, source_parent)

class CTstrategyPage(BasicPage):
    def __init__(self):
        super().__init__("Controle: Estratégias", QIcon("src/assets/PID.png"))

        button_style = """
            QPushButton {
                background-color: #14532d;
                color: white;
                border-radius: 5px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #22c55e;
                color: #222;
            }
        """
        explanation_label = QLabel(
            "Edite ou crie estratégias de controle diretamente nos arquivos Python da pasta 'intelligence'."
        )
        explanation_label.setWordWrap(True)
        explanation_label.setStyleSheet("""
            font-size: 15px;
            margin-bottom: 18px;
            color: #444;
            background: #f8f8f8;
            border-radius: 8px;
            padding: 12px 20px;
        """)
        explanation_label.setFixedHeight(60)
        explanation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_widget(explanation_label)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setSizes([160, 600])

        # Caminho da pasta intelligence
        self.intelligence_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../simulator/intelligence")
        )

        # Modelo de arquivos: mostra arquivos e subpastas (estrutura de árvore)
        self.model = QFileSystemModel()
        self.model.setRootPath(self.intelligence_dir)
        self.model.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)

        # Proxy para ocultar __pycache__
        self.proxy_model = HidePycacheProxyModel()
        self.proxy_model.setSourceModel(self.model)

        self.tree = QTreeView()
        self.tree.setModel(self.proxy_model)
        self.tree.setRootIndex(self.proxy_model.mapFromSource(self.model.index(self.intelligence_dir)))
        self.tree.setMaximumWidth(300)
        self.tree.setHeaderHidden(True)
        self.tree.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        self.tree.setIconSize(QSize(16, 16))
        self.tree.doubleClicked.connect(self.open_selected_file)
        # Oculta todas as colunas exceto a 0 (nome/ícone)
        for col in range(1, self.model.columnCount()):
            self.tree.hideColumn(col)
        splitter.addWidget(self.tree)

        # Editor de código
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)

        self.editor = CodeEdit()
        self.editor.modes.append(PygmentsSyntaxHighlighter(self.editor.document()))
        self.editor.panels.append(LineNumberPanel())
        self.editor.setTabStopDistance(4)

        # Fonte VSCode-like
        font = QFont("Cascadia Code, Consolas, Menlo, Monaco, monospace", 12)
        self.editor.setFont(font)
        self.editor.setStyleSheet("background-color: #ffffff; color: #d4d4d4;")
        self.current_file = None

        # Botões de arquivo
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        btn_new = QPushButton("Novo")
        btn_new.clicked.connect(self.new_file)
        btn_layout.addWidget(btn_new)

        btn_open = QPushButton("Abrir")
        btn_open.clicked.connect(self.open_file)
        btn_layout.addWidget(btn_open)

        btn_save = QPushButton("Salvar")
        btn_save.clicked.connect(self.save_file)
        btn_layout.addWidget(btn_save)

        btn_delete = QPushButton("Deletar")
        btn_delete.clicked.connect(self.delete_file)
        btn_layout.addWidget(btn_delete)

        editor_layout.addLayout(btn_layout)
        editor_layout.addWidget(self.editor)
        splitter.addWidget(editor_container)

        btn_new.setStyleSheet(button_style)
        btn_open.setStyleSheet(button_style)
        btn_save.setStyleSheet(button_style)
        btn_delete.setStyleSheet(button_style)

        main_layout = QVBoxLayout()
        main_layout.addWidget(splitter)
        container = QWidget()
        container.setLayout(main_layout)
        self.add_widget(container)

    def open_selected_file(self, index):
        file_path = self.model.filePath(self.proxy_model.mapToSource(index))
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.editor.setPlainText(f.read(), 'text/x-python', 'utf-8')
                self.current_file = file_path
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Não foi possível abrir o arquivo:\n{e}")

    def new_file(self):
        from PyQt6.QtWidgets import QInputDialog
        file_name, ok = QInputDialog.getText(self, "Novo arquivo", "Nome do novo arquivo (.py):")
        if ok and file_name:
            if not file_name.endswith(".py"):
                file_name += ".py"
            file_path = os.path.join(self.intelligence_dir, file_name)
            if os.path.exists(file_path):
                QMessageBox.warning(self, "Aviso", "Arquivo já existe.")
                return
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("")
            self.model.setRootPath(self.intelligence_dir)  # Atualiza a árvore
            self.editor.setPlainText("", 'text/x-python', 'utf-8')
            self.current_file = file_path
            
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir arquivo", self.intelligence_dir, "Python Files (*.py);;Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.editor.setPlainText(f.read(), 'text/x-python', 'utf-8')
            self.current_file = file_path

    def save_file(self):
        if self.current_file is None:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Salvar arquivo", self.intelligence_dir, "Python Files (*.py)"
            )
            if not file_path:
                return
            self.current_file = file_path
        with open(self.current_file, 'w', encoding='utf-8') as f:
            f.write(self.editor.toPlainText())
        QMessageBox.information(self, "Salvo", f"Arquivo salvo: {self.current_file}")
        self.model.setRootPath(self.intelligence_dir)  # Atualiza a árvore


    def delete_file(self):
        import os
        if self.current_file and os.path.exists(self.current_file):
            reply = QMessageBox.question(
                self, "Deletar", f"Deletar arquivo {self.current_file}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                os.remove(self.current_file)
                self.editor.setPlainText("", 'text/x-python', 'utf-8')
                self.current_file = None
                QMessageBox.information(self, "Deletado", "Arquivo deletado.")
                self.model.setRootPath(self.intelligence_dir)  # Atualiza a árvore

        else:
            QMessageBox.warning(self, "Aviso", "Nenhum arquivo para deletar.")

    def destroy(self):
        # Libere arquivos abertos, threads, etc.
        if hasattr(self, 'editor') and hasattr(self.editor, 'close'):
            try:
                self.editor.close()
            except Exception:
                pass
        self.current_file = None