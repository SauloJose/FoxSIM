import numpy as np
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPointF
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QFontMetrics, QImage, QPen, QBrush
from ui.pages.objects.imageGL import *
from ui.pages.objects.backbuffer2D import *

class SimulatorWidget(QWidget):
    '''
        Widget baseado em QWidget que simula uma superfície de renderização similar ao Pygame,
        permitindo renderização customizada com QPainter para objetos 2D, incluindo imagens, formas geométricas
        e elementos gráficos simulados.
    '''
    initialized = pyqtSignal()

    def __init__(self, parent=None, width=None, height=None):
        super().__init__(parent)
        self.view_width = max(1, width) if width is not None else 800
        self.view_height = max(1, height) if height is not None else 600
        self.setMinimumSize(self.view_width, self.view_height)
        self.back_buffer = BackBuffer2D()
        self.framebuffer = QPixmap(self.view_width, self.view_height)
        self.framebuffer.fill(Qt.GlobalColor.black)
        self.click_position = None
        self._background_image = None

        # Timer para atualização (FPS)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.render_frame)
        self._fps = 60
        self.set_FPS(self._fps)

        # Controle de tempo
        self._running = False
        self._paused = False
        self._elapsed_time = 0
        self._start_time = None

        self.initialized.emit()

    def set_FPS(self, fps):
        self._fps = max(1, int(fps))
        self._timer.setInterval(int(1000 / self._fps))

    def start_timer(self):
        self._running = True
        self._paused = False
        self._elapsed_time = 0
        self._start_time = None
        self._timer.start()

    def pause_timer(self):
        self._paused = True
        self._timer.stop()

    def reset_timer(self):
        self._elapsed_time = 0
        self._start_time = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.framebuffer)
        painter.end()

    def update_widget(self):
        """
        Atualiza o widget, desenhando o framebuffer na tela (semelhante ao flip do pygame).
        """
        self.update()

    def render_frame(self):
        # Redesenha o framebuffer (QPixmap) usando QPainter
        self.framebuffer = QPixmap(self.view_width, self.view_height)
        self.framebuffer.fill(Qt.GlobalColor.black)
        painter = QPainter(self.framebuffer)
        # Desenha a imagem de fundo se existir
        if self._background_image and self._background_image.is_valid():
            bg_img = self._background_image.get_qimage()
            if bg_img:
                painter.drawImage(0, 0, bg_img.scaled(self.view_width, self.view_height))
        # Desenha os demais elementos
        for call in sorted(self.back_buffer.get_calls(), key=lambda x: x.layer):
            try:
                self._process_draw_call(painter, call)
            except Exception as e:
                print(f"Erro ao renderizar: {str(e)}")
                continue
        painter.end()
        self.back_buffer.clear()
        self.update_widget()  # Chama update_widget para desenhar na tela

    def _process_draw_call(self, painter, call):
        if call.draw_type == BackBuffer2D.DRAW_IMAGE:
            if call.obj:
                self._render_image(painter, call.obj, call.x, call.y, call.scale, call.angle, call.alpha)
            else:
                print("[Aviso][_process_draw_call]: DRAW_IMAGE com objeto nulo.")
        elif call.draw_type == BackBuffer2D.DRAW_PRIMITIVE:
            if call.obj == "rect":
                self._render_rect(painter, call.x, call.y, call.scale_x, call.scale_y, call.color, fill=call.fill)
            elif call.obj == "rect_vbo":
                self._render_rect(painter, call.x, call.y, call.scale_x, call.scale_y, call.color, fill=call.fill)
            elif call.obj == "line":
                self._render_line(painter, call.x, call.y, call.end_x, call.end_y, call.color)
            elif call.obj == "circle":
                self._render_circle(painter, call.x, call.y, call.radius, call.color)
            elif call.obj == "polygon":
                self._render_polygon(painter, call.points, call.color)
            elif call.obj == "arrow":
                self._render_arrow(painter, call.x, call.y, call.end_x, call.end_y, call.color)
            else:
                print(f"[Aviso][_process_draw_call]: Objeto de primitiva desconhecido: {call.obj}")
        elif call.draw_type == BackBuffer2D.DRAW_TEXT:
            if isinstance(call.obj, str):
                self._render_text(painter, call.x, call.y, call.obj, call.color)
            else:
                print("[Aviso][_process_draw_call]: DRAW_TEXT com objeto não textual.")
        else:
            print(f"[Aviso][_process_draw_call]: Tipo de draw_call desconhecido: {call.draw_type}")

    # Métodos de renderização usando QPainter
    def _render_rect(self, painter, x, y, w, h, color, thickness=1, fill=False):
        qcolor = QColor.fromRgbF(*color) if color else QColor(255,255,255)
        pen = QPen(qcolor)
        pen.setWidth(thickness)
        painter.setPen(pen)
        if fill:
            painter.setBrush(QBrush(qcolor))
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(int(x), int(y), int(w), int(h))

    def _render_line(self, painter, x1, y1, x2, y2, color, thickness=1):
        qcolor = QColor.fromRgbF(*color) if color else QColor(255,255,255)
        pen = QPen(qcolor)
        pen.setWidth(thickness)
        painter.setPen(pen)
        painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def _render_circle(self, painter, x, y, radius, color, segments=32, thickness=1):
        qcolor = QColor.fromRgbF(*color) if color else QColor(255,255,255)
        pen = QPen(qcolor)
        pen.setWidth(thickness)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(int(x - radius), int(y - radius), int(radius * 2), int(radius * 2))

    def _render_polygon(self, painter, points, color, thickness=1):
        if not points or len(points) < 3:
            return
        qcolor = QColor.fromRgbF(*color) if color else QColor(255,255,255)
        pen = QPen(qcolor)
        pen.setWidth(thickness)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        qpoints = [QPointF(float(px), float(py)) for px, py in points]
        painter.drawPolygon(*qpoints)

    def _render_text(self, painter, x, y, text, color):
        if not text or not color or len(color) < 4:
            return
        qcolor = QColor.fromRgbF(*color)
        painter.setPen(qcolor)
        font = QFont("Arial", 14, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(int(x), int(y), text)

    def _render_arrow(self, painter, x1, y1, x2, y2, color, width=1):
        qcolor = QColor.fromRgbF(*color) if color else QColor(255,255,255)
        pen = QPen(qcolor)
        pen.setWidth(width)
        painter.setPen(pen)
        painter.drawLine(int(x1), int(y1), int(x2, int(y2)))
        # Arrow head
        import math
        angle = math.atan2(y2 - y1, x2 - x1)
        head_len = 10 * width
        head_angle = math.pi / 6
        left_x = x2 - head_len * math.cos(angle - head_angle)
        left_y = y2 - head_len * math.sin(angle - head_angle)
        right_x = x2 - head_len * math.cos(angle + head_angle)
        right_y = y2 - head_len * math.sin(angle + head_angle)
        painter.drawPolygon(
            QPointF(x2, y2),
            QPointF(left_x, left_y),
            QPointF(right_x, right_y)
        )

    def _render_image(self, painter, image_obj: Image, x: float, y: float,
                     scale: float = 1.0, angle: float = 0.0, alpha: float = 1.0):
        if not image_obj or not image_obj.is_valid():
            return
        img = image_obj.get_qimage()
        if img is None:
            return
        painter.save()
        painter.setOpacity(alpha)
        # Centraliza a imagem no ponto (x, y)
        w = img.width()
        h = img.height()
        painter.translate(x, y)
        if angle != 0:
            painter.rotate(angle)
        painter.drawImage(-w // 2, -h // 2, img)
        painter.restore()

    def set_background_image(self, image: Image):
        """
        Define a imagem de fundo (campo) que será desenhada sempre antes dos demais elementos.
        """
        if image and image.is_valid():
            self._background_image = image
        else:
            self._background_image = None

    # Eventos de clique
    def mousePressEvent(self, event):
        pos = event.position() if hasattr(event, "position") else event.pos()
        self.click_position = (int(pos.x()), int(pos.y()))
        print(f"Click registrado em: {self.click_position}")

    def get_click_position(self):
        return self.click_position

    def cleanup(self):
        self._timer.stop()
        self.back_buffer.clear()
        self.framebuffer.fill(Qt.GlobalColor.black)

    def closeEvent(self, event):
        self.cleanup()
        super().closeEvent(event)
