from PyQt6.QtGui import QImage
import os
import numpy as np

class Image:
    """Classe estilo Pygame para desenho de imagens no SimulatorWidget (QPainter)"""
    def __init__(self, filepath=None, default_scale=1.0):
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
        """Retorna o QImage transformado (rotação, escala, flip)"""
        if not self._source:
            return None
        img = self._source
        # Flip
        if self._flip_x or self._flip_y:
            img = img.mirrored(self._flip_x, self._flip_y)
        # Escala
        if self._current_scale != 1.0:
            img = img.scaled(
                int(img.width() * self._current_scale),
                int(img.height() * self._current_scale)
            )
        # Rotação
        if self._current_angle != 0:
            from PyQt6.QtGui import QTransform
            transform = QTransform().rotate(self._current_angle)
            img = img.transformed(transform)
        return img

    def __repr__(self):
        return f"Image('{self._filepath}', size={self.size}, angle={self._current_angle}, scale={self._current_scale})"