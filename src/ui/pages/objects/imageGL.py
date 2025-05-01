from PIL import Image as PILImage
from PIL.Image import Transpose
import os 
import numpy as np 


class Image:
    """Classe estilo Pygame para desenho de imagens no GL2DWidget"""
    def __init__(self, filepath=None, default_scale=1.0):
        self._source = None
        self._filepath = filepath
        self._current_angle = 0
        self._current_scale = default_scale
        self._flip_x = False
        self._flip_y = False
        
        if filepath:
            self.load(filepath)

    def is_valid(self):
        return self._source is not None

    def load(self, filepath):
        try:
            if not os.path.exists(filepath):
                print(f"Arquivo não encontrado: {filepath}")
                return False
                
            self._source = PILImage.open(filepath).convert("RGBA")
            self._filepath = filepath

            return True
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")
            self._source = None
            return False

    @classmethod
    def create_fallback_texture(cls, size=32, color=(255,0,0,255)):
        """Cria uma imagem de fallback programaticamente"""
        try:
            img_data = np.zeros((size, size, 4), dtype=np.uint8)
            img_data[:,:] = color
            
            fallback = cls()
            fallback._source = PILImage.fromarray(img_data, 'RGBA')
            return fallback
        except Exception as e:
            print(f"Falha ao criar fallback: {str(e)}")
            return None

    @property
    def width(self):
        """Largura com escala aplicada"""
        return int(self._source.width * self._current_scale) if self._source else 0

    @property
    def height(self):
        """Altura com escala aplicada"""
        return int(self._source.height * self._current_scale) if self._source else 0

    @property
    def size(self):
        """Tamanho (width, height) com escala"""
        return (self.width, self.height)

    def copy(self):
        """Retorna uma cópia idêntica"""
        new_img = Image()
        new_img._source = self._source.copy() if self._source else None
        new_img._filepath = self._filepath
        new_img._current_angle = self._current_angle
        new_img._current_scale = self._current_scale
        new_img._flip_x = self._flip_x
        new_img._flip_y = self._flip_y
        new_img.texture_id = None 
        return new_img

    def rotate(self, angle):
        """
        Rotaciona a imagem (ângulo em graus)
        Retorna uma NOVA instância rotacionada
        """
        rotated = self.copy()
        rotated._current_angle = (self._current_angle + angle) % 360
        return rotated

    def set_rotation(self, angle):
        """
        Define rotação absoluta (ângulo em graus)
        Retorna uma NOVA instância rotacionada
        """
        rotated = self.copy()
        rotated._current_angle = angle % 360
        return rotated

    def scale(self, factor):
        """
        Escala a imagem (fator multiplicativo)
        Retorna uma NOVA instância escalada
        """
        scaled = self.copy()
        scaled._current_scale = self._current_scale * factor
        return scaled

    def set_scale(self, scale):
        """
        Define escala absoluta
        Retorna uma NOVA instância escalada
        """
        scaled = self.copy()
        scaled._current_scale = scale
        return scaled

    def flip(self, x=False, y=False):
        """
        Espelha a imagem
        Retorna uma NOVA instância espelhada
        """
        flipped = self.copy()
        flipped._flip_x = x if x is not None else self._flip_x
        flipped._flip_y = y if y is not None else self._flip_y
        return flipped

    def draw(self, x, y, screen, layer=1, alpha=1.0):
        """
        Desenha a imagem no GL2DWidget (estilo Pygame)
        Args:
            x, y (float): Posição
            screen (GL2DWidget): Widget de renderização
            layer (int): Camada de desenho
            alpha (float): Transparência (0.0-1.0)
        """
        if not self._source or not hasattr(screen, 'back_buffer'):
            return

        # Chama o método draw_img do GL2DWidget com todos os parâmetros
        screen.back_buffer.draw_img(
            image_obj=self,
            x=x,
            y=y,
            angle=self._current_angle,
            scale=self._current_scale,
            alpha=alpha,
            layer=layer
        )

    def _prepare_for_gl(self):
        """Prepara os dados para renderização OpenGL (chamado pelo GL2DWidget)"""
        if not self._source:
            return None

        try:
            img = self._source.copy()
            
            # Aplica rotação
            if self._current_angle != 0:
                img = img.rotate(-self._current_angle, resample=PILImage.BICUBIC, expand=True)
            
            # Aplica escala
            if self._current_scale != 1.0:
                new_size = (int(img.width * self._current_scale), 
                        int(img.height * self._current_scale))
                img = img.resize(new_size, PILImage.LANCZOS)
            
            # Aplica flip
            if self._flip_x or self._flip_y:
                if self._flip_x and self._flip_y:
                    transpose = Transpose.TRANSPOSE
                elif self._flip_x:
                    transpose = Transpose.FLIP_LEFT_RIGHT
                else:
                    transpose = Transpose.FLIP_TOP_BOTTOM
                img = img.transpose(transpose)
            
            # Prepara para OpenGL (flip vertical)
            img = img.transpose(Transpose.FLIP_TOP_BOTTOM)
            return {
                'data': img.tobytes("raw", "RGBA", 0, -1),
                'size': img.size,
                'angle': self._current_angle,
                'scale': self._current_scale,
                'flip': (self._flip_x, self._flip_y)
            }
        except Exception as e:
            print(f"Erro ao preparar imagem para OpenGL: {e}")
            return None 
    
    def __repr__(self):
        return f"Image('{self._filepath}', size={self.size}, angle={self._current_angle}, scale={self._current_scale})"