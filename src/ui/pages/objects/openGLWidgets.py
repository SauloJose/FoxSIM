import sys
import numpy as np
import cv2
from PIL import Image
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,QSizePolicy, QOpenGLWidget,QGLWidget,
    QLabel, QPushButton, QHBoxLayout, QSplitter, QStackedWidget, QFrame, QStyle,QStyleFactory,QLineEdit,QSlider,QGraphicsView
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QImage, QPainter,QPixmap,QFont,QColor,QPalette

from OpenGL.GL import *
from PIL import Image as PILImage


class Image:
    '''
        Classe responsável pelo carregamento e gerenciamento de texturas OpenGL a partir de imagens.

        Esta classe permite carregar imagens de disco ou objetos PIL e convertê-los em texturas 
        OpenGL, com suporte a transformações como rotação e escala.

        Atributos:
            texture_id (int): Identificador da textura OpenGL.
            width (int): Largura da imagem original.
            height (int): Altura da imagem original.
            scale (float): Fator de escala aplicado à imagem.
            angle (float): Ângulo de rotação da imagem, em graus.

        Métodos:
            load_from_path(image_path): Carrega a imagem a partir de um caminho.
            load_from_pillow(image_obj): Carrega a imagem a partir de um objeto PIL.
            set_scale(scale): Define o fator de escala.
            rotate(angle): Rotaciona a imagem em graus.
            draw(widget, x, y): Desenha a imagem no widget OpenGL especificado.
    '''
    def __init__(self, image_path=None, image_obj=None):
        self.texture_id = None
        self.width = 0
        self.height = 0
        self.scale = 1.0
        self.angle = 0

        if image_path:
            self.load_from_path(image_path)
        elif image_obj:
            self.load_from_pillow(image_obj)

    def load_from_path(self, image_path):
        image = PILImage.open(image_path).convert("RGBA")
        self.load_from_pillow(image)

    def load_from_pillow(self, image_obj):
        image_obj = image_obj.transpose(PILImage.FLIP_TOP_BOTTOM)
        self.image_data = image_obj.tobytes("raw", "RGBA", 0, -1)
        self.width, self.height = image_obj.size

        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, self.image_data)

    def set_scale(self, scale):
        self.scale = scale

    def rotate(self, angle):
        self.angle += angle

    def draw(self, widget, x, y):
        w = int(self.width * self.scale)
        h = int(self.height * self.scale)

        widget.makeCurrent()
        glPushMatrix()
        glTranslatef(x, y, 0)
        glRotatef(self.angle, 0, 0, 1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(-w / 2, -h / 2)
        glTexCoord2f(1, 0); glVertex2f(w / 2, -h / 2)
        glTexCoord2f(1, 1); glVertex2f(w / 2, h / 2)
        glTexCoord2f(0, 1); glVertex2f(-w / 2, h / 2)
        glEnd()

        glPopMatrix()
        widget.doneCurrent()


class GL2DWidget(QOpenGLWidget):
    '''
        Widget baseado em QOpenGLWidget que simula uma superfície de renderização similar ao Pygame,
        permitindo renderização customizada com OpenGL para objetos 2D, incluindo imagens, formas geométricas
        e elementos gráficos simulados.

        Este componente é ideal para sistemas de simulação visual como VSSS, permitindo controle total
        sobre o desenho de elementos com alto desempenho.

        Atributos:
            width (int): Largura do widget.
            height (int): Altura do widget.
            image (Image): Objeto de imagem usado para renderização básica (pode ser substituído).
            timer (QTimer): Timer responsável por atualizar o renderizador a cada frame.

        Métodos:
            initializeGL(): Configura o contexto OpenGL inicial.
            resizeGL(w, h): Ajusta o viewport e a projeção ao redimensionar a janela.
            paintGL(): Método principal de renderização (equivalente ao loop do Pygame).
            draw_rect(x, y, w, h, color, filled=True): Desenha um retângulo.
            draw_line(x1, y1, x2, y2, color, thickness=1): Desenha uma linha.
            draw_circle(x, y, radius, color, filled=True): Desenha um círculo.
            draw_polygon(points, color, filled=True): Desenha um polígono com vértices definidos.
            draw_arrow(x1, y1, x2, y2, color, thickness=1): Desenha uma seta entre dois pontos.
            keyPressEvent(event): Captura eventos de teclado (exemplo de interação).
    '''
    def __init__(self, parent=None, width=None, height=None):
        '''
            Inicializa o widget, define largura e altura, carrega a imagem e configura um timer para atualização.

            Args:
                parent (QWidget): Widget pai.
                width (int): Largura opcional do widget.
                height (int): Altura opcional do widget.
        '''
        super(GL2DWidget, self).__init__(parent)
        if parent is not None and (width is None or height is None):
            parent_size = parent.size()
            self.width = width if width is not None else parent_size.width()
            self.height = height if height is not None else parent_size.height()
        else:
            self.width = width if width is not None else 800
            self.height = height if height is not None else 600

        self.setFixedSize(self.width, self.height)
        self.image = Image(image_path="your_image_path.png")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000 // 60)

    def initializeGL(self):
        '''
            Configurações iniciais do contexto OpenGL: cor de fundo, textura e blending.
        '''
        glClearColor(0.2, 0.2, 0.2, 1.0)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def resizeGL(self, w, h):
        '''
            Redimensiona o viewport OpenGL e define projeção ortográfica baseada na nova largura e altura.

            Args:
                w (int): Nova largura.
                h (int): Nova altura.
        '''
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, h, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        '''
            Função de renderização principal. Limpa o buffer e redesenha a imagem.
        '''
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.image.draw(self, 400, 300)
        glFlush()

    def draw_rect(self, x, y, w, h, color):
        '''
            Desenha um retângulo preenchido com a cor especificada.

            Args:
                x, y (float): Posição do canto superior esquerdo.
                w, h (float): Largura e altura.
                color (tuple): Cor (r, g, b, a).
        '''

        glColor4f(*color)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()

    def draw_line(self, x1, y1, x2, y2, color, width=1):
        '''
            Desenha uma linha entre dois pontos.

            Args:
                x1, y1, x2, y2 (float): Pontos de início e fim.
                color (tuple): Cor (r, g, b, a).
                width (int): Espessura da linha.
        '''
        glLineWidth(width)
        glColor4f(*color)
        glBegin(GL_LINES)
        glVertex2f(x1, y1)
        glVertex2f(x2, y2)
        glEnd()

    def draw_circle(self, x, y, radius, color, segments=32):
        '''
            Desenha um círculo preenchido com vértices em forma de fan.

            Args:
                x, y (float): Centro do círculo.
                radius (float): Raio.
                color (tuple): Cor (r, g, b, a).
                segments (int): Número de segmentos para suavidade.
        '''
        glColor4f(*color)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(x, y)
        for i in range(segments + 1):
            angle = 2.0 * np.pi * i / segments
            dx = radius * np.cos(angle)
            dy = radius * np.sin(angle)
            glVertex2f(x + dx, y + dy)
        glEnd()

    def draw_polygon(self, points, color):
        '''
            Desenha um polígono conectado pelos pontos fornecidos.

            Args:
                points (list): Lista de tuplas (x, y).
                color (tuple): Cor (r, g, b, a).
        '''
        glColor4f(*color)
        glBegin(GL_POLYGON)
        for x, y in points:
            glVertex2f(x, y)
        glEnd()

    def draw_arrow(self, x1, y1, x2, y2, color, width=1):
        '''
            Desenha uma seta entre dois pontos, com cabeça em forma de triângulo.

            Args:
                x1, y1, x2, y2 (float): Ponto inicial e final.
                color (tuple): Cor da seta (r, g, b, a).
                width (int): Espessura da linha.
        '''
        self.draw_line(x1, y1, x2, y2, color, width)
        angle = np.arctan2(y2 - y1, x2 - x1)
        head_length = 10
        head_angle = np.pi / 6

        left_x = x2 - head_length * np.cos(angle - head_angle)
        left_y = y2 - head_length * np.sin(angle - head_angle)
        right_x = x2 - head_length * np.cos(angle + head_angle)
        right_y = y2 - head_length * np.sin(angle + head_angle)

        self.draw_polygon([(x2, y2), (left_x, left_y), (right_x, right_y)], color)

    def keyPressEvent(self, event):
        '''
            Exemplo de interação com o teclado: rotaciona imagem ao pressionar seta para cima/baixo.

            Args:
                event (QKeyEvent): Evento de teclado.
        '''
        if event.key() == Qt.Key_Up:
            self.image.rotate(5)
        elif event.key() == Qt.Key_Down:
            self.image.rotate(-5)
