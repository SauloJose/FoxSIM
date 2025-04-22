import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from ui.pages.objects.openGLWidgets import *
from ui.pages.objects.imageGL import Image
import numpy as np
import random

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenGL Robot Renderer")
        self.setGeometry(100, 100, 800, 600)

        self.robot_images = {}
        self.load_failures = []

        # Posicionamento e caminhos dos robôs
        self.ROBOT_POSITIONS = {
            'robot1': (200, 300),
            'robot2': (400, 300)
        }

        self.ROBOT_PATHS = {
            'robot1': "src/assets/ATA1.png",
            'robot2': "src/assets/ATA2.png"
        }

        # Caminho da imagem do campo
        self.FIELD_PATH = "src/assets/field.png"  # Caminho da imagem do campo
        self.field_image = Image(self.FIELD_PATH)
        self.DEBUG_OBJECTS = [
            ('circle', 100, 100, 30, (0, 1, 0, 1)),
            ('rect', 250, 100, 80, 40, (1, 0, 0, 1)),
            ('arrow', 50, 50, 150, 150, (1, 1, 0, 1)),
            ('text', 10, 30, "Bem-vindo!", (1, 1, 1, 1)),
            ('polygon', random.randint(100, 700), random.randint(100, 500), (0, 1, 0, 1))  # Adicionando pentágono verde
        ]

        self.init_ui()
        QTimer.singleShot(100, self.initialize_resources)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        self.status_label = QLabel("Inicializando...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.gl_widget = GL2DWidget(self)
        layout.addWidget(self.gl_widget, 1)

    def initialize_resources(self):
        try:
            if not getattr(self.gl_widget, 'initialized', False):
                QTimer.singleShot(100, self.initialize_resources)
                return

            self.status_label.setText("Carregando imagens...")
            QApplication.processEvents()

            # Carregando as imagens dos robôs
            for name, path in self.ROBOT_PATHS.items():
                img = Image(path)
                if img.is_valid():
                    self.robot_images[name] = img
                else:
                    self.load_failures.append(name)
                    self.robot_images[name] = Image.create_fallback_texture()

            # Carregando a imagem do campo
            self.field_image = Image(self.FIELD_PATH)
            if not self.field_image.is_valid():
                self.load_failures.append("campo")
                self.field_image = Image.create_fallback_texture()

            if self.load_failures:
                self.status_label.setText(f"Com fallback para: {', '.join(self.load_failures)}")
            else:
                self.status_label.setText("Todos recursos carregados!")

            self.setup_scene()

        except Exception as e:
            self.show_error(f"Erro ao carregar recursos: {e}")

    def setup_scene(self):
        try:
            buffer = self.gl_widget.back_buffer
            buffer.clear()

            # Desenhar a imagem do campo
            if self.field_image.is_valid():
                buffer.draw_img(self.field_image, 400, 300, angle=0, scale=1, alpha=1.0)

            # Desenhar os robôs
            for name, (x, y) in self.ROBOT_POSITIONS.items():
                img = self.robot_images.get(name)
                if img:
                    angle = 45 if name == 'robot2' else 0
                    alpha = 1 if name == 'robot2' else 1.0
                    buffer.draw_img(img, x, y, angle=angle, scale=0.45, alpha=alpha)

            # Desenhar objetos de depuração
            for obj in self.DEBUG_OBJECTS:
                tipo, *args = obj
                if tipo == 'circle':
                    buffer.draw_circle(*args)
                elif tipo == 'rect':
                    buffer.draw_rect(*args)
                elif tipo == 'arrow':
                    buffer.draw_arrow(*args)
                elif tipo == 'text':
                    buffer.draw_text(*args)
                elif tipo == 'polygon':  # Desenho do pentágono
                    x, y, color = args
                    points = self.generate_polygon(x, y, 5, 50)  # Gerando um pentágono
                    buffer.draw_polygon(x, y, points, color)  # Passando diretamente

            self.gl_widget.render_frame()

        except Exception as e:
            self.show_error(f"Erro na cena: {e}")

    def generate_polygon(self, x, y, sides, radius):
        """Gera os pontos de um polígono regular dado um número de lados e o raio."""
        points = []
        angle_step = 2 * np.pi / sides
        for i in range(sides):
            angle = i * angle_step
            dx = x + radius * np.cos(angle)
            dy = y + radius * np.sin(angle)
            points.append((dx, dy))
        return points

    def show_error(self, message):
        print("ERRO:", message)
        traceback.print_exc()
        QMessageBox.critical(self, "Erro", message)
        self.status_label.setText(f"Erro: {message}")

    def closeEvent(self, event):
        if hasattr(self, 'robot_images'):
            for img in self.robot_images.values():
                if hasattr(img, 'cleanup'):
                    img.cleanup()
        super().closeEvent(event)

    def showEvent(self, event):
        """Sobrescreve o método show() para garantir que a cena seja configurada ao mostrar a janela."""
        super().showEvent(event)
        self.setup_scene()  # Chama setup_scene sempre que a janela for mostrada

    def focusInEvent(self,event):
        """Método que será chamado quando a janela receber o foco."""
        super().focusInEvent(event)
        self.setup_scene()  # Chama setup_scene quando a janela recebe o foco

    def focusOutEvent(self,event):
        """Método que será chamado quando a janela receber o foco."""
        super().focusOutEvent(event)
        self.status_label.setText("Foco perdido.")

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        win = MainWindow()
        win.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"ERRO FATAL: {e}")
        traceback.print_exc()
        sys.exit(1)
