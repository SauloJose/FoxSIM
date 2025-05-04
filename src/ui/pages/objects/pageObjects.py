import sys
import numpy as np
import cv2
from PIL import Image
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

from OpenGL.GL import *
from PIL import Image

#Classe básica para as paginas
class BasicPage(QWidget):
    def __init__(self, page_name: str, icon: QIcon = None):
        super().__init__()

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background-color: white;")

        # Layout principal da página
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Cabeçalho (indicator)
        indicator = QFrame()
        indicator.setFixedHeight(60)
        indicator.setStyleSheet("background-color: white; border-bottom: 2px solid #cccccc;")

        indicator_layout = QHBoxLayout(indicator)
        indicator_layout.setContentsMargins(10, 0, 0, 0)
        indicator_layout.setSpacing(10)

        if icon:
            icon_label = QLabel()
            icon_label.setPixmap(icon.pixmap(40, 40))
            indicator_layout.addWidget(icon_label)

        label = QLabel(page_name)
        label.setStyleSheet("font-weight: bold; font-size: 18px;")
        indicator_layout.addWidget(label)
        indicator_layout.addStretch()

        main_layout.addWidget(indicator)

        # Widget de conteúdo: herdeiros da classe vão adicionar aqui
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: white;")

        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(10)

        main_layout.addWidget(self.content_widget)

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)

    def add_layout(self, layout):
        container = QWidget()
        container.setLayout(layout)
        self.content_layout.addWidget(container)

    def destroy(self):
        # Método base: pode ser sobrescrito nas subclasses
        pass


#Classes básicas de Widgets para utilizar na página básica
class BasicViewer(QGraphicsView):
    def __init__(self, width=400, height=300):
        super().__init__()
        self.setFixedSize(width, height)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFixedSize(width, height)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.label)

    def show_image(self, image):
        """Aceita QImage, PIL.Image, OpenCV (BGR) ou numpy array (RGB/gray) e exibe."""
        qimg = self._convert_to_qimage(image)
        if qimg:
            pixmap = QPixmap.fromImage(qimg)
            self.label.setPixmap(pixmap)

    def _convert_to_qimage(self, image):
        if isinstance(image, QImage):
            return image

        elif isinstance(image, np.ndarray):
            # Imagem em escala de cinza
            if image.ndim == 2:
                return QImage(image.data, image.shape[1], image.shape[0], QImage.Format_Grayscale8)

            # OpenCV padrão: BGR → precisa converter para RGB
            elif image.ndim == 3 and image.shape[2] == 3:
                if image.dtype != np.uint8:
                    image = image.astype(np.uint8)
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                return QImage(rgb.data, rgb.shape[1], rgb.shape[0], rgb.strides[0], QImage.Format_RGB888)

        elif isinstance(image, Image.Image):
            image = image.convert("RGB")
            data = image.tobytes("raw", "RGB")
            return QImage(data, image.width, image.height, QImage.Format_RGB888)

        return None

    def destroy(self):
        pass


#Viewers especializados
class CameraViewer(BasicViewer):
    '''
        Viewer Especializado para threads
    '''
    def __init__(self, width=400, height=300):
        super().__init__(width, height)

    def update_from_frame(self, image):
        """Chamado por alguma thread externa quando uma nova imagem estiver pronta."""
        self.show_image(image)

    def destroy(self):
        # Libera a câmera se estiver aberta
        if hasattr(self, 'cap') and self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
        # ...adicione outras limpezas se necessário...



