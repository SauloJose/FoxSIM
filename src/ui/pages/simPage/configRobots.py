from ui.mainWindow.MainWindows import *
import os, json

class ConfigRobotsPage(BasicPage):
    def __init__(self):
        super().__init__("Simulador: Configuração dos Robôs", QIcon("src/assets/robot.png"))

        # Diretório e arquivos de configuração
        self.conf_dir = os.path.join("src", "data", "temp")
        self.conf_file = os.path.join(self.conf_dir, "BotConf.json")
        self.conf_reset_file = os.path.join(self.conf_dir, "BotConfR.json")
        os.makedirs(self.conf_dir, exist_ok=True)

        # Explanation section
        explanation_label = QLabel(
            "Configure os parâmetros físicos dos robôs e da bola, além das configurações dos times e jogadores (massa, tamanho, velocidade, cores, etc)."
        )
        explanation_label.setWordWrap(True)
        explanation_label.setStyleSheet("""
            font-size: 14px; 
            margin-bottom: 18px; 
            color: #444; 
            background: #f8f8f8; 
            border-radius: 8px; 
            padding: 10px 18px;
        """)
        explanation_label.setFixedHeight(60)
        explanation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_widget(explanation_label)

        # Main container with gray background and shadow
        main_container = QWidget()
        main_container.setObjectName("robotConfigMainContainer")
        main_container.setStyleSheet("""
            #robotConfigMainContainer {
                background: #ffffff;
                border: 1.5px solid #e0e0e0;
                border-radius: 16px;
                padding: 24px;
            }
            QComboBox QAbstractItemView {
                selection-background-color: #e0ffe0;
                selection-color: #006400;
            }
            QComboBox {
                selection-background-color: #e0ffe0;
                selection-color: #006400;
            }
        """)
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(48)

        # Left column: Physical parameters
        left_column = QVBoxLayout()
        left_column.setSpacing(28)  # Espaçamento maior entre grupos

        # Sessão Robô
        robot_group = QGroupBox("Parâmetros Físicos do Robô")
        robot_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px; font-weight: bold; color: #228B22;
            }
            QGroupBox::title {
                subcontrol-origin: content;
                subcontrol-position: top left;
                left: 10px;
                top: 4px;
                padding: 0 8px;
                background: transparent;
            }
            QComboBox QAbstractItemView {
                selection-background-color: #e0ffe0;
                selection-color: #006400;
            }
            QComboBox {
                selection-background-color: #e0ffe0;
                selection-color: #006400;
            }
        """)
        robot_layout = QFormLayout()
        robot_layout.setContentsMargins(12, 30, 12, 12)
        robot_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        robot_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        robot_layout.setSpacing(12)  # Espaço entre linhas do formulário
        # Comprimento
        length_input = QDoubleSpinBox()
        length_input.setRange(0.01, 100.0)
        length_input.setSingleStep(0.01)
        length_input.setSuffix(" cm")
        length_input.setFixedWidth(90)
        robot_layout.addRow("Comprimento:", length_input)
        # Massa (incremento 0.01)
        mass_input = QDoubleSpinBox()
        mass_input.setRange(0.01, 100.0)
        mass_input.setSingleStep(0.01)
        mass_input.setSuffix(" kg")
        mass_input.setFixedWidth(90)
        robot_layout.addRow("Massa:", mass_input)
        # Velocidade máxima
        speed_input = QSpinBox()
        speed_input.setRange(1, 500)
        speed_input.setSuffix(" cm/s")
        speed_input.setFixedWidth(90)
        robot_layout.addRow("Velocidade Máx.:", speed_input)
        # Velocidade angular máxima
        ang_speed_input = QDoubleSpinBox()
        ang_speed_input.setRange(0.1, 50.0)
        ang_speed_input.setSingleStep(0.1)
        ang_speed_input.setSuffix(" rad/s")
        ang_speed_input.setFixedWidth(90)
        robot_layout.addRow("Velocidade Angular Máx.:", ang_speed_input)
        robot_group.setLayout(robot_layout)
        left_column.addWidget(robot_group)

        # Sessão Bola
        ball_group = QGroupBox("Parâmetros da Bola")
        ball_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px; font-weight: bold; color: #228B22;
            }
            QGroupBox::title {
                subcontrol-origin: content;
                subcontrol-position: top left;
                left: 10px;
                top: 4px;
                padding: 0 8px;
                background: transparent;
            }
            QComboBox QAbstractItemView {
                selection-background-color: #e0ffe0;
                selection-color: #006400;
            }
            QComboBox {
                selection-background-color: #e0ffe0;
                selection-color: #006400;
            }
        """)
        ball_layout = QFormLayout()
        ball_layout.setContentsMargins(12, 30, 12, 12)  # Margens internas do formulário
        ball_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        ball_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        ball_layout.setSpacing(12)
        # Raio
        radius_input = QDoubleSpinBox()
        radius_input.setRange(0.01, 50.0)
        radius_input.setSingleStep(0.01)
        radius_input.setSuffix(" cm")
        radius_input.setFixedWidth(90)
        ball_layout.addRow("Raio:", radius_input)
        # Massa (incremento 0.01)
        ball_mass_input = QDoubleSpinBox()
        ball_mass_input.setRange(0.01, 1000.0)
        ball_mass_input.setSingleStep(0.01)
        ball_mass_input.setSuffix(" g")
        ball_mass_input.setFixedWidth(90)
        ball_layout.addRow("Massa:", ball_mass_input)
        # Velocidade máxima da bola
        ball_speed_input = QSpinBox()
        ball_speed_input.setRange(1, 1000)
        ball_speed_input.setSuffix(" cm/s")
        ball_speed_input.setFixedWidth(90)
        ball_layout.addRow("Velocidade Máx.:", ball_speed_input)
        ball_group.setLayout(ball_layout)
        left_column.addWidget(ball_group)

        left_column.addStretch(1)

        # Right column: Team configurations
        right_column = QVBoxLayout()
        right_column.setSpacing(28)

        team_group = QGroupBox("Configurações dos Times e Jogadores")
        team_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px; font-weight: bold; color: #228B22;
            }
            QGroupBox::title {
                subcontrol-origin: content;
                subcontrol-position: top left;
                left: 10px;
                top: 4px;
                padding: 0 8px;
                background: transparent;
            }
            QComboBox QAbstractItemView {
                selection-background-color: #e0ffe0;
                selection-color: #006400;
            }
            QComboBox {
                selection-background-color: #e0ffe0;
                selection-color: #006400;
            }
        """)
        team_layout = QVBoxLayout()
        team_layout.setSpacing(18)

        # Time A
        team_a_label = QLabel("<b>Time A</b>")
        team_a_label.setStyleSheet("font-size: 14px; color: #006400; margin-bottom: 4px; background: none;")
        team_layout.addWidget(team_a_label)
        team_a_form = QFormLayout()
        team_a_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        team_a_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        team_a_form.setSpacing(10)
        # Cor do time
        team_a_color_input = QLineEdit()
        team_a_color_input.setPlaceholderText("Ex: 120, 100%, 50%")
        team_a_color_input.setFixedWidth(120)
        team_a_form.addRow("Cor do Time:", team_a_color_input)
        # Goleiro
        goalie_a_input = QLineEdit()
        goalie_a_input.setPlaceholderText("Ex: 60, 100%, 50%")
        goalie_a_input.setFixedWidth(120)
        team_a_form.addRow("Cor Goleiro:", goalie_a_input)
        # Atacantes
        for i in range(1, 3):
            att_input = QLineEdit()
            att_input.setPlaceholderText("Ex: 90, 100%, 50%")
            att_input.setFixedWidth(120)
            team_a_form.addRow(f"Cor Atacante {i}:", att_input)
        team_layout.addLayout(team_a_form)
        team_layout.addSpacing(10)

        # Time B
        team_b_label = QLabel("<b>Time B</b>")
        team_b_label.setStyleSheet("font-size: 14px; color: #003399; margin-top: 10px; margin-bottom: 4px; background: none;")
        team_layout.addWidget(team_b_label)
        team_b_form = QFormLayout()
        team_b_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        team_b_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        team_b_form.setSpacing(10)
        # Cor do time
        team_b_color_input = QLineEdit()
        team_b_color_input.setPlaceholderText("Ex: 240, 100%, 50%")
        team_b_color_input.setFixedWidth(120)
        team_b_form.addRow("Cor do Time:", team_b_color_input)
        # Goleiro
        goalie_b_input = QLineEdit()
        goalie_b_input.setPlaceholderText("Ex: 180, 100%, 50%")
        goalie_b_input.setFixedWidth(120)
        team_b_form.addRow("Cor Goleiro:", goalie_b_input)
        # Atacantes
        for i in range(1, 3):
            att_input = QLineEdit()
            att_input.setPlaceholderText("Ex: 210, 100%, 50%")
            att_input.setFixedWidth(120)
            team_b_form.addRow(f"Cor Atacante {i}:", att_input)
        team_layout.addLayout(team_b_form)

        team_group.setLayout(team_layout)
        right_column.addWidget(team_group)

        # Save button
        save_button = QPushButton("Salvar Configurações")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #006400;
                color: white;
                border-radius: 6px;
                padding: 10px 28px;
                font-size: 15px;
                font-weight: bold;
                margin-top: 18px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #228B22;
            }
        """)

        # Reset button
        reset_button = QPushButton("Resetar Configurações")
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #888;
                color: white;
                border-radius: 6px;
                padding: 10px 28px;
                font-size: 15px;
                font-weight: bold;
                margin-top: 8px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)

        # Adiciona botões à coluna da direita
        right_column.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignRight)
        right_column.addWidget(reset_button, alignment=Qt.AlignmentFlag.AlignRight)

        # Add columns to main layout
        main_layout.addLayout(left_column, stretch=1)
        main_layout.addLayout(right_column, stretch=1)

        # Add main container to the page
        self.add_widget(main_container)

        # Salvar referências dos inputs para uso posterior
        self.length_input = length_input
        self.mass_input = mass_input
        self.speed_input = speed_input
        self.ang_speed_input = ang_speed_input

        # Sessão Bola
        self.radius_input = radius_input
        self.ball_mass_input = ball_mass_input
        self.ball_speed_input = ball_speed_input

        # Sessão Times
        self.team_a_color_input = team_a_color_input
        self.goalie_a_input = goalie_a_input
        self.att_a_inputs = []
        for i in range(1, 3):
            self.att_a_inputs.append(team_a_form.itemAt(i+1, QFormLayout.FieldRole).widget())
        self.team_b_color_input = team_b_color_input
        self.goalie_b_input = goalie_b_input
        self.att_b_inputs = []
        for i in range(1, 3):
            self.att_b_inputs.append(team_b_form.itemAt(i+1, QFormLayout.FieldRole).widget())

        # Conecta sinais dos botões
        save_button.clicked.connect(self.save_config)
        reset_button.clicked.connect(self.reset_config)

        # Carrega configurações iniciais
        self.load_config()

    def load_config(self):
        conf_file = self.conf_file if os.path.exists(self.conf_file) else self.conf_reset_file
        try:
            with open(conf_file, "r") as f:
                data = json.load(f)
        except Exception:
            data = {}

        # Robô
        self.length_input.setValue(int(data.get("robot_length", 8)))
        self.mass_input.setValue(float(data.get("robot_mass", 1.0)))
        self.speed_input.setValue(int(data.get("robot_max_speed", 10)))
        self.ang_speed_input.setValue(float(data.get("robot_max_ang_speed", 5.0)))
        # Bola
        self.radius_input.setValue(int(data.get("ball_radius", 2)))
        self.ball_mass_input.setValue(float(data.get("ball_mass", 45.0)))
        self.ball_speed_input.setValue(int(data.get("ball_max_speed", 50)))
        # Time A
        self.team_a_color_input.setText(data.get("team_a_color", "120, 100%, 50%"))
        self.goalie_a_input.setText(data.get("goalie_a_color", "60, 100%, 50%"))
        att_a_colors = data.get("att_a_colors", ["90, 100%, 50%", "90, 100%, 50%"])
        for i, att_input in enumerate(self.att_a_inputs):
            att_input.setText(att_a_colors[i] if i < len(att_a_colors) else "")
        # Time B
        self.team_b_color_input.setText(data.get("team_b_color", "240, 100%, 50%"))
        self.goalie_b_input.setText(data.get("goalie_b_color", "180, 100%, 50%"))
        att_b_colors = data.get("att_b_colors", ["210, 100%, 50%", "210, 100%, 50%"])
        for i, att_input in enumerate(self.att_b_inputs):
            att_input.setText(att_b_colors[i] if i < len(att_b_colors) else "")

    def save_config(self):
        data = {
            # Robô
            "robot_length": self.length_input.value(),
            "robot_mass": self.mass_input.value(),
            "robot_max_speed": self.speed_input.value(),
            "robot_max_ang_speed": self.ang_speed_input.value(),
            # Bola
            "ball_radius": self.radius_input.value(),
            "ball_mass": self.ball_mass_input.value(),
            "ball_max_speed": self.ball_speed_input.value(),
            # Time A
            "team_a_color": self.team_a_color_input.text(),
            "goalie_a_color": self.goalie_a_input.text(),
            "att_a_colors": [att.text() for att in self.att_a_inputs],
            # Time B
            "team_b_color": self.team_b_color_input.text(),
            "goalie_b_color": self.goalie_b_input.text(),
            "att_b_colors": [att.text() for att in self.att_b_inputs]
        }
        with open(self.conf_file, "w") as f:
            json.dump(data, f, indent=4)

    def reset_config(self):
        if os.path.exists(self.conf_reset_file):
            with open(self.conf_reset_file, "r") as f:
                data = json.load(f)
            with open(self.conf_file, "w") as f2:
                json.dump(data, f2, indent=4)
            self.load_config()

    def destroy(self):
        # Libere recursos se houver
        pass