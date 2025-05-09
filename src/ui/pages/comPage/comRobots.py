from ui.pages.objects.pageObjects import *

class COMrobotPage(BasicPage):
    def __init__(self,log_manager: LogManager = None):
        super().__init__("Comunicação: Robôs", QIcon("src/assets/USB.png"),log_manager)

        # Explanation section
        explanation_label = QLabel(
            "Configure os parâmetros de comunicação dos robôs, como IP, porta, protocolo e taxa de transmissão. "
            "Você pode testar a conexão e salvar as configurações."
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
        explanation_label.setFixedHeight(60)
        explanation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_widget(explanation_label)

        # Main container for shadow/border effect
        main_container = QWidget()
        main_container.setObjectName("comRobotsMainContainer")
        main_container.setStyleSheet("""
            #comRobotsMainContainer {
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
        """)
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(40, 40, 40, 28)  # Aumenta margens
        main_layout.setSpacing(32)  # Espaço maior entre widgets

        # Communication group
        comm_group = QGroupBox("Configuração de Comunicação dos Robôs")
        comm_group.setStyleSheet("""
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
            QWidget { background: #f8f8fa; border-radius: 10px; }
            QComboBox QAbstractItemView {
                selection-background-color: #e0ffe0;
                selection-color: #006400;
            }
            QComboBox {
                selection-background-color: #e0ffe0;
                selection-color: #006400;
            }
        """)
        comm_form = QFormLayout()
        comm_form.setContentsMargins(12, 40, 12, 12)
        comm_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        comm_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        comm_form.setSpacing(16)  # Espaço maior entre linhas

        ip_input = QLineEdit()
        ip_input.setPlaceholderText("Ex: 192.168.0.10")
        ip_input.setFixedWidth(180)
        comm_form.addRow("Endereço IP:", ip_input)

        port_input = QLineEdit()
        port_input.setPlaceholderText("Ex: 5000")
        port_input.setFixedWidth(100)
        comm_form.addRow("Porta:", port_input)

        proto_input = QComboBox()
        proto_input.addItems(["UDP", "TCP", "Serial"])
        proto_input.setFixedWidth(100)
        comm_form.addRow("Protocolo:", proto_input)

        baud_input = QLineEdit()
        baud_input.setPlaceholderText("Ex: 115200")
        baud_input.setFixedWidth(100)
        comm_form.addRow("Baudrate:", baud_input)

        # Substitui ID do Robô por seleção de função
        robot_role_combo = QComboBox()
        robot_role_combo.addItems(["GOLEIRO", "ATACANTE 1", "ATACANTE 2"])
        robot_role_combo.setFixedWidth(140)
        comm_form.addRow("Robô:", robot_role_combo)

        comm_group.setLayout(comm_form)
        main_layout.addWidget(comm_group)

        main_layout.addSpacing(16)

        # Test connection button
        test_btn = QPushButton("Testar Conexão")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #bbb;
                color: #222;
                border-radius: 6px;
                padding: 8px 22px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #888;
                color: white;
            }
        """)
        main_layout.addWidget(test_btn, alignment=Qt.AlignmentFlag.AlignLeft)

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

    def destroy(self):
        # Libere recursos de comunicação, threads, etc.
        pass