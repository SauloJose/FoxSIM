import sys
import time
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer
from ui.pages.objects.SimWidget import SimulatorWidget
from ui.pages.objects.image import Image

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Teste do SimulatorWidget com Image")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.sim_widget = SimulatorWidget(self)
        layout.addWidget(self.sim_widget)
        self.setLayout(layout)

        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_rotation)
        self.img_path = "src/assets/ATA1.png"

        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0

        QTimer.singleShot(100, self.start_loop)

    def start_loop(self):
        if not Image(self.img_path).is_valid():
            print("Falha ao carregar a imagem.")
            return
        self.timer.start(16)  # ~60 FPS

    def update_rotation(self):

        # Gira imagem
        img = Image(self.img_path).rotate(self.angle).scale(0.05)
        img2 = Image(self.img_path).scale(0.05).rotate(self.angle)

        center_x = self.sim_widget.width() // 2
        center_y = self.sim_widget.height() // 2
        cx_2 = center_x
        cy_2 = center_y + 100

        # Desenhar as imagens
        img.draw(center_x, center_y, self.sim_widget)
        img2.draw(cx_2, cy_2, self.sim_widget)

        # === FPS ===
        self.frame_count += 1
        current_time = time.time()
        elapsed = current_time - self.last_time

        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.last_time = current_time

        # Desenhar o texto com o FPS
        self.sim_widget.back_buffer.draw_text(
            10, 20, f"FPS: {self.fps:.1f}",
            color=(0.0, 0.0, 0.0, 1.0),
            layer=self.sim_widget.back_buffer.LAYER_DEBUG
        )

        # Renderizar e exibir
        self.sim_widget.render_frame()
        self.sim_widget.flip()

        # Atualizar ângulo
        self.angle = (self.angle + 5) % 360

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
