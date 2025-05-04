from ui.pages.objects.pageObjects import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import cv2

class VSEntryDataPage(BasicPage):
    def __init__(self):
        super().__init__("Sistema de Visão: Configuração de Entrada de Dados", QIcon("src/assets/USB.png"))

        self._camera_cap = None  # Se usar cv2.VideoCapture, armazene aqui

        # Explicação
        explanation_label = QLabel(
            "Configure as entradas de dados para o sistema de visão: fonte, resolução, FPS, codec e caminho do arquivo."
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
        main_container.setObjectName("entryMainContainer")
        main_container.setStyleSheet("""
            #entryMainContainer {
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
        main_layout.setContentsMargins(40, 20, 40, 20)
        main_layout.setSpacing(18)

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
        self.img_path_label = QLabel("Nenhum arquivo selecionado")
        self.img_path_label.setStyleSheet("font-size: 13px; color: #555; background: #fff; border: 1px solid #ddd; border-radius: 4px; padding: 4px 8px;")
        self.img_path_label.setMinimumWidth(220)
        self.img_btn = QPushButton("Selecionar")
        self.img_btn.setFixedWidth(90)
        self.img_btn.setStyleSheet("""
            QPushButton {
                background-color: #14532d;
                color: white;
                border-radius: 5px;
                padding: 4px 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #22c55e;
                color: #222;
            }
        """)
        self.img_row.addWidget(self.img_label)
        self.img_row.addWidget(self.img_path_label)
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
        self.cam_row.addWidget(self.cam_label)
        self.cam_row.addWidget(self.cam_combo)
        self.cam_row.addStretch(1)
        main_layout.addLayout(self.cam_row)

        # Caminho do vídeo
        self.vid_row = QHBoxLayout()
        self.vid_label = QLabel("Arquivo de Vídeo:")
        self.vid_label.setMinimumWidth(120)
        self.vid_label.setStyleSheet("font-size: 13px; color: #222; background: none;")
        self.vid_path_label = QLabel("Nenhum arquivo selecionado")
        self.vid_path_label.setStyleSheet("font-size: 13px; color: #555; background: #fff; border: 1px solid #ddd; border-radius: 4px; padding: 4px 8px;")
        self.vid_path_label.setMinimumWidth(220)
        self.vid_btn = QPushButton("Selecionar")
        self.vid_btn.setFixedWidth(90)
        self.vid_btn.setStyleSheet("""
            QPushButton {
                background-color: #14532d;
                color: white;
                border-radius: 5px;
                padding: 4px 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #22c55e;
                color: #222;
            }
        """)
        self.vid_row.addWidget(self.vid_label)
        self.vid_row.addWidget(self.vid_path_label)
        self.vid_row.addWidget(self.vid_btn)
        self.vid_row.addStretch(1)
        main_layout.addLayout(self.vid_row)

        # Atualiza campos conforme fonte de dados
        def update_fields():
            mode = self.data_source_input.currentText()
            self.img_btn.setEnabled(mode == "Imagem")
            self.img_path_label.setEnabled(mode == "Imagem")
            self.cam_combo.setEnabled(mode == "Câmera")
            self.vid_btn.setEnabled(mode == "Vídeo")
            self.vid_path_label.setEnabled(mode == "Vídeo")
        self.data_source_input.currentIndexChanged.connect(update_fields)

        # Selecionar imagem
        def select_img():
            file, _ = QFileDialog.getOpenFileName(main_container, "Selecionar Imagem", filter="Imagens (*.png *.jpg *.jpeg *.bmp)")
            if file:
                self.img_path_label.setText(file)
            else:
                self.img_path_label.setText("Nenhum arquivo selecionado")
        self.img_btn.clicked.connect(select_img)

        # Selecionar vídeo
        def select_vid():
            file, _ = QFileDialog.getOpenFileName(main_container, "Selecionar Arquivo de Vídeo", filter="Vídeos (*.mp4 *.avi *.mov *.mkv)")
            if file:
                self.vid_path_label.setText(file)
            else:
                self.vid_path_label.setText("Nenhum arquivo selecionado")
        self.vid_btn.clicked.connect(select_vid)

        # Listar câmeras disponíveis
        def list_cameras():
            self.cam_combo.clear()
            max_tested = 6
            found = False
            for i in range(max_tested):
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW if hasattr(cv2, 'CAP_DSHOW') else 0)
                if cap is not None and cap.isOpened():
                    # Tenta pegar nome amigável (nem sempre disponível)
                    name = f"Câmera {i}"
                    self.cam_combo.addItem(name)
                    found = True
                    cap.release()
            if not found:
                self.cam_combo.addItem("Nenhuma câmera encontrada")
        list_cameras()

        update_fields()

        self.add_widget(main_container)

    def destroy(self):
        # Libera câmera se aberta
        if hasattr(self, '_camera_cap') and self._camera_cap is not None:
            try:
                self._camera_cap.release()
            except Exception:
                pass
            self._camera_cap = None
        # ...adicione outras limpezas se necessário...