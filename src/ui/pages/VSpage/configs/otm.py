from ui.pages.objects.pageObjects import *

class VSOtimizationPage(BasicPage):
    def __init__(self,log_manager: LogManager = None):
        super().__init__("Sistema de Visão: Otimização", QIcon("src/assets/control-panel.png"),log_manager)

        # Explanation section
        explanation_label = QLabel(
            "Ajuste os principais parâmetros para otimizar o desempenho do sistema de visão. "
            "Configure filtros, paralelismo, uso de GPU, compressão e outras opções para obter o melhor resultado."
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
        explanation_label.setFixedHeight(120)
        explanation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_widget(explanation_label)

        # Main container for shadow/border effect
        main_container = QWidget()
        main_container.setObjectName("otmMainContainer")
        main_container.setStyleSheet("""
            #otmMainContainer {
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
            QSpinBox, QDoubleSpinBox {
                qproperty-buttonSymbols: UpDownArrows;
            }
        """)
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(40, 20, 40, 20)
        main_layout.setSpacing(22)

        # Paralelismo
        parallel_row = QHBoxLayout()
        parallel_label = QLabel("<b>Paralelismo (Threads):</b>")
        parallel_label.setMinimumWidth(180)
        parallel_label.setStyleSheet("font-size: 13px; color: #222; background: none;")
        parallel_spin = QSpinBox()
        parallel_spin.setRange(1, 32)
        parallel_spin.setValue(4)
        parallel_spin.setFixedWidth(100)
        parallel_row.addWidget(parallel_label)
        parallel_row.addWidget(parallel_spin)
        parallel_row.addStretch(1)
        main_layout.addLayout(parallel_row)

        # Uso de GPU
        gpu_row = QHBoxLayout()
        gpu_label = QLabel("<b>Usar GPU:</b>")
        gpu_label.setMinimumWidth(180)
        gpu_label.setStyleSheet("font-size: 13px; color: #222; background: none;")
        gpu_checkbox = QCheckBox("Ativar aceleração por GPU")
        gpu_row.addWidget(gpu_label)
        gpu_row.addWidget(gpu_checkbox)
        gpu_row.addStretch(1)
        main_layout.addLayout(gpu_row)

        # Compressão de Imagem
        compression_row = QHBoxLayout()
        compression_label = QLabel("<b>Nível de Compressão:</b>")
        compression_label.setMinimumWidth(180)
        compression_label.setStyleSheet("font-size: 13px; color: #222; background: none;")
        compression_slider = QSlider(Qt.Orientation.Horizontal)
        compression_slider.setRange(0, 100)
        compression_slider.setValue(50)
        compression_slider.setFixedWidth(180)
        compression_row.addWidget(compression_label)
        compression_row.addWidget(compression_slider)
        compression_row.addStretch(1)
        main_layout.addLayout(compression_row)

        # Filtro Pré-processamento
        filter_row = QHBoxLayout()
        filter_label = QLabel("<b>Filtro de Pré-processamento:</b>")
        filter_label.setMinimumWidth(180)
        filter_label.setStyleSheet("font-size: 13px; color: #222; background: none;")
        filter_combo = QComboBox()
        filter_combo.addItems(["Nenhum", "Blur", "Sharpen", "Bilateral", "Median"])
        filter_combo.setFixedWidth(180)
        filter_row.addWidget(filter_label)
        filter_row.addWidget(filter_combo)
        filter_row.addStretch(1)
        main_layout.addLayout(filter_row)

        # Tamanho do Lote (Batch)
        batch_row = QHBoxLayout()
        batch_label = QLabel("<b>Tamanho do Lote (Batch):</b>")
        batch_label.setMinimumWidth(180)
        batch_label.setStyleSheet("font-size: 13px; color: #222; background: none;")
        batch_spin = QSpinBox()
        batch_spin.setRange(1, 128)
        batch_spin.setValue(8)
        batch_spin.setFixedWidth(100)
        batch_row.addWidget(batch_label)
        batch_row.addWidget(batch_spin)
        batch_row.addStretch(1)
        main_layout.addLayout(batch_row)

        # Botão de salvar e otimizar
        optimize_button = QPushButton("Aplicar Otimizações")
        optimize_button.setStyleSheet("""
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
        main_layout.addWidget(optimize_button, alignment=Qt.AlignmentFlag.AlignRight)

        # Add main container to the page
        self.add_widget(main_container)

    def destroy(self):
        # Libere threads ou recursos se houver
        pass