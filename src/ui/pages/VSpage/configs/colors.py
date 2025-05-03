from ui.pages.objects.pageObjects import *


class VSselectColor(BasicPage):
    def __init__(self):
        super().__init__("Sistema de Visão: Identificação de Cores", QIcon("src/assets/control-panel.png"))

        # Explanation section
        explanation_label = QLabel("Identifique cores na imagem capturada pela câmera.")
        explanation_label.setWordWrap(True)
        explanation_label.setStyleSheet("font-size: 12px; color: #555; margin-bottom: 10px;")
        explanation_label.setFixedHeight(50)  # Reduced height
        explanation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_widget(explanation_label)

        # Layout for live feed and color detection
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Live camera feed
        live_feed_frame = QFrame()
        live_feed_frame.setStyleSheet("background-color: black; border: 1px solid gray;")
        live_feed_frame.setFixedSize(400, 300)
        layout.addWidget(live_feed_frame)

        # Color detection panel
        color_panel = QVBoxLayout()
        color_panel.addWidget(QLabel("<b>Cor Detectada:</b>"))
        detected_color_label = QLabel()
        detected_color_label.setStyleSheet("background-color: white; border: 1px solid black;")
        detected_color_label.setFixedSize(100, 100)
        color_panel.addWidget(detected_color_label)

        color_panel.addWidget(QLabel("<b>Código HSL:</b>"))
        hsl_code_label = QLabel("H: 0, S: 0%, L: 0%")
        hsl_code_label.setStyleSheet("font-size: 14px; color: #333;")
        color_panel.addWidget(hsl_code_label)

        layout.addLayout(color_panel)

        self.add_layout(layout)