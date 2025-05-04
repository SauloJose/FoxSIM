from PyQt6.QtWidgets import (
    QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QFormLayout, QGroupBox, QWidget
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from ui.pages.objects.pageObjects import *


class CTstrategyPage(BasicPage):
    def __init__(self):
        super().__init__("Controle: Estratégias", QIcon("src/assets/PID.png"))

        # Explanation section
        explanation_label = QLabel(
            "Configure os parâmetros do controle PID e visualize o resultado da simulação. "
            "Ajuste os ganhos e pontos de referência para observar o comportamento do sistema."
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
        main_container.setObjectName("strategyMainContainer")
        main_container.setStyleSheet("""
            #strategyMainContainer {
                background: #f4f4f7;
                border: 1.5px solid #e0e0e0;
                border-radius: 16px;
                padding: 24px;
            }
        """)
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(36, 28, 36, 28)  # Aumenta margens
        main_layout.setSpacing(56)  # Espaço maior entre grupos

        # PID Form Section
        pid_group = QGroupBox("Parâmetros do Controle PID")
        pid_group.setStyleSheet("""
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
        pid_form = QFormLayout()
        pid_form.setContentsMargins(12, 30, 12, 12)
        pid_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        pid_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        pid_form.setSpacing(16)  # Espaço maior entre linhas

        self.kp_input = QLineEdit()
        self.kp_input.setPlaceholderText("Ganho Proporcional")
        self.kp_input.setFixedWidth(120)
        pid_form.addRow("Kp:", self.kp_input)

        self.ki_input = QLineEdit()
        self.ki_input.setPlaceholderText("Ganho Integral")
        self.ki_input.setFixedWidth(120)
        pid_form.addRow("Ki:", self.ki_input)

        self.kd_input = QLineEdit()
        self.kd_input.setPlaceholderText("Ganho Derivativo")
        self.kd_input.setFixedWidth(120)
        pid_form.addRow("Kd:", self.kd_input)

        self.setpoint_input = QLineEdit()
        self.setpoint_input.setPlaceholderText("Ponto Inicial")
        self.setpoint_input.setFixedWidth(120)
        pid_form.addRow("Ponto Inicial:", self.setpoint_input)

        self.endpoint_input = QLineEdit()
        self.endpoint_input.setPlaceholderText("Ponto Final")
        self.endpoint_input.setFixedWidth(120)
        pid_form.addRow("Ponto Final:", self.endpoint_input)

        # Extra: tempo de simulação
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("Tempo (s)")
        self.time_input.setFixedWidth(120)
        pid_form.addRow("Tempo Simulação:", self.time_input)

        # Simulate button centralizado
        simulate_button = QPushButton("Simular Controle PID")
        simulate_button.setStyleSheet("""
            QPushButton {
                background-color: #006400;
                color: white;
                border-radius: 6px;
                padding: 8px 22px;
                font-size: 15px;
                font-weight: bold;
                margin-top: 12px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #228B22;
            }
        """)
        # Centraliza o botão usando um layout auxiliar
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(simulate_button)
        btn_row.addStretch(1)
        pid_form.addRow("", btn_row)

        pid_group.setLayout(pid_form)
        main_layout.addWidget(pid_group, stretch=1)

        # PID Graph Section
        graph_section = QVBoxLayout()
        graph_section.setSpacing(24)  # Espaço maior entre widgets

        graph_placeholder = QLabel()
        graph_placeholder.setStyleSheet("""
            background-color: #eaeaea;
            border: 2px solid #bbb;
            border-radius: 12px;
        """)
        graph_placeholder.setFixedSize(700, 400)  # Tamanho maior
        graph_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        graph_placeholder.setText("Visualização do Gráfico PID")
        graph_section.addWidget(graph_placeholder)

        main_layout.addSpacing(24)
        main_layout.addLayout(graph_section, stretch=2)

        # Add main container to the page
        self.add_widget(main_container)