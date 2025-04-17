import sys
import numpy as np
import pygame
import cv2
from PIL import Image
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, 
    QLabel, QPushButton, QHBoxLayout, QSplitter, QStackedWidget, QFrame, QStyle,QStyleFactory
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QImage, QPainter,QPixmap

#Classe básica para as paginas
class BasicPage(QWidget):
    '''
        Classe básica para representar as páginas do sistema
    '''
    def __init__(self, page_name: str, icon: QIcon = None):
        super().__init__()

        # Layout principal da página
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Indicador de página no topo
        indicator = QFrame()
        indicator.setFixedHeight(60)
        indicator.setStyleSheet("background-color: white; border-bottom: 2px solid #cccccc;")

        indicator_layout = QHBoxLayout(indicator)
        indicator_layout.setContentsMargins(10, 0, 0, 0)
        indicator_layout.setSpacing(10)

        # Ícone opcional
        if icon:
            icon_label = QLabel()
            icon_label.setPixmap(icon.pixmap(40, 40))
            indicator_layout.addWidget(icon_label)

        # Nome da página
        label = QLabel(page_name)
        label.setStyleSheet("font-weight: bold; font-size: 18px;")
        indicator_layout.addWidget(label)
        indicator_layout.addStretch()

        # Adiciona o indicador no layout principal
        main_layout.addWidget(indicator)

        # Área em branco para herança/uso posterior
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.addStretch()  # Apenas ocupa espaço, pode ser sobrescrito
        main_layout.addLayout(self.content_layout)


#Classes básicas de Widgets para utilizar na página básica
class BasicViewer(QWidget):
    def __init__(self, width=400, height=300):
        super().__init__()
        self.setFixedSize(width, height)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFixedSize(width, height)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
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



#Renderizador para objetos utilizando o Pygame
class PygameRenderThread(QThread):
    frame_ready = pyqtSignal(np.ndarray)

    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height
        self.running = False

    def run(self):
        pygame.init()
        surface = pygame.Surface((self.width, self.height))
        clock = pygame.time.Clock()
        self.running = True

        while self.running:
            surface.fill((255, 255, 255))
            pygame.draw.circle(surface, (255, 0, 0), (self.width//2, self.height//2), 50)

            buffer = pygame.surfarray.array3d(surface)
            buffer = np.transpose(buffer, (1, 0, 2))
            self.frame_ready.emit(buffer)

            clock.tick(30)  # 30 FPS

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


