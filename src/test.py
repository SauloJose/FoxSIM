import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QOpenGLWidget
from PyQt5.QtOpenGL import QGLWidget
from PIL import Image
from PyQt5.QtCore import QTimer,Qt 
from PyQt5.QtGui import QImage, QPainter

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.images = []
        self.robots = []  # Lista de robôs
        self.setFixedSize(800, 600)  # Tamanho fixo da janela

    def initializeGL(self):
        glClearColor(0.2, 0.2, 0.2, 1.0)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, h, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Desenha todos os robôs
        for robot in self.robots:
            robot.draw()

        glFlush()

    def load_texture(self, image_path):
        image = Image.open(image_path).convert("RGBA")
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        image_data = image.tobytes("raw", "RGBA", 0, -1)
        width, height = image.size

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, image_data)

        return texture_id, width, height

    def draw_image(self, image_path, x, y, scale=1.0, angle=0):
        texture_id, w, h = self.load_texture(image_path)
        w = int(w * scale)
        h = int(h * scale)

        self.images.append((texture_id, x, y, w, h, angle))
        self.update()  # Atualiza o widget para redesenhar

    def draw_rectangle(self, x, y, width, height, color=(1.0, 1.0, 1.0, 1.0)):
        glColor4f(*color)  # Define a cor do retângulo (RGBA)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()

class Robot:
    def __init__(self, widget, image_path, x, y, scale=1.0, angle_rad=0):
        self.widget = widget
        self.image_path = image_path
        self.x = x
        self.y = y
        self.scale = scale
        self.angle_rad = angle_rad
        self.texture_id, self.img_w, self.img_h = self.widget.load_texture(image_path)

    def draw(self):
        x, y, w, h = self.x, self.y, self.img_w * self.scale, self.img_h * self.scale

        # Aplica a rotação
        glPushMatrix()
        glTranslatef(x + w / 2, y + h / 2, 0)  # Move para o centro da imagem
        glRotatef(np.degrees(self.angle_rad), 0, 0, 1)  # Aplica rotação
        glTranslatef(-(x + w / 2), -(y + h / 2), 0)  # Move de volta para a posição original

        # Desenha a imagem com rotação
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(x, y)
        glTexCoord2f(1, 0); glVertex2f(x + w, y)
        glTexCoord2f(1, 1); glVertex2f(x + w, y + h)
        glTexCoord2f(0, 1); glVertex2f(x, y + h)
        glEnd()

        glPopMatrix()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("OpenGL Robot Renderer")
        self.gl_widget = GLWidget(self)
        self.setCentralWidget(self.gl_widget)

        # Cria robôs após a janela estar pronta e o contexto GL inicializado
        QTimer.singleShot(0, self.load_robots)

    def load_robots(self):
        # Robô 1 normal
        robot1 = Robot(self.gl_widget, "src/assets/ATA1.png", 100, 100)

        # Robô 2 rotacionado 60° e menor
        robot2 = Robot(self.gl_widget, "src/assets/ATA2.png", 300, 200, scale=0.6, angle_rad=np.radians(60))

        self.gl_widget.robots.append(robot1)
        self.gl_widget.robots.append(robot2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
