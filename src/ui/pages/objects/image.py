from PyQt6.QtGui import QImage, QTransform
from PyQt6.QtCore import QRectF,Qt
from PyQt6.QtGui import QPixmap,QPainter,QColor
import os
import numpy as np

class Image:
    """Classe estilo Pygame para desenho de imagens no SimulatorWidget (QPainter)"""
    def __init__(self, filepath=None, default_scale: float=1.0):
        self._source = None  # QImage
        self._filepath = filepath
        self._current_angle = 0
        self._current_scale = default_scale
        self._flip_x = False
        self._flip_y = False

        if filepath:
            self.load(filepath)

    def is_valid(self):
        return self._source is not None and not self._source.isNull()

    def load(self, filepath):
        if not os.path.exists(filepath):
            print(f"Arquivo não encontrado: {filepath}")
            return False
        img = QImage(filepath)
        if img.isNull():
            print(f"Erro ao carregar imagem: {filepath}")
            self._source = None
            return False
        self._source = img.convertToFormat(QImage.Format.Format_ARGB32)
        self._filepath = filepath
        return True

    @classmethod
    def create_fallback_texture(cls, size=32, color=(255,0,0,255)):
        """Cria uma imagem de fallback programaticamente"""
        try:
            img_data = np.zeros((size, size, 4), dtype=np.uint8)
            img_data[:,:] = color
            img = QImage(img_data.data, size, size, QImage.Format.Format_RGBA8888)
            fallback = cls()
            fallback._source = img.copy()
            return fallback
        except Exception as e:
            print(f"Falha ao criar fallback: {str(e)}")
            return None

    @property
    def width(self):
        return int(self._source.width() * self._current_scale) if self._source else 0

    @property
    def height(self):
        return int(self._source.height() * self._current_scale) if self._source else 0

    @property
    def size(self):
        return (self.width, self.height)

    def copy(self):
        new_img = Image()
        new_img._source = self._source.copy() if self._source else None
        new_img._filepath = self._filepath
        new_img._current_angle = self._current_angle
        new_img._current_scale = self._current_scale
        new_img._flip_x = self._flip_x
        new_img._flip_y = self._flip_y
        return new_img

    def rotate(self, angle):
        rotated = self.copy()
        rotated._current_angle = (self._current_angle + angle) % 360
        return rotated

    def set_rotation(self, angle):
        rotated = self.copy()
        rotated._current_angle = angle % 360
        return rotated

    def scale(self, factor):
        scaled = self.copy()
        scaled._current_scale = self._current_scale * factor
        return scaled

    def set_scale(self, scale):
        scaled = self.copy()
        scaled._current_scale = scale
        return scaled

    def flip(self, x=False, y=False):
        flipped = self.copy()
        flipped._flip_x = x if x is not None else self._flip_x
        flipped._flip_y = y if y is not None else self._flip_y
        return flipped

    def get_size(self):
        """Equivalente ao método do Pygame: retorna (largura, altura)."""
        return self.size

    def get_rect(self, center=None, topleft=None):
        """
        Retorna um retângulo (QRectF) representando a área da imagem.
        Pode ser centralizado ou ter canto superior esquerdo especificado.

        Args:
            center (tuple): (x, y) para centralizar o retângulo.
            topleft (tuple): (x, y) para posicionar o canto superior esquerdo.
        """
        w, h = self.size
        if center:
            x, y = center
            return QRectF(x - w / 2, y - h / 2, w, h)
        elif topleft:
            x, y = topleft
            return QRectF(x, y, w, h)
        else:
            return QRectF(0, 0, w, h)

    def draw(self, x, y, screen, layer=1, alpha=1.0):
        """
        Desenha a imagem no SimulatorWidget (QPainter)
        Args:
            x, y (float): Posição
            screen (SimulatorWidget): Widget de renderização
            layer (int): Camada de desenho
            alpha (float): Transparência (0.0-1.0)
        """
        if not self._source or not hasattr(screen, 'back_buffer'):
            return
        screen.back_buffer.draw_img(
            image_obj=self,
            x=x,
            y=y,
            angle=self._current_angle,
            scale=self._current_scale,
            alpha=alpha,
            layer=layer
        )

    def get_qimage(self):
        """Retorna o QImage transformado (rotação, escala, flip) com suavização máxima"""
        if not self._source:
            return None
        img = self._source

        # Flip
        if self._flip_x or self._flip_y:
            img = img.mirrored(self._flip_x, self._flip_y)

        # Escala com suavização
        if self._current_scale != 1.0:
            img = img.scaled(
                int(img.width() * self._current_scale),
                int(img.height() * self._current_scale),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )


        return img

    # No arquivo image.py, adicione este método à classe Image
    def get_highlighted_copy(self, intensity=100):
        """Retorna uma cópia clareada da imagem"""
        if not self.is_valid():
            return None
            
        # Cria uma QImage com os mesmos dados, mas podemos modificar
        img = self._source.copy()
        
        # Clareia cada pixel
        for x in range(img.width()):
            for y in range(img.height()):
                color = img.pixelColor(x, y)
                if color.alpha() > 0:  # Só modifica pixels visíveis
                    r = min(color.red() + intensity, 255)
                    g = min(color.green() + intensity, 255)
                    b = min(color.blue() + intensity, 255)
                    img.setPixelColor(x, y, QColor(r, g, b, color.alpha()))
        
        # Cria uma nova Image com a versão clareada
        highlighted = Image()
        highlighted._source = img
        highlighted._current_angle = self._current_angle
        highlighted._current_scale = self._current_scale
        highlighted._flip_x = self._flip_x
        highlighted._flip_y = self._flip_y
        return highlighted
    
    def __repr__(self):
        return f"Image('{self._filepath}', size={self.size}, angle={self._current_angle}, scale={self._current_scale})"