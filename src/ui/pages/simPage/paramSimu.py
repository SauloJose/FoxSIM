from ui.mainWindow.MainWindows import *

class ParamSimuPage(BasicPage):
    def __init__(self):
        super().__init__("Parâmetros de Simulação", QIcon("src/assets/simulation.png"))

        # Explanation section
        explanation_label = QLabel(
            "Configure os principais parâmetros do simulador, como FPS, modo de renderização, tempo de simulação, gravidade, resolução, ruído, entre outros."
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

        # Main container for shadow/border effect
        main_container = QWidget()
        main_container.setObjectName("simuParamMainContainer")
        main_container.setStyleSheet("""
            #simuParamMainContainer {
                background: #fff;
                border: 1.5px solid #e0e0e0;
                border-radius: 12px;
                padding: 18px;
            }
        """)
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(40, 20, 40, 20)
        main_layout.setSpacing(22)

        # FPS
        fps_row = QHBoxLayout()
        fps_label = QLabel("<b>FPS:</b>")
        fps_label.setMinimumWidth(160)
        fps_label.setStyleSheet("font-size: 13px; color: #222; background: none;")
        fps_input = QSpinBox()
        fps_input.setRange(1, 240)
        fps_input.setValue(60)
        fps_input.setSuffix(" fps")
        fps_input.setFixedWidth(120)
        fps_row.addWidget(fps_label)
        fps_row.addWidget(fps_input)
        fps_row.addStretch(1)
        main_layout.addLayout(fps_row)

        # Render Mode
        render_row = QHBoxLayout()
        render_label = QLabel("<b>Modo de Renderização:</b>")
        render_label.setMinimumWidth(160)
        render_label.setStyleSheet("font-size: 13px; color: #222; background: none;")
        render_combo = QComboBox()
        render_combo.addItems(["2D", "3D", "Wireframe", "Texturizado"])
        render_combo.setFixedWidth(180)
        render_row.addWidget(render_label)
        render_row.addWidget(render_combo)
        render_row.addStretch(1)
        main_layout.addLayout(render_row)

        # Simulation Time
        time_row = QHBoxLayout()
        time_label = QLabel("<b>Tempo de Simulação:</b>")
        time_label.setMinimumWidth(160)
        time_label.setStyleSheet("font-size: 13px; color: #222; background: none;")
        time_input = QDoubleSpinBox()
        time_input.setRange(0.1, 3600.0)
        time_input.setSingleStep(0.1)
        time_input.setSuffix(" s")
        time_input.setValue(300.0)
        time_input.setFixedWidth(120)
        time_row.addWidget(time_label)
        time_row.addWidget(time_input)
        time_row.addStretch(1)
        main_layout.addLayout(time_row)

        # Gravity
        gravity_row = QHBoxLayout()
        gravity_label = QLabel("<b>Gravidade:</b>")
        gravity_label.setMinimumWidth(160)
        gravity_label.setStyleSheet("font-size: 13px; color: #222; background: none;")
        gravity_input = QDoubleSpinBox()
        gravity_input.setRange(0.0, 20.0)
        gravity_input.setSingleStep(0.1)
        gravity_input.setSuffix(" m/s²")
        gravity_input.setValue(9.8)
        gravity_input.setFixedWidth(120)
        gravity_row.addWidget(gravity_label)
        gravity_row.addWidget(gravity_input)
        gravity_row.addStretch(1)
        main_layout.addLayout(gravity_row)

        # Resolution
        res_row = QHBoxLayout()
        res_label = QLabel("<b>Resolução:</b>")
        res_label.setMinimumWidth(160)
        res_label.setStyleSheet("font-size: 13px; color: #222; background: none;")
        res_combo = QComboBox()
        res_combo.addItems(["800x600", "1280x720", "1920x1080", "2560x1440"])
        res_combo.setFixedWidth(180)
        res_row.addWidget(res_label)
        res_row.addWidget(res_combo)
        res_row.addStretch(1)
        main_layout.addLayout(res_row)

        # Noise
        noise_row = QHBoxLayout()
        noise_label = QLabel("<b>Ruído Sensorial:</b>")
        noise_label.setMinimumWidth(160)
        noise_label.setStyleSheet("font-size: 13px; color: #222; background: none;")
        noise_input = QDoubleSpinBox()
        noise_input.setRange(0.0, 1.0)
        noise_input.setSingleStep(0.01)
        noise_input.setSuffix(" (0-1)")
        noise_input.setValue(0.05)
        noise_input.setFixedWidth(120)
        noise_row.addWidget(noise_label)
        noise_row.addWidget(noise_input)
        noise_row.addStretch(1)
        main_layout.addLayout(noise_row)

        # Physics Engine
        engine_row = QHBoxLayout()
        engine_label = QLabel("<b>Motor de Física:</b>")
        engine_label.setMinimumWidth(160)
        engine_label.setStyleSheet("font-size: 13px; color: #222; background: none;")
        engine_combo = QComboBox()
        engine_combo.addItems(["Padrão", "Box2D", "Bullet", "PhysX"])
        engine_combo.setFixedWidth(180)
        engine_row.addWidget(engine_label)
        engine_row.addWidget(engine_combo)
        engine_row.addStretch(1)
        main_layout.addLayout(engine_row)

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
        main_layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignRight)

        # Add main container to the page
        self.add_widget(main_container)