from PyQt6.QtWidgets import (
    QLabel, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QFormLayout, QGroupBox, QSpinBox, QFileDialog, QWidget
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from ui.pages.objects.pageObjects import *


class CTneuralPage(BasicPage):
    def __init__(self):
        super().__init__("Controle: Redes Neurais", QIcon("src/assets/IA.png"))

        # Explanation section
        explanation_label = QLabel(
            "Configure os parâmetros das redes neurais, buffers, e gerencie os pesos. "
            "Ajuste hiperparâmetros, salve/carregue pesos e monitore o status da rede."
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
        explanation_label.setFixedHeight(80)
        explanation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_widget(explanation_label)

        # Main container
        main_container = QWidget()
        main_container.setObjectName("neuralMainContainer")
        main_container.setStyleSheet("""
            #neuralMainContainer {
                background: #f4f4f7;
                border: 1.5px solid #e0e0e0;
                border-radius: 16px;
                padding: 24px;
            }
        """)
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(40, 50, 40, 32)  # Aumenta margens
        main_layout.setSpacing(56)  # Espaço maior entre grupos

        # Left: Configuração dos parâmetros
        params_group = QGroupBox("Parâmetros da Rede Neural")
        params_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                color: #228B22;
            }
            QGroupBox::title {
                subcontrol-origin: content;
                subcontrol-position: top left;
                left: 10px;
                top: 4px;
                padding: 0 8px;
                background: transparent;
            }
        """)
        params_form = QFormLayout()
        params_form.setContentsMargins(12, 24, 12, 12)
        params_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        params_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        params_form.setSpacing(16)  # Espaço maior entre linhas

        # Hiperparâmetros
        self.learning_rate = QLineEdit()
        self.learning_rate.setPlaceholderText("Ex: 0.001")
        self.learning_rate.setFixedWidth(100)
        params_form.addRow("Learning Rate:", self.learning_rate)

        self.epochs = QSpinBox()
        self.epochs.setRange(1, 10000)
        self.epochs.setValue(100)
        self.epochs.setFixedWidth(100)
        params_form.addRow("Épocas:", self.epochs)

        self.batch_size = QSpinBox()
        self.batch_size.setRange(1, 1024)
        self.batch_size.setValue(32)
        self.batch_size.setFixedWidth(100)
        params_form.addRow("Batch Size:", self.batch_size)

        self.buffer_size = QSpinBox()
        self.buffer_size.setRange(1, 100000)
        self.buffer_size.setValue(1000)
        self.buffer_size.setFixedWidth(100)
        params_form.addRow("Buffer Size:", self.buffer_size)

        self.hidden_layers = QSpinBox()
        self.hidden_layers.setRange(1, 10)
        self.hidden_layers.setValue(2)
        self.hidden_layers.setFixedWidth(100)
        params_form.addRow("Camadas Ocultas:", self.hidden_layers)

        self.neurons_per_layer = QSpinBox()
        self.neurons_per_layer.setRange(1, 512)
        self.neurons_per_layer.setValue(64)
        self.neurons_per_layer.setFixedWidth(100)
        params_form.addRow("Neurônios/Camada:", self.neurons_per_layer)

        # Botão para aplicar configurações
        apply_btn = QPushButton("Aplicar Parâmetros")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #006400;
                color: white;
                border-radius: 6px;
                padding: 8px 22px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #228B22;
            }
        """)
        params_form.addRow("", apply_btn)
        params_group.setLayout(params_form)
        main_layout.addWidget(params_group, stretch=1)

        # Right: Gerenciamento de pesos e status
        weights_group = QGroupBox("Gerenciamento de Pesos & Status")
        weights_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                color: #228B22;
            }
            QGroupBox::title {
                subcontrol-origin: content;
                subcontrol-position: top left;
                left: 10px;
                top: 4px;
                padding: 0 8px;
                background: transparent;
            }
        """)
        weights_layout = QVBoxLayout()
        weights_layout.setContentsMargins(12, 24, 12, 12)
        weights_layout.setSpacing(18)  # Espaço maior entre widgets

        # Salvar pesos
        save_row = QHBoxLayout()
        self.save_path = QLineEdit()
        self.save_path.setPlaceholderText("Arquivo para salvar pesos")
        self.save_path.setFixedWidth(180)
        save_btn = QPushButton("Salvar Pesos")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #228B22;
                color: white;
                border-radius: 5px;
                padding: 6px 18px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #006400;
            }
        """)
        save_row.addWidget(self.save_path)
        save_row.addWidget(save_btn)
        weights_layout.addLayout(save_row)

        # Carregar pesos
        load_row = QHBoxLayout()
        self.load_path = QLineEdit()
        self.load_path.setPlaceholderText("Arquivo para carregar pesos")
        self.load_path.setFixedWidth(180)
        load_btn = QPushButton("Carregar Pesos")
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #bbb;
                color: #222;
                border-radius: 5px;
                padding: 6px 18px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #888;
                color: white;
            }
        """)
        load_row.addWidget(self.load_path)
        load_row.addWidget(load_btn)
        weights_layout.addLayout(load_row)

        # Status da rede neural
        status_label = QLabel("Status: <span style='color:#228B22;'>Pronto</span>")
        status_label.setStyleSheet("font-size: 14px; margin-top: 18px;")
        weights_layout.addWidget(status_label)

        weights_group.setLayout(weights_layout)
        main_layout.addWidget(weights_group, stretch=1)

        # Add main container to the page
        self.add_widget(main_container)