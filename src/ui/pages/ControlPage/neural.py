from PyQt6.QtWidgets import (
    QLabel, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QFormLayout, QGroupBox, QSpinBox, QFileDialog, QWidget
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from ui.pages.objects.pageObjects import *
from ui.pages.ControlPage.PIDcontrol import SimBot
import os, json
import pyqtgraph as pg
import numpy as np  # Corrigir: garantir import do numpy
import time

class CTneuralPage(BasicPage):
    def __init__(self, log_manager: LogManager = None):
        super().__init__("Controle: Redes Neurais", QIcon("src/assets/IA.png"), log_manager)

        # Explanation section
        explanation_label = QLabel(
            "Configure os parâmetros de treinamento da rede neural e visualize os gráficos de desempenho."
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
        main_layout.setContentsMargins(10,10,10,10)
        main_layout.setSpacing(30)

        # Left: Configuração dos parâmetros, controles e diagrama da rede
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(20)

        # Grupo de posicionamento
        position_group = QGroupBox("Posicionamento")
        position_group.setStyleSheet(self.getGroupBoxStyle())
        position_form = QFormLayout()
        position_form.setSpacing(12)

        # Posição inicial do robô
        self.robot_x = QLineEdit()
        self.robot_x.setPlaceholderText("Coordenada X")
        self.robot_y = QLineEdit()
        self.robot_y.setPlaceholderText("Coordenada Y")
        position_form.addRow("Posição Inicial:", self.createDoubleInputRow(self.robot_x, self.robot_y))

        # Posição desejada
        self.target_x = QLineEdit()
        self.target_x.setPlaceholderText("Coordenada X")
        self.target_y = QLineEdit()
        self.target_y.setPlaceholderText("Coordenada Y")
        position_form.addRow("Posição Desejada:", self.createDoubleInputRow(self.target_x, self.target_y))

        # Adicionar obstáculo
        self.obstacle_x = QLineEdit()
        self.obstacle_x.setPlaceholderText("X")
        self.obstacle_y = QLineEdit()
        self.obstacle_y.setPlaceholderText("Y")
        self.obstacle_radius = QLineEdit()
        self.obstacle_radius.setPlaceholderText("Raio")
        add_obstacle_btn = QPushButton("Adicionar Obstáculo")
        add_obstacle_btn.setStyleSheet(self.getButtonStyle("#228B22"))
        position_form.addRow("Obstáculo:", self.createTripleInputRow(
            self.obstacle_x, self.obstacle_y, self.obstacle_radius, add_obstacle_btn))

        position_group.setLayout(position_form)
        left_layout.addWidget(position_group)

        # Grupo de treinamento
        training_group = QGroupBox("Treinamento")
        training_group.setStyleSheet(self.getGroupBoxStyle())
        training_form = QFormLayout()
        training_form.setSpacing(12)

        self.learning_rate = QLineEdit()
        self.learning_rate.setPlaceholderText("Ex: 0.001")
        training_form.addRow("Learning Rate:", self.learning_rate)

        self.epochs = QSpinBox()
        self.epochs.setRange(1, 10000)
        self.epochs.setValue(100)
        training_form.addRow("Épocas:", self.epochs)

        training_group.setLayout(training_form)
        left_layout.addWidget(training_group)

        # Botões de controle
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)

        self.save_btn = QPushButton("Salvar")
        self.save_btn.setStyleSheet(self.getButtonStyle("#228B22"))
        self.restore_btn = QPushButton("Restaurar")
        self.restore_btn.setStyleSheet(self.getButtonStyle("#1E90FF"))
        self.start_btn = QPushButton("Iniciar")
        self.start_btn.setStyleSheet(self.getButtonStyle("#32CD32"))
        self.pause_btn = QPushButton("Pausar")
        self.pause_btn.setStyleSheet(self.getButtonStyle("#FF8C00"))
        self.pause_btn.setEnabled(False)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.restore_btn)
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.pause_btn)

        left_layout.addWidget(button_container)

        # Espaço reservado para o diagrama da rede neural
        network_group = QGroupBox("Diagrama da Rede Neural")
        network_group.setStyleSheet(self.getGroupBoxStyle())
        network_layout = QVBoxLayout(network_group)
        network_layout.setContentsMargins(5, 15, 5, 5)
        
        # Widget reservado para o diagrama (será preenchido posteriormente)
        self.network_diagram = QWidget()
        self.network_diagram.setStyleSheet("""
            background: white;
            border: 1px solid #ddd;
            min-height: 300px;
        """)
        self.network_diagram.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        network_layout.addWidget(self.network_diagram)
        left_layout.addWidget(network_group, stretch=1)  # Adiciona stretch para ocupar espaço disponível

        main_layout.addWidget(left_container, stretch=1)

        # Right: Gráficos (pyqtgraph)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(20)

        # Gráfico de erro (altura fixa de 200px)
        error_group = QGroupBox("Minimização do Erro")
        error_group.setStyleSheet(self.getGroupBoxStyle())
        error_layout = QVBoxLayout(error_group)
        error_layout.setContentsMargins(0, 0, 0, 0)
        
        # Gráfico de erro usando pyqtgraph
        self.error_plot = pg.PlotWidget()
        self.error_plot.setBackground('w')
        self.error_plot.setMinimumHeight(200)
        self.error_plot.setMaximumHeight(200)
        error_layout.addWidget(self.error_plot)
        right_layout.addWidget(error_group)

        # Gráfico de trajetória (ocupa o restante do espaço)
        trajectory_group = QGroupBox("Trajetória")
        trajectory_group.setStyleSheet(self.getGroupBoxStyle())
        trajectory_layout = QVBoxLayout(trajectory_group)
        trajectory_layout.setContentsMargins(0, 0, 0, 0)
        
        # Gráfico de trajetória usando pyqtgraph
        self.trajectory_plot = pg.PlotWidget()
        self.trajectory_plot.setBackground('w')
        trajectory_layout.addWidget(self.trajectory_plot)
        right_layout.addWidget(trajectory_group, stretch=1)  # Ocupa todo espaço restante

        main_layout.addWidget(right_container, stretch=2)
        self.add_widget(main_container)

    def getGroupBoxStyle(self):
        return """
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #228B22;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """

    def getButtonStyle(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 13px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #333;
            }}
            QPushButton:disabled {{
                background-color: #ccc;
            }}
        """

    def createDoubleInputRow(self, widget1, widget2):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        widget1.setFixedWidth(80)
        widget2.setFixedWidth(80)
        layout.addWidget(widget1)
        layout.addWidget(widget2)
        return container

    def createTripleInputRow(self, widget1, widget2, widget3, button):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        widget1.setFixedWidth(60)
        widget2.setFixedWidth(60)
        widget3.setFixedWidth(60)
        layout.addWidget(widget1)
        layout.addWidget(widget2)
        layout.addWidget(widget3)
        layout.addWidget(button)
        return container

    def destroy(self):
        # Libere threads, arquivos, etc.
        pass
    