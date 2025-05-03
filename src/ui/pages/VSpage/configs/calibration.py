from ui.pages.objects.pageObjects import *


class VSCalibrationPage(BasicPage):
    def __init__(self):
        super().__init__("Sistema de Visão: Calibração", QIcon("src/assets/control-panel.png"))

        # Explanation section
        explanation_label = QLabel("Calibre os parâmetros do sistema de visão para melhor desempenho.")
        explanation_label.setWordWrap(True)
        explanation_label.setStyleSheet("font-size: 12px; color: #555; margin-bottom: 10px;")
        explanation_label.setFixedHeight(50)  # Reduced height
        explanation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_widget(explanation_label)

        # Calibration layout
        calibration_layout = QVBoxLayout()
        calibration_layout.setContentsMargins(20, 20, 20, 20)
        calibration_layout.setSpacing(15)

        calibration_layout.addWidget(QLabel("<b>Brilho:</b>"))
        brightness_slider = QSlider(Qt.Orientation.Horizontal)
        brightness_slider.setRange(0, 100)
        calibration_layout.addWidget(brightness_slider)

        calibration_layout.addWidget(QLabel("<b>Contraste:</b>"))
        contrast_slider = QSlider(Qt.Orientation.Horizontal)
        contrast_slider.setRange(0, 100)
        calibration_layout.addWidget(contrast_slider)

        calibration_layout.addWidget(QLabel("<b>Saturação:</b>"))
        saturation_slider = QSlider(Qt.Orientation.Horizontal)
        saturation_slider.setRange(0, 100)
        calibration_layout.addWidget(saturation_slider)

        # Add a calibrate button
        calibrate_button = QPushButton("Aplicar Calibração")
        calibrate_button.setStyleSheet("""
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
        calibration_layout.addWidget(calibrate_button)

        self.add_layout(calibration_layout)