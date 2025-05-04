from ui.pages.objects.pageObjects import *

class LogPage(BasicPage):
    def __init__(self):
        super().__init__("Logs", QIcon("src/assets/simulation.png"))

        # Explanation section
        explanation_label = QLabel(
            "Visualize e filtre os logs do sistema em tempo real. Utilize os filtros avançados para encontrar eventos específicos."
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

        # Main container
        main_container = QWidget()
        main_container.setObjectName("logMainContainer")
        main_container.setStyleSheet("""
            #logMainContainer {
                background: #f4f4f7;
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
            QSpinBox, QDoubleSpinBox {
                qproperty-buttonSymbols: UpDownArrows;
            }
        """)
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(36)

        # Terminal/logs area
        terminal_group = QGroupBox("Terminal de Logs")
        terminal_group.setStyleSheet("""
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
            QWidget { background: #181818; border-radius: 10px; }
        """)
        terminal_layout = QVBoxLayout()
        terminal_layout.setContentsMargins(12, 30, 12, 12)
        terminal_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        terminal_layout.setSpacing(10)
        terminal_widget = QLabel()
        terminal_widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        terminal_widget.setStyleSheet("""
            background-color: #181818;
            color: #e0e0e0;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px;
            border-radius: 8px;
            padding: 12px;
        """)
        terminal_widget.setMinimumWidth(420)
        terminal_widget.setMinimumHeight(320)
        terminal_widget.setText("Logs do sistema aparecerão aqui...")
        terminal_layout.addWidget(terminal_widget)
        terminal_group.setLayout(terminal_layout)
        main_layout.addWidget(terminal_group, stretch=2)

        # Filtros avançados
        filter_group = QGroupBox("Filtros Avançados")
        filter_group.setStyleSheet("""
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
            QWidget { background: #f8f8fa; border-radius: 10px; }
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
        filter_layout = QFormLayout()
        filter_layout.setContentsMargins(12, 40, 12, 12)
        filter_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        filter_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        filter_layout.setSpacing(30)

        filtro_input = QLineEdit()
        filtro_input.setPlaceholderText("Palavra-chave ou expressão")
        filtro_input.setFixedWidth(180)
        filter_layout.addRow("Filtro de Logs:", filtro_input)

        nivel_input = QComboBox()
        nivel_input.addItems(["Todos", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        nivel_input.setFixedWidth(120)
        filter_layout.addRow("Nível de Log:", nivel_input)

        data_ini_input = QLineEdit()
        data_ini_input.setPlaceholderText("dd/mm/aaaa")
        data_ini_input.setFixedWidth(120)
        filter_layout.addRow("Data Inicial:", data_ini_input)

        data_fim_input = QLineEdit()
        data_fim_input.setPlaceholderText("dd/mm/aaaa")
        data_fim_input.setFixedWidth(120)
        filter_layout.addRow("Data Final:", data_fim_input)

        apply_button = QPushButton("Aplicar Filtro")
        apply_button.setStyleSheet("""
            QPushButton {
                background-color: #006400;
                color: white;
                border-radius: 6px;
                padding: 8px 22px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 12px;
            }
            QPushButton:hover {
                background-color: #228B22;
            }
        """)
        filter_layout.addRow("", apply_button)

        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group, stretch=1)

        # Add main container to the page
        self.add_widget(main_container)

    def destroy(self):
        # Libere threads de log, arquivos, etc.
        pass