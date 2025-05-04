from ui.pages.objects.pageObjects import *
from PyQt6.QtWidgets import *

class VSEntryDataPage(BasicPage):
    def __init__(self):
        super().__init__("Sistema de Visão: Configuração de Entrada de Dados", QIcon("src/assets/USB.png"))

        # Explanation section
        explanation_label = QLabel(
            "Configure as entradas de dados para o sistema de visão, incluindo fonte, resolução, FPS, codec e caminho do arquivo."
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

        # Main container for shadow/border effect
        main_container = QWidget()
        main_container.setObjectName("entryMainContainer")
        main_container.setStyleSheet("""
            #entryMainContainer {
                background: #f4f4f7;
                border: 1.5px solid #e0e0e0;
                border-radius: 16px;
                padding: 24px;
            }
        """)
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(40, 20, 40, 20)
        main_layout.setSpacing(22)

        # Fonte de Dados
        source_row = QHBoxLayout()
        source_label = QLabel("Fonte de Dados:")
        source_label.setMinimumWidth(120)
        source_label.setStyleSheet("font-size: 13px; color: #222; background: none;")
        self.data_source_input = QComboBox()
        self.data_source_input.addItems(["Imagem", "Câmera", "Vídeo"])
        self.data_source_input.setFixedWidth(180)
        source_row.addWidget(source_label)
        source_row.addWidget(self.data_source_input)
        source_row.addStretch(1)
        main_layout.addLayout(source_row)

        # Caminho da imagem
        self.img_row = QHBoxLayout()
        self.img_label = QLabel("Arquivo de Imagem:")
        self.img_label.setMinimumWidth(120)
        self.img_label.setStyleSheet("font-size: 13px; color: #222; background: none;")
        self.img_input = QLineEdit()
        self.img_input.setPlaceholderText("Selecione a imagem")
        self.img_input.setFixedWidth(220)
        self.img_btn = QPushButton("Selecionar")
        self.img_btn.setFixedWidth(90)
        self.img_btn.setStyleSheet("""
            QPushButton {
                background-color: #006400;
                color: white;
                border-radius: 5px;
                padding: 4px 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #228B22;
                color: white;
            }
        """)
        self.img_row.addWidget(self.img_label)
        self.img_row.addWidget(self.img_input)
        self.img_row.addWidget(self.img_btn)
        self.img_row.addStretch(1)
        main_layout.addLayout(self.img_row)

        # Seleção de câmera
        self.cam_row = QHBoxLayout()
        self.cam_label = QLabel("Dispositivo de Câmera:")
        self.cam_label.setMinimumWidth(120)
        self.cam_label.setStyleSheet("font-size: 13px; color: #222; background: none;")
        self.cam_combo = QComboBox()
        self.cam_combo.setFixedWidth(220)
        # Exemplo: simula 2 câmeras conectadas
        self.cam_combo.addItems(["Câmera 0 (Webcam)", "Câmera 1 (USB)"])
        self.cam_row.addWidget(self.cam_label)
        self.cam_row.addWidget(self.cam_combo)
        self.cam_row.addStretch(1)
        main_layout.addLayout(self.cam_row)

        # Caminho do vídeo
        self.vid_row = QHBoxLayout()
        self.vid_label = QLabel("Arquivo de Vídeo:")
        self.vid_label.setMinimumWidth(120)
        self.vid_label.setStyleSheet("font-size: 13px; color: #222; background: none;")
        self.vid_input = QLineEdit()
        self.vid_input.setPlaceholderText("Selecione ou informe o caminho")
        self.vid_input.setFixedWidth(220)
        self.vid_btn = QPushButton("Selecionar")
        self.vid_btn.setFixedWidth(90)
        self.vid_btn.setStyleSheet("""
            QPushButton {
                background-color: #006400;
                color: white;
                border-radius: 5px;
                padding: 4px 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #228B22;
                color: white;
            }
        """)
        self.vid_row.addWidget(self.vid_label)
        self.vid_row.addWidget(self.vid_input)
        self.vid_row.addWidget(self.vid_btn)
        self.vid_row.addStretch(1)
        main_layout.addLayout(self.vid_row)

        # Função para atualizar habilitação dos campos
        def update_fields():
            mode = self.data_source_input.currentText()
            self.img_input.setEnabled(mode == "Imagem")
            self.img_btn.setEnabled(mode == "Imagem")
            self.cam_combo.setEnabled(mode == "Câmera")
            self.vid_input.setEnabled(mode == "Vídeo")
            self.vid_btn.setEnabled(mode == "Vídeo")
        self.data_source_input.currentIndexChanged.connect(update_fields)
        update_fields()

        # Lógica para selecionar arquivo de imagem
        def select_img():
            file, _ = QFileDialog.getOpenFileName(main_container, "Selecionar Imagem", filter="Imagens (*.png *.jpg *.jpeg *.bmp)")
            if file:
                self.img_input.setText(file)
        self.img_btn.clicked.connect(select_img)

        # Lógica para selecionar arquivo de vídeo
        def select_vid():
            file, _ = QFileDialog.getOpenFileName(main_container, "Selecionar Arquivo de Vídeo", filter="Vídeos (*.mp4 *.avi *.mov *.mkv)")
            if file:
                self.vid_input.setText(file)
        self.vid_btn.clicked.connect(select_vid)

        # Add main container to the page
        self.add_widget(main_container)