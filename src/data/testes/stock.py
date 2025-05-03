import sys
import pygame
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QWindow

class PygameWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)  # Define o tamanho mínimo do widget

        # Inicializa o Pygame
        pygame.init()

        # Cria uma janela Pygame embutida no widget PyQt5
        self.pygame_window = QWindow.fromWinId(self.winId())
        self.screen = pygame.display.set_mode((400, 300), flags=pygame.RESIZABLE)

        # Configura um timer para atualizar o Pygame
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pygame)
        self.timer.start(16)  # Aproximadamente 60 FPS

    def update_pygame(self):
        # Lógica de renderização do Pygame
        self.screen.fill((0, 0, 0))  # Fundo preto
        pygame.draw.circle(self.screen, (255, 0, 0), (200, 150), 50)  # Círculo vermelho
        pygame.display.flip()  # Atualiza a tela

    def closeEvent(self, event):
        # Encerra o Pygame ao fechar o widget
        pygame.quit()
        super().closeEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 + Pygame Integration")

        # Layout principal
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Adiciona o widget Pygame
        self.pygame_widget = PygameWidget(self)
        layout.addWidget(self.pygame_widget)

        self.setCentralWidget(central_widget)
        self.resize(800, 600)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())