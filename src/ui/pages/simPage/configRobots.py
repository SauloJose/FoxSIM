from ui.mainWindow.MainWindows import *

class ConfigRobotsPage(BasicPage):
    def __init__(self):
        super().__init__("Simulador: Configuração dos Robôs", QIcon("src/assets/robot.png"))

        # Explanation section
        explanation_label = QLabel(
            "Configure os parâmetros físicos dos robôs e as configurações dos times, como massa, tamanho, velocidade e cores."
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

        # Left column: Physical parameters
        left_column = QVBoxLayout()
        left_column.setSpacing(10)
        left_column.addWidget(QLabel("<b>Parâmetros Físicos:</b>"))
        left_column.addWidget(QLabel("Massa (kg):"))
        mass_input = QDoubleSpinBox()
        mass_input.setRange(0.1, 100.0)
        mass_input.setSingleStep(0.1)
        mass_input.setSuffix(" kg")
        left_column.addWidget(mass_input)

        left_column.addWidget(QLabel("Tamanho (cm):"))
        size_input = QSpinBox()
        size_input.setRange(1, 100)
        size_input.setSuffix(" cm")
        left_column.addWidget(size_input)

        left_column.addWidget(QLabel("Velocidade Máxima (cm/s):"))
        speed_input = QSpinBox()
        speed_input.setRange(1, 500)
        speed_input.setSuffix(" cm/s")
        left_column.addWidget(speed_input)

        # Right column: Team configurations
        right_column = QVBoxLayout()
        right_column.setSpacing(10)
        right_column.addWidget(QLabel("<b>Configurações dos Times:</b>"))
        right_column.addWidget(QLabel("Cor do Time A (HSL):"))
        team_a_color_input = QLineEdit()
        team_a_color_input.setPlaceholderText("Ex: 120, 100%, 50%")
        right_column.addWidget(team_a_color_input)

        right_column.addWidget(QLabel("Cor do Time B (HSL):"))
        team_b_color_input = QLineEdit()
        team_b_color_input.setPlaceholderText("Ex: 240, 100%, 50%")
        right_column.addWidget(team_b_color_input)

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
        right_column.addWidget(save_button)

        form_layout.addLayout(left_column)
        form_layout.addLayout(right_column)

        # Add form to the page
        self.add_layout(form_layout)