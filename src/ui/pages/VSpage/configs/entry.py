from ui.pages.objects.pageObjects import *
from PyQt6.QtWidgets import *

class VSEntryDataPage(BasicPage):
    def __init__(self):
        super().__init__("Sistema de Visão: Configuração de Entrada de Dados", QIcon("src/assets/USB.png"))

        # Explanation section
        explanation_label = QLabel("Configure as entradas de dados para o sistema de visão.")
        explanation_label.setWordWrap(True)
        explanation_label.setStyleSheet("font-size: 12px; color: #555; margin-bottom: 10px;")
        explanation_label.setFixedHeight(50)  # Reduced height
        self.add_widget(explanation_label)

        # Form layout
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)

        form_layout.addWidget(QLabel("<b>Fonte de Dados:</b>"))
        data_source_input = QComboBox()
        data_source_input.addItems(["Câmera", "Arquivo de Vídeo", "Stream ao Vivo"])
        form_layout.addWidget(data_source_input)

        form_layout.addWidget(QLabel("<b>Resolução:</b>"))
        resolution_input = QLineEdit()
        resolution_input.setPlaceholderText("Ex: 1920x1080")
        form_layout.addWidget(resolution_input)

        form_layout.addWidget(QLabel("<b>Taxa de Quadros (FPS):</b>"))
        fps_input = QSpinBox()
        fps_input.setRange(1, 120)
        fps_input.setSuffix(" FPS")
        form_layout.addWidget(fps_input)

        # Add a save button
        save_button = QPushButton("Salvar Configurações")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #006400;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #228B22;
            }
        """)
        form_layout.addWidget(save_button)

        self.add_layout(form_layout)