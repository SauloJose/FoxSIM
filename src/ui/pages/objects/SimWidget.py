import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer, pyqtSignal
from vispy import scene
from vispy.color import Color

# Substitua pelos seus módulos
from ui.pages.objects.imageGL import Image
from ui.pages.objects.backbuffer2D import BackBuffer2D

class SimulatorWidget(QWidget):
    """
    Widget de simulação 2D acelerado por GPU usando VisPy,
    integrado a PyQt6. Mantém backbuffer, camadas, primitivas
    e imagens.
    """
    initialized = pyqtSignal()

    def __init__(self, parent=None, width=800, height=600):
        super().__init__(parent)
        self.setMinimumSize(width, height)

        # Back buffer
        self.back_buffer = BackBuffer2D()

        # Layout para inserir o canvas
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Canvas VisPy
        self.canvas = scene.SceneCanvas(keys='interactive', size=(width, height),
                                        show=True, parent=self)
        layout.addWidget(self.canvas.native)

        # Viewbox 2D
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = scene.PanZoomCamera(aspect=1)
        self.view.camera.set_range(x=(0, width), y=(0, height))

        # Background
        self._background_image = None

        # Timer FPS
        self._fps = 60
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update_frame)
        self.set_FPS(self._fps)

        # Estado
        self.click_position = None

    def set_FPS(self, fps):
        self._fps = fps
        interval = int(1000 / fps)
        self._timer.start(interval)

    def set_background_image(self, image: Image):
        """Define imagem de fundo"""
        if image and image.is_valid():
            self._background_image = image
        else:
            print("Imagem de fundo inválida ou não carregada.")  # Adicione um print para depuração
            self._background_image = None

    def update_frame(self):
        """Atualiza o frame atual"""

        # Desenha background
        if self._background_image:
            arr = self._background_image.get_numpy()
            if arr is not None:
                scene.Image(arr, parent=self.view.scene, method='auto')

        # Desenha primitivas e imagens do back buffer
        for call in sorted(self.back_buffer.get_calls(), key=lambda x: x.layer):
            if call.draw_type == BackBuffer2D.DRAW_PRIMITIVE:
                self._draw_primitive(call)
            elif call.draw_type == BackBuffer2D.DRAW_IMAGE and call.obj.is_valid():
                arr = call.obj.get_numpy()
                if arr is not None:
                    scene.Image(arr, parent=self.view.scene,
                                pos=(call.x, call.y),
                                scale=(call.scale, call.scale))

        self.back_buffer.clear()

    def _draw_primitive(self, call):
        """Desenha primitivas básicas"""
        color = Color(call.color)
        if call.obj == "rect":
            scene.Rectangle(pos=(call.x, call.y),  # Corrigido para passar 'pos' corretamente
                            width=call.scale_x,
                            height=call.scale_y,
                            color=color,
                            parent=self.view.scene)
        elif call.obj == "circle":
            scene.Ellipse(center=(call.x, call.y),
                          radius=(call.radius, call.radius),
                          color=color,
                          parent=self.view.scene)
        elif call.obj == "line":
            scene.Line(np.array([[call.x, call.y], [call.end_x, call.end_y]]),
                       color=color,
                       parent=self.view.scene)
        elif call.obj == "polygon":
            points = np.array(call.points)
            if points.shape[0] >= 3:
                scene.Polygon(pos=points,  # Corrigido para passar 'pos' corretamente
                              color=color,
                              parent=self.view.scene)
        elif call.obj == "arrow":
            # linha principal
            scene.Line(np.array([[call.x, call.y], [call.end_x, call.end_y]]),
                       color=color, parent=self.view.scene)
            # cabeça da seta simples
            dx = call.end_x - call.x
            dy = call.end_y - call.y
            angle = np.arctan2(dy, dx)
            head_len = 10
            head_angle = np.pi / 6
            left = [call.end_x - head_len * np.cos(angle - head_angle),
                    call.end_y - head_len * np.sin(angle - head_angle)]
            right = [call.end_x - head_len * np.cos(angle + head_angle),
                     call.end_y - head_len * np.sin(angle + head_angle)]
            scene.Polygon(pos=np.array([[call.end_x, call.end_y], left, right]),  # Corrigido para passar 'pos' corretamente
                          color=color, parent=self.view.scene)

    def mousePressEvent(self, event):
        pos = event.position() if hasattr(event, "position") else event.pos()
        self.click_position = (int(pos.x()), int(pos.y()))
        print(f"Click registrado em: {self.click_position}")

    def get_click_position(self):
        return self.click_position

    def cleanup(self):
        self._timer.stop()
        self.back_buffer.clear()

    def closeEvent(self, event):
        self.cleanup()
        super().closeEvent(event)

    def flip(self):
        """Força atualização do frame"""
        self.update_frame()