from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from vispy import scene, app
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VisPy + PyQt6 Example")
        self.resize(640, 480)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Criar canvas VisPy
        self.canvas = scene.SceneCanvas(keys='interactive', show=True)
        layout.addWidget(self.canvas.native)

        # Adicionar uma view
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = 'panzoom'  # ou 'turntable' para 3D

        # Criar uma imagem inicial
        self.image_data = np.random.rand(480, 640, 3).astype(np.float32)
        self.image = scene.visuals.Image(self.image_data, parent=self.view.scene)

        # Criar timer VisPy corretamente
        self.timer = app.Timer(interval=1/60, connect=self.update_image, start=True)

    def update_image(self, event):
        # Atualiza o array da imagem (simulação)
        self.image_data = np.random.rand(480, 640, 3).astype(np.float32)
        self.image.set_data(self.image_data)
        self.canvas.update()

if __name__ == "__main__":
    appQt = QApplication([])
    window = MainWindow()
    window.show()
    app.run()
