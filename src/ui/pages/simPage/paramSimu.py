from ui.mainWindow.MainWindows import *
import os
import json

class ParamSimuPage(BasicPage):
    def __init__(self,log_manager: LogManager = None):
        super().__init__("Parâmetros de Simulação", QIcon("src/assets/simulation.png"), log_manager)
        # Explicação
        explanation_label = QLabel(
            "Configure FPS, tempo de partida, velocidade da simulação, atrito, restituição, modo debug e logs."
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

        # Main container com estilo similar ao configRobots
        main_container = QWidget()
        main_container.setObjectName("simuParamMainContainer")
        main_container.setStyleSheet("""
            #simuParamMainContainer {
                background: #ffffff;
                border: 1.5px solid #e0e0e0;
                border-radius: 16px;
                padding: 24px;
            }
        """)
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(48)

        # ----------- LADO ESQUERDO -----------
        left_column = QVBoxLayout()
        left_column.setSpacing(28)

        # Grupo Parâmetros Gerais
        general_group = QGroupBox("Parâmetros Gerais da Simulação")
        general_group.setStyleSheet("""
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
        """)
        general_layout = QFormLayout()
        general_layout.setContentsMargins(12, 30, 12, 12)
        general_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        general_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        general_layout.setSpacing(12)

        self.fps_input = QSpinBox()
        self.fps_input.setRange(1, 240)
        self.fps_input.setSuffix(" fps")
        self.fps_input.setFixedWidth(80)
        general_layout.addRow("FPS:", self.fps_input)

        self.time_input = QDoubleSpinBox()
        self.time_input.setRange(1.0, 3600.0)
        self.time_input.setSingleStep(1.0)
        self.time_input.setSuffix(" s")
        self.time_input.setFixedWidth(80)
        general_layout.addRow("Tempo de Partida:", self.time_input)

        self.speed_input = QDoubleSpinBox()
        self.speed_input.setRange(0.1, 10.0)
        self.speed_input.setSingleStep(0.1)
        self.speed_input.setFixedWidth(80)
        general_layout.addRow("Velocidade Simulação:", self.speed_input)

        self.debug_checkbox = QCheckBox("Modo Debug Ativado")
        self.debug_checkbox.setFixedWidth(140)
        general_layout.addRow("", self.debug_checkbox)

        self.logs_checkbox = QCheckBox("Ativar Logs")
        self.logs_checkbox.setFixedWidth(140)
        general_layout.addRow("", self.logs_checkbox)

        general_group.setLayout(general_layout)
        left_column.addWidget(general_group)
        left_column.addStretch(1)

        # ----------- LADO DIREITO -----------
        right_column = QVBoxLayout()
        right_column.setSpacing(28)

        # Grupo Atrito
        friction_group = QGroupBox("Coeficientes de Atrito")
        friction_group.setStyleSheet("""
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
        """)
        friction_layout = QFormLayout()
        friction_layout.setContentsMargins(12, 30, 12, 12)
        friction_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        friction_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        friction_layout.setSpacing(12)
        self.friction_rr = QDoubleSpinBox(); self.friction_rr.setRange(0, 10); self.friction_rr.setSingleStep(0.01); self.friction_rr.setFixedWidth(80)
        self.friction_rf = QDoubleSpinBox(); self.friction_rf.setRange(0, 10); self.friction_rf.setSingleStep(0.01); self.friction_rf.setFixedWidth(80)
        self.friction_rw = QDoubleSpinBox(); self.friction_rw.setRange(0, 10); self.friction_rw.setSingleStep(0.01); self.friction_rw.setFixedWidth(80)
        self.friction_br = QDoubleSpinBox(); self.friction_br.setRange(0, 10); self.friction_br.setSingleStep(0.01); self.friction_br.setFixedWidth(80)
        friction_layout.addRow("Robô-Robô:", self.friction_rr)
        friction_layout.addRow("Robô-Campo:", self.friction_rf)
        friction_layout.addRow("Robô-Paredes:", self.friction_rw)
        friction_layout.addRow("Bola-Robô:", self.friction_br)
        friction_group.setLayout(friction_layout)
        right_column.addWidget(friction_group)

        # Grupo Restituição
        restitution_group = QGroupBox("Coeficientes de Restituição")
        restitution_group.setStyleSheet("""
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
        """)
        restitution_layout = QFormLayout()
        restitution_layout.setContentsMargins(12, 30, 12, 12)
        restitution_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        restitution_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        restitution_layout.setSpacing(12)
        self.restitution_rb = QDoubleSpinBox(); self.restitution_rb.setRange(0, 1); self.restitution_rb.setSingleStep(0.01); self.restitution_rb.setFixedWidth(80)
        self.restitution_rr = QDoubleSpinBox(); self.restitution_rr.setRange(0, 1); self.restitution_rr.setSingleStep(0.01); self.restitution_rr.setFixedWidth(80)
        self.restitution_bf = QDoubleSpinBox(); self.restitution_bf.setRange(0, 1); self.restitution_bf.setSingleStep(0.01); self.restitution_bf.setFixedWidth(80)
        restitution_layout.addRow("Robô-Bola:", self.restitution_rb)
        restitution_layout.addRow("Robô-Robô:", self.restitution_rr)
        restitution_layout.addRow("Bola-Campo:", self.restitution_bf)
        restitution_group.setLayout(restitution_layout)
        right_column.addWidget(restitution_group)

        right_column.addStretch(1)

        # Adiciona as colunas ao layout principal
        main_layout.addLayout(left_column, stretch=1)
        main_layout.addLayout(right_column, stretch=1)

        # Botões (centralizados)
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.save_button = QPushButton("Salvar Configurações")
        self.save_button.setStyleSheet("""
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
        self.restore_button = QPushButton("Restaurar Padrão")
        self.restore_button.setStyleSheet("""
            QPushButton {
                background-color: #b22222;
                color: white;
                border-radius: 6px;
                padding: 10px 28px;
                font-size: 15px;
                font-weight: bold;
                margin-top: 18px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #800000;
            }
        """)
        btn_row.addWidget(self.save_button)
        btn_row.addSpacing(20)
        btn_row.addWidget(self.restore_button)
        right_column.addLayout(btn_row)

        # Adiciona o container principal à página
        self.add_widget(main_container)

        # Conecta botões
        self.save_button.clicked.connect(self.save_params)
        self.restore_button.clicked.connect(self.restore_params)

        # Carrega parâmetros ao abrir
        self.load_params()
    def get_param_path(self):
        return os.path.join("src", "data", "temp", "ParamSimu.json")

    def get_paramR_path(self):
        return os.path.join("src", "data", "temp", "ParamSimuR.json")

    def load_params(self):
        path = self.get_param_path()
        if not os.path.exists(path):
            path = self.get_paramR_path()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.fps_input.setValue(data.get("fps", 60))
            self.time_input.setValue(data.get("tempo_partida", 300.0))
            self.speed_input.setValue(data.get("velocidade_simulacao", 1.0))
            self.friction_rr.setValue(data.get("fric_rr", 0.5))
            self.friction_rf.setValue(data.get("fric_rf", 0.5))
            self.friction_rw.setValue(data.get("fric_rw", 0.5))
            self.friction_br.setValue(data.get("fric_br", 0.5))
            self.restitution_rb.setValue(data.get("rest_rb", 0.7))
            self.restitution_rr.setValue(data.get("rest_rr", 0.7))
            self.restitution_bf.setValue(data.get("rest_bf", 0.7))
            self.debug_checkbox.setChecked(data.get("debug", False))
            self.logs_checkbox.setChecked(data.get("logs", False))

    def save_params(self):
        data = {
            "fps": self.fps_input.value(),
            "tempo_partida": self.time_input.value(),
            "velocidade_simulacao": self.speed_input.value(),
            "fric_rr": self.friction_rr.value(),
            "fric_rf": self.friction_rf.value(),
            "fric_rw": self.friction_rw.value(),
            "fric_br": self.friction_br.value(),
            "rest_rb": self.restitution_rb.value(),
            "rest_rr": self.restitution_rr.value(),
            "rest_bf": self.restitution_bf.value(),
            "debug": self.debug_checkbox.isChecked(),
            "logs": self.logs_checkbox.isChecked()
        }
        with open(self.get_param_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def restore_params(self):
        path = self.get_paramR_path()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.fps_input.setValue(data.get("fps", 60))
            self.time_input.setValue(data.get("tempo_partida", 300.0))
            self.speed_input.setValue(data.get("velocidade_simulacao", 1.0))
            # Correção: o nome correto é friction_br, não friction_rb
            self.friction_br.setValue(data.get("fric_br", 0.5))
            self.friction_rr.setValue(data.get("fric_rr", 0.5))
            self.friction_rf.setValue(data.get("fric_rf", 0.5))
            self.friction_rw.setValue(data.get("fric_rw", 0.5))
            self.restitution_rb.setValue(data.get("rest_rb", 0.7))
            self.restitution_rr.setValue(data.get("rest_rr", 0.7))
            self.restitution_bf.setValue(data.get("rest_bf", 0.7))
            self.debug_checkbox.setChecked(data.get("debug", False))
            self.logs_checkbox.setChecked(data.get("logs", False))