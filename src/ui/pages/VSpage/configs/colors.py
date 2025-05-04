from ui.pages.objects.pageObjects import *

class VSselectColor(BasicPage):
    def __init__(self):
        super().__init__("Sistema de Visão: Identificação de Cores", QIcon("src/assets/control-panel.png"))

        # Explicação
        explanation_label = QLabel(
            "Escolha uma cor em HSL e visualize sua representação. Veja também o código RGB correspondente. "
            "A esquerda, visualize a imagem da câmera."
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

        # Container principal
        main_container = QWidget()
        main_container.setObjectName("colorMainContainer")
        main_container.setStyleSheet("""
            #colorMainContainer {
                background: #fff;
                border: 1.5px solid #e0e0e0;
                border-radius: 14px;
                padding: 22px;
            }
        """)
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(36, 36, 36, 36)  # Aumenta o topo/bottom
        main_layout.setSpacing(64)  # Espaço maior entre câmera e painel

        # Viewer da câmera (lado esquerdo)
        camera_view = QFrame()
        camera_view.setStyleSheet("""
            background-color: #222;
            border: 2.5px solid #228B22;
            border-radius: 12px;
        """)
        camera_view.setFixedSize(640, 480)
        main_layout.addWidget(camera_view, stretch=2)

        # Painel de seleção de cor (lado direito)
        color_panel = QVBoxLayout()
        color_panel.setSpacing(36)  # Espaçamento maior entre widgets
        color_panel.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Formulário HSL
        form_group = QGroupBox("Selecionar Cor (HSL)")
        form_group.setStyleSheet("""
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
        form_layout = QGridLayout()
        form_layout.setContentsMargins(12, 30, 12, 12)  # Top maior para não sobrepor o título
        form_layout.setHorizontalSpacing(10)
        form_layout.setVerticalSpacing(18)  # Espaço maior entre linhas

        # Sliders para H, S, L
        h_slider = QSlider(Qt.Orientation.Horizontal)
        h_slider.setRange(0, 360)
        h_slider.setValue(0)
        h_slider.setFixedWidth(180)
        h_label = QLabel("0°")
        h_label.setFixedWidth(40)

        s_slider = QSlider(Qt.Orientation.Horizontal)
        s_slider.setRange(0, 100)
        s_slider.setValue(100)
        s_slider.setFixedWidth(180)
        s_label = QLabel("100%")
        s_label.setFixedWidth(40)

        l_slider = QSlider(Qt.Orientation.Horizontal)
        l_slider.setRange(0, 100)
        l_slider.setValue(50)
        l_slider.setFixedWidth(180)
        l_label = QLabel("50%")
        l_label.setFixedWidth(40)

        form_layout.addWidget(QLabel("H (Matiz):"), 0, 0)
        form_layout.addWidget(h_slider, 0, 1)
        form_layout.addWidget(h_label, 0, 2)
        form_layout.addWidget(QLabel("S (Saturação):"), 1, 0)
        form_layout.addWidget(s_slider, 1, 1)
        form_layout.addWidget(s_label, 1, 2)
        form_layout.addWidget(QLabel("L (Luminosidade):"), 2, 0)
        form_layout.addWidget(l_slider, 2, 1)
        form_layout.addWidget(l_label, 2, 2)

        form_group.setLayout(form_layout)
        color_panel.addWidget(form_group)
        color_panel.addSpacing(18)  # Espaço maior após formulário

        # Visualização da cor escolhida
        color_preview = QLabel()
        color_preview.setFixedSize(120, 120)
        color_preview.setStyleSheet("background: #fff; border: 2px solid #888; border-radius: 10px;")
        color_panel.addWidget(color_preview, alignment=Qt.AlignmentFlag.AlignHCenter)
        color_panel.addSpacing(16)

        # Exibir códigos HSL e RGB
        hsl_label = QLabel("HSL: 0°, 100%, 50%")
        hsl_label.setStyleSheet("font-size: 14px; color: #333; margin-top: 8px; background: none;")
        color_panel.addWidget(hsl_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        rgb_label = QLabel("RGB: 255, 0, 0")
        rgb_label.setStyleSheet("font-size: 14px; color: #333; background: none;")
        color_panel.addWidget(rgb_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Atualização dinâmica da cor
        def update_color():
            h = h_slider.value()
            s = s_slider.value()
            l = l_slider.value()
            h_label.setText(f"{h}°")
            s_label.setText(f"{s}%")
            l_label.setText(f"{l}%")
            # Conversão HSL para RGB (0-255)
            import colorsys
            r, g, b = colorsys.hls_to_rgb(h/360, l/100, s/100)
            r, g, b = int(r*255), int(g*255), int(b*255)
            color_preview.setStyleSheet(
                f"background: rgb({r},{g},{b}); border: 2px solid #888; border-radius: 10px;"
            )
            hsl_label.setText(f"HSL: {h}°, {s}%, {l}%")
            rgb_label.setText(f"RGB: {r}, {g}, {b}")

        h_slider.valueChanged.connect(update_color)
        s_slider.valueChanged.connect(update_color)
        l_slider.valueChanged.connect(update_color)
        update_color()

        color_panel.addStretch(1)
        main_layout.addLayout(color_panel, stretch=1)

        # Adiciona o container principal à página
        self.add_widget(main_container)