from ui.pages.objects.pageObjects import *

class VSCalibrationPage(BasicPage):
    def __init__(self):
        super().__init__("Sistema de Visão: Calibração", QIcon("src/assets/vision.png"))

        # Explanation section
        explanation_label = QLabel("Ajuste os parâmetros de calibração da câmera para obter a melhor qualidade de imagem.")
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
        main_container.setObjectName("calibMainContainer")
        main_container.setStyleSheet("""
            #calibMainContainer {
                background: #fff;
                border: 1.5px solid #e0e0e0;
                border-radius: 12px;
                padding: 18px;
            }
            QComboBox QAbstractItemView {
                selection-background-color: #e0ffe0;
                selection-color: #006400;
            }
            QComboBox {
                selection-background-color: #e0ffe0;
                selection-color: #006400;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #e0e0e0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #bbb;
                border: 1px solid #888;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
        """)
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(40)

        # Viewer on the left (maior)
        viewer = QLabel("Visualização")
        viewer.setStyleSheet("""
            background-color: #222;
            border: 2px solid #bbb;
            border-radius: 8px;
            color: #eee;
            font-size: 15px;
        """)
        viewer.setFixedSize(640, 480)
        main_layout.addWidget(viewer)

        # Calibration form on the right
        calibration_form = QVBoxLayout()
        calibration_form.setSpacing(10)
        calibration_form.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Sliders for calibration (labels maiores)
        sliders = [
            ("Zoom", 1, 10, 1),
            ("Saturação", 0, 100, 50),
            ("Brilho", 0, 100, 50),
            ("Contraste", 0, 100, 50),
            ("Ganho", 0, 100, 50),
            ("Balanço de Branco", 2000, 9000, 4500),
            ("Nitidez", 0, 100, 50),
            ("Exposição", -10, 10, 0),
            ("Gamma", 1, 10, 5)
        ]
        self.slider_widgets = {}
        for label_text, min_val, max_val, default in sliders:
            label = QLabel(f"<b>{label_text}:</b>")
            label.setStyleSheet("font-size: 13px; color: #222; background: none;")
            label.setFixedWidth(150)  # Aumenta o comprimento do label
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(min_val, max_val)
            slider.setValue(default)
            slider.setFixedWidth(200)
            slider.setMinimumHeight(28)  # Garante altura suficiente
            slider.setStyleSheet("""
                QSlider::groove:horizontal { height: 8px; background: #e0e0e0; border-radius: 4px; }
                QSlider::handle:horizontal { background: #228B22; border: 1px solid #888; width: 18px; margin: -6px 0; border-radius: 9px; }
            """)
            value_label = QLabel(str(default))
            value_label.setFixedWidth(36)
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            slider.valueChanged.connect(lambda v, l=value_label: l.setText(str(v)))
            row = QHBoxLayout()
            row.setSpacing(8)
            row.setContentsMargins(0, 0, 0, 0)
            row.addWidget(label)
            row.addWidget(slider)
            row.addWidget(value_label)
            calibration_form.addLayout(row)
            self.slider_widgets[label_text] = slider

        # ComboBox para modo de foco
        focus_row = QHBoxLayout()
        focus_label = QLabel("<b>Foco:</b>")
        focus_label.setStyleSheet("font-size: 13px; color: #222; background: none;")
        focus_label.setFixedWidth(110)
        focus_combo = QComboBox()
        focus_combo.addItems(["Automático", "Manual"])
        focus_combo.setFixedWidth(120)
        focus_row.addWidget(focus_label)
        focus_row.addWidget(focus_combo)
        calibration_form.addLayout(focus_row)

        # Checkbox para autoexposição
        autoexp_row = QHBoxLayout()
        autoexp_label = QLabel("<b>Autoexposição:</b>")
        autoexp_label.setStyleSheet("font-size: 13px; color: #222; background: none;")
        autoexp_label.setFixedWidth(110)
        autoexp_checkbox = QCheckBox()
        autoexp_row.addWidget(autoexp_label)
        autoexp_row.addWidget(autoexp_checkbox)
        calibration_form.addLayout(autoexp_row)

        calibration_form.addSpacing(10)

        # Save and restore buttons
        btn_row = QHBoxLayout()
        save_button = QPushButton("Aplicar Calibração")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #006400;
                color: white;
                border-radius: 6px;
                padding: 8px 22px;
                font-size: 15px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #228B22;
            }
        """)
        restore_button = QPushButton("Restaurar Padrão")
        restore_button.setStyleSheet("""
            QPushButton {
                background-color: #bbb;
                color: #222;
                border-radius: 6px;
                padding: 8px 22px;
                font-size: 15px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #888;
                color: white;
            }
        """)
        btn_row.addWidget(save_button)
        btn_row.addWidget(restore_button)
        calibration_form.addLayout(btn_row)

        main_layout.addLayout(calibration_form)

        # Add main container to the page
        self.add_widget(main_container)