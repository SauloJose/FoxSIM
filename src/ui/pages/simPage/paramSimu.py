from ui.mainWindow.MainWindows import *

class ParamSimuPage(BasicPage):
    def __init__(self):
        super().__init__("Simulador: Parâmetros da Simulação", QIcon("src/assets/control-panel.png"))

        # Explanation section
        explanation_label = QLabel(
            "Configure os parâmetros gerais da simulação, como duração, velocidade e configurações do ambiente."
        )
        explanation_label.setWordWrap(True)
        explanation_label.setStyleSheet("font-size: 12px; margin-bottom: 10px; color: #555;")
        explanation_label.setFixedHeight(50)  # Reduced height
        explanation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_widget(explanation_label)

        # Form layout
        form_layout = QHBoxLayout()
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(20)

        # Left column: General simulation parameters
        left_column = QVBoxLayout()
        left_column.setSpacing(10)
        left_column.addWidget(QLabel("<b>Parâmetros Gerais:</b>"))
        left_column.addWidget(QLabel("Duração da Simulação (s):"))
        duration_input = QSpinBox()
        duration_input.setRange(1, 3600)
        duration_input.setSuffix(" s")
        left_column.addWidget(duration_input)

        left_column.addWidget(QLabel("Velocidade da Simulação (x):"))
        speed_input = QDoubleSpinBox()
        speed_input.setRange(0.1, 10.0)
        speed_input.setSingleStep(0.1)
        speed_input.setSuffix("x")
        left_column.addWidget(speed_input)

        # Right column: Environmental settings
        right_column = QVBoxLayout()
        right_column.setSpacing(10)
        right_column.addWidget(QLabel("<b>Configurações do Ambiente:</b>"))
        right_column.addWidget(QLabel("Dimensão do Campo (m):"))
        field_size_input = QLineEdit()
        field_size_input.setPlaceholderText("Ex: 10x20")
        right_column.addWidget(field_size_input)

        right_column.addWidget(QLabel("Gravidade (m/s²):"))
        gravity_input = QDoubleSpinBox()
        gravity_input.setRange(0.1, 20.0)
        gravity_input.setSingleStep(0.1)
        gravity_input.setSuffix(" m/s²")
        right_column.addWidget(gravity_input)

        # Add a submit button
        submit_button = QPushButton("Salvar Configurações")
        submit_button.setStyleSheet("""
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
        right_column.addWidget(submit_button)

        form_layout.addLayout(left_column)
        form_layout.addLayout(right_column)

        # Add form to the page
        self.add_layout(form_layout)