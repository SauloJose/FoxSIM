from ui.mainWindow.MainWindows import *
import os, json
from PIL import Image as PILImage
from PIL import ImageDraw

# Importa a função de geração de imagem do robô


class ConfigRobotsPage(BasicPage):
    def __init__(self,log_manager: LogManager = None):
        super().__init__("Simulador: Configuração dos Robôs", QIcon("src/assets/robot.png"),log_manager)

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

        # --- NOVO: Configuração visual dos times e jogadores ---
        def create_team_config(team_label, team_color_default, player_labels, img_filenames, team_key):
            team_widget = QWidget()
            team_layout = QVBoxLayout(team_widget)
            team_layout.setSpacing(6)
            team_layout.setContentsMargins(0, 0, 0, 0)

            # Linha: Label do time + input cor
            hlayout = QHBoxLayout()
            lbl = QLabel(f"<b>{team_label}</b>")
            lbl.setStyleSheet("font-size: 14px; min-width: 60px;")
            color_input = QLineEdit()
            color_input.setPlaceholderText("#RRGGBB")
            color_input.setFixedWidth(70)
            color_input.setText(team_color_default)

            # Quadradinho de cor ao lado do input
            color_box = QLabel()
            color_box.setFixedSize(15, 15)
            color_box.setStyleSheet(f"background: {team_color_default}; border: 1px solid #ccc;")
            def update_team_color_box(text, box=color_box):
                if len(text) == 7 and text.startswith("#"):
                    box.setStyleSheet(f"background: {text}; border: 1px solid #ccc;")
                else:
                    box.setStyleSheet("background: #ffffff; border: 1px solid #ccc;")
            self.connect_color_picker(color_box, color_input)  # Conecta o clique no quadrado à função de seleção de cor
            color_input.textChanged.connect(update_team_color_box)


            hlayout.addWidget(lbl)
            hlayout.addWidget(color_box)
            hlayout.addWidget(color_input)
            hlayout.addStretch(1)
            team_layout.addLayout(hlayout)

            # Linha: 3 jogadores (colunas verticais)
            players_hlayout = QHBoxLayout()
            players_hlayout.setSpacing(16)
            img_labels, cor1_inputs, cor2_inputs = [], [], []
            for idx, (p_label, fname) in enumerate(zip(player_labels, img_filenames)):
                vbox = QVBoxLayout()
                vbox.setSpacing(10)

                # Label do jogador
                plabel = QLabel(p_label)
                plabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                plabel.setStyleSheet("font-size:13px;")
                vbox.addWidget(plabel, alignment=Qt.AlignmentFlag.AlignHCenter)
                # Imagem
                img = QLabel()
                img.setFixedSize(50,50)
                img.setStyleSheet("background: transparent;")
                img.setAlignment(Qt.AlignmentFlag.AlignCenter)
                img_labels.append(img)
                vbox.addWidget(img, alignment=Qt.AlignmentFlag.AlignHCenter)

                vbox.addSpacing(18)

                # Cor 1
                hbox1 = QHBoxLayout()
                cor1 = QLineEdit()
                cor1.setPlaceholderText("Cor 1")
                cor1.setFixedWidth(60)
                cor1.setAlignment(Qt.AlignmentFlag.AlignCenter)
                color_box1 = QLabel()
                color_box1.setFixedSize(15, 15)
                color_box1.setStyleSheet("background: #ffffff; border: 1px solid #ccc;")
                def update_color_box1(text, box=color_box1):
                    if len(text) == 7 and text.startswith("#"):
                        box.setStyleSheet(f"background: {text}; border: 1px solid #ccc;")
                    else:
                        box.setStyleSheet("background: #ffffff; border: 1px solid #ccc;")
                self.connect_color_picker(color_box1, cor1)  # Conecta o clique no quadrado à função de seleção de cor
                cor1.textChanged.connect(update_color_box1)
                hbox1.addStretch(1)
                hbox1.addWidget(color_box1)
                hbox1.addWidget(cor1)
                hbox1.addStretch(1)
                vbox.addLayout(hbox1)
                cor1_inputs.append(cor1)

                # Cor 2
                hbox2 = QHBoxLayout()
                cor2 = QLineEdit()
                cor2.setPlaceholderText("Cor 2")
                cor2.setFixedWidth(60)
                cor2.setAlignment(Qt.AlignmentFlag.AlignCenter)
                color_box2 = QLabel()
                color_box2.setFixedSize(15, 15)
                color_box2.setStyleSheet("background: #ffffff; border: 1px solid #ccc;")
                def update_color_box2(text, box=color_box2):
                    if len(text) == 7 and text.startswith("#"):
                        box.setStyleSheet(f"background: {text}; border: 1px solid #ccc;")
                    else:
                        box.setStyleSheet("background: #ffffff; border: 1px solid #ccc;")
                self.connect_color_picker(color_box2, cor2)  # Conecta o clique no quadrado à função de seleção de cor
                cor2.textChanged.connect(update_color_box2)
                hbox2.addStretch(1)
                hbox2.addWidget(color_box2)
                hbox2.addWidget(cor2)
                hbox2.addStretch(1)
                vbox.addLayout(hbox2)
                cor2_inputs.append(cor2)

                players_hlayout.addLayout(vbox)
            team_layout.addLayout(players_hlayout)
            return team_widget, color_input, img_labels, cor1_inputs, cor2_inputs

        # --- TIME A ---
        atkA_widget, atkA_color_hex, atkA_imgs, atkA_cor1, atkA_cor2 = create_team_config(
            "Time A", "#1e90ff", ["ATA1", "ATA2", "ATGK"], ["ATK1.png", "ATK2.png", "ATGK.png"], "A"
        )
        # --- TIME B ---
        atkB_widget, atkB_color_hex, atkB_imgs, atkB_cor1, atkB_cor2 = create_team_config(
            "Time B", "#ff3333", ["ETA1", "ETA2", "ETGK"], ["ETA1.png", "ETA2.png", "ETGK.png"], "B"
        )

        # Layout principal da direita (apenas times)
        right_column = QVBoxLayout()
        right_column.setSpacing(24)
        right_column.addWidget(atkA_widget)
        right_column.addWidget(atkB_widget)
        right_column.addStretch(1)

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

        # NOVO: refs para customização visual
        self.atkA_imgs = atkA_imgs
        self.atkA_cor1 = atkA_cor1
        self.atkA_cor2 = atkA_cor2
        self.atkA_color_hex = atkA_color_hex
        self.atkB_imgs = atkB_imgs
        self.atkB_cor1 = atkB_cor1
        self.atkB_cor2 = atkB_cor2
        self.atkB_color_hex = atkB_color_hex

        # Conecta sinais dos botões
        save_button.clicked.connect(self.save_config)
        reset_button.clicked.connect(self.reset_config)

        # Conecta sinais dos inputs de cor para atualizar imagens
        def connect_color_inputs(imgs, cor1s, cor2s, team_color_input, filenames, team):
            for i in range(3):
                cor1s[i].textChanged.connect(lambda _, idx=i: self.update_robot_image(team, idx))
                cor2s[i].textChanged.connect(lambda _, idx=i: self.update_robot_image(team, idx))
            team_color_input.textChanged.connect(lambda: [self.update_robot_image(team, idx) for idx in range(3)])

        connect_color_inputs(self.atkA_imgs, self.atkA_cor1, self.atkA_cor2, self.atkA_color_hex, ["ATK1.png", "ATK2.png", "ATKG.png"], "A")
        connect_color_inputs(self.atkB_imgs, self.atkB_cor1, self.atkB_cor2, self.atkB_color_hex, ["ETA1.png", "ETA2.png", "ETGK.png"], "B")

        # Carrega configurações iniciais
        self.load_config()

    def update_robot_image(self, team, idx):
        # team: "A" ou "B", idx: 0=goleiro, 1=atk1, 2=atk2
        if team == "A":
            imgs = self.atkA_imgs
            cor1s = self.atkA_cor1
            cor2s = self.atkA_cor2
            team_color = self.atkA_color_hex.text() or "#1e90ff"
            filenames = ["ATA1.png", "ATA2.png", "ATGK.png"]
        else:
            imgs = self.atkB_imgs
            cor1s = self.atkB_cor1
            cor2s = self.atkB_cor2
            team_color = self.atkB_color_hex.text() or "#ff3333"
            filenames = ["ETA1.png", "ETA2.png", "ETGK.png"]
        cor1 = cor1s[idx].text() or "#ffcc00"
        cor2 = cor2s[idx].text() or "#ffffff"
        fname = filenames[idx]
        path = os.path.join("src", "assets", fname)
        try:
            # Pega o comprimento do input
            robot_length_cm = self.length_input.value()
            self.gerar_robo_vss_png(team_color, cor1, cor2, x_cm=robot_length_cm, caminho_saida=path)
            # Redimensiona para 50x50
            img_pil = PILImage.open(path).convert("RGBA").resize((50, 50), PILImage.LANCZOS)
            # Exibe no QLabel
            buffer = QBuffer()
            buffer.open(QBuffer.OpenModeFlag.ReadWrite)
            img_pil.save(buffer, format="PNG")
            pix = QPixmap()
            pix.loadFromData(buffer.data())
            imgs[idx].setPixmap(pix)
        except Exception as e:
            imgs[idx].setText("Erro\nna imagem")

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

        # NOVO: Cores e imagens dos robôs customizados
        self.atkA_color_hex.setText(data.get("team_a_color_hex", "#1e90ff"))
        self.atkB_color_hex.setText(data.get("team_b_color_hex", "#ff3333"))
        atkA_colors1 = data.get("atkA_cor1", ["#ffcc00", "#ffcc00", "#ffcc00"])
        atkA_colors2 = data.get("atkA_cor2", ["#ffffff", "#ffffff", "#ffffff"])
        atkB_colors1 = data.get("atkB_cor1", ["#ffcc00", "#ffcc00", "#ffcc00"])
        atkB_colors2 = data.get("atkB_cor2", ["#ffffff", "#ffffff", "#ffffff"])
        for i in range(3):
            self.atkA_cor1[i].setText(atkA_colors1[i] if i < len(atkA_colors1) else "#ffcc00")
            self.atkA_cor2[i].setText(atkA_colors2[i] if i < len(atkA_colors2) else "#ffffff")
            self.atkB_cor1[i].setText(atkB_colors1[i] if i < len(atkB_colors1) else "#ffcc00")
            self.atkB_cor2[i].setText(atkB_colors2[i] if i < len(atkB_colors2) else "#ffffff")
            # Atualiza imagens
            self.update_robot_image("A", i)
            self.update_robot_image("B", i)

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
            # NOVO: Cores customizadas dos robôs
            "team_a_color_hex": self.atkA_color_hex.text(),
            "team_b_color_hex": self.atkB_color_hex.text(),
            "atkA_cor1": [c.text() for c in self.atkA_cor1],
            "atkA_cor2": [c.text() for c in self.atkA_cor2],
            "atkB_cor1": [c.text() for c in self.atkB_cor1],
            "atkB_cor2": [c.text() for c in self.atkB_cor2],
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

    def gerar_robo_vss_png(self, cor_time, cor1, cor2, x_cm=7.5, caminho_saida="robo_vss.png"):
        """
        Gera uma imagem PNG de um robô VSS na escala correta (3.6 px = 1 cm).
        - cor_time: cor do retângulo inferior
        - cor1: cor do quadrado superior esquerdo
        - cor2: cor do quadrado superior direito
        - x_cm: lado do robô em centímetros
        """
        px_por_cm = 3.6
        lado_px = int(round(x_cm * px_por_cm))

        # Proporções fixas do desenho (referência: corpo 100x100, borda 105x105, rodas 10x40)
        prop_corpo = 1.0
        prop_borda = 1.03
        prop_roda_w = 0.1
        prop_roda_h = 0.60
        prop_sup_q = 0.5
        prop_inf_h = 0.5

        # Calcula o espaço extra necessário para as rodas
        roda_w = int(lado_px * prop_roda_w)
        img_size = int(lado_px * prop_borda) + 2 * roda_w + 2  # +2*roda_w para garantir espaço dos dois lados
    
        img = Image.new("RGBA", (img_size, img_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Quadrado preto maior (borda)
        borda_size = int(lado_px * prop_borda)
        borda_x = (img_size - borda_size) // 2
        borda_y = (img_size - borda_size) // 2
        draw.rectangle([borda_x, borda_y, borda_x+borda_size, borda_y+borda_size], fill="#000000")

        # Quadrado principal (corpo)
        quad_size = lado_px
        quad_x = (img_size - quad_size) // 2
        quad_y = (img_size - quad_size) // 2

        # Rodas (proporcionais ao lado)
        roda_w = int(lado_px * prop_roda_w)
        roda_h = int(lado_px * prop_roda_h)
        roda_y = quad_y + (quad_size - roda_h)//2
        # Esquerda
        draw.rectangle([quad_x-roda_w, roda_y, quad_x, roda_y+roda_h], fill="#111111")
        # Direita
        draw.rectangle([quad_x+quad_size, roda_y, quad_x+quad_size+roda_w, roda_y+roda_h], fill="#111111")

        # Quadrados superiores (proporcionais)
        sup_q = int(lado_px * prop_sup_q)
        draw.rectangle([quad_x, quad_y, quad_x+sup_q, quad_y+sup_q], fill=cor1)
        draw.rectangle([quad_x+sup_q, quad_y, quad_x+quad_size, quad_y+sup_q], fill=cor2)

        # Retângulo inferior (proporcional)
        inf_h = int(lado_px * prop_inf_h)
        draw.rectangle([quad_x, quad_y+sup_q, quad_x+quad_size, quad_y+quad_size], fill=cor_time)

        # Gira a imagem 90° no sentido horário
        img = img.rotate(-90, expand=True)
        img.save(caminho_saida)

    def connect_color_picker(self, label, lineedit):
        def open_color_dialog(event):
            color = QColorDialog.getColor()
            if color.isValid():
                hex_color = color.name()
                lineedit.setText(hex_color)
        label.mousePressEvent = open_color_dialog