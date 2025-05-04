from ui.pages.objects.pageObjects import *

class COMSysPage(BasicPage):
    def __init__(self):
        super().__init__("Comunicação: Sistemas", QIcon("src/assets/monitor.png"))

        # Explanation section
        explanation_label = QLabel(
            "Configure os parâmetros de comunicação entre os sistemas internos (Visão, Controle, Simulação). "
            "Defina IP, porta e velocidade de comunicação para cada subsistema."
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

        # Main container
        main_container = QWidget()
        main_container.setObjectName("comSysMainContainer")
        main_container.setStyleSheet("""
            #comSysMainContainer {
                background: #f4f4f7;
                border: 1.5px solid #e0e0e0;
                border-radius: 16px;
                padding: 24px;
            }
        """)
        main_layout = QVBoxLayout(main_container)
        main_layout.setSpacing(36)  # Espaço maior entre grupos

        # Group for Vision System
        vision_group = QGroupBox("Sistema de Visão")
        vision_group.setStyleSheet("""
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
        """)
        vision_form = QFormLayout()
        vision_form.setContentsMargins(12, 30, 12, 12)
        vision_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        vision_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        vision_form.setSpacing(16)  # Espaço maior entre linhas
        vision_ip = QLineEdit(); vision_ip.setPlaceholderText("IP ou Host")
        vision_port = QLineEdit(); vision_port.setPlaceholderText("Porta")
        vision_baud = QLineEdit(); vision_baud.setPlaceholderText("Velocidade (bps)")
        vision_form.addRow("Endereço/IP:", vision_ip)
        vision_form.addRow("Porta:", vision_port)
        vision_form.addRow("Velocidade:", vision_baud)
        vision_group.setLayout(vision_form)
        main_layout.addWidget(vision_group)

        # Group for Control System
        control_group = QGroupBox("Sistema de Controle")
        control_group.setStyleSheet("""
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
        """)
        control_form = QFormLayout()
        control_form.setContentsMargins(12, 30, 12, 12)
        control_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        control_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        control_form.setSpacing(16)
        control_ip = QLineEdit(); control_ip.setPlaceholderText("IP ou Host")
        control_port = QLineEdit(); control_port.setPlaceholderText("Porta")
        control_baud = QLineEdit(); control_baud.setPlaceholderText("Velocidade (bps)")
        control_form.addRow("Endereço/IP:", control_ip)
        control_form.addRow("Porta:", control_port)
        control_form.addRow("Velocidade:", control_baud)
        control_group.setLayout(control_form)
        main_layout.addWidget(control_group)

        # Group for Simulation/Computer Vision System
        sim_group = QGroupBox("Sistema de Simulação / Visão Computacional")
        sim_group.setStyleSheet("""
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
        """)
        sim_form = QFormLayout()
        sim_form.setContentsMargins(12, 30, 12, 12)
        sim_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        sim_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        sim_form.setSpacing(16)
        sim_ip = QLineEdit(); sim_ip.setPlaceholderText("IP ou Host")
        sim_port = QLineEdit(); sim_port.setPlaceholderText("Porta")
        sim_baud = QLineEdit(); sim_baud.setPlaceholderText("Velocidade (bps)")
        sim_form.addRow("Endereço/IP:", sim_ip)
        sim_form.addRow("Porta:", sim_port)
        sim_form.addRow("Velocidade:", sim_baud)
        sim_group.setLayout(sim_form)
        main_layout.addWidget(sim_group)

        # Save button
        save_btn = QPushButton("Salvar Configurações")
        save_btn.setStyleSheet("""
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
        main_layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.add_widget(main_container)