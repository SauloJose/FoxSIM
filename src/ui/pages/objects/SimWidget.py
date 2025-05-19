import numpy as np
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPointF
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QFontMetrics, QImage, QPen, QBrush
from ui.pages.objects.image import *
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
        if width is not None and height is not None:
            self.view_width = max(1, width)
            self.view_height = max(1, height)
        elif parent is not None and hasattr(parent, "width") and hasattr(parent, "height"):
            # Pega tamanho do parent se possível
            self.view_width = max(1, parent.width())
            self.view_height = max(1, parent.height())
        else:
            self.view_width = int(1.2*645)
            self.view_height = 600
            
        self.setMinimumSize(self.view_width, self.view_height)
        self.back_buffer = BackBuffer2D()
        self.click_position = None
        self._background_image = None

        #Flag para controle de renderização
        self._render_paused = False 
        self._force_next_frame = False 
        self._auto_flip = False 

        # Back e front buffer
        self._needs_flip = False  # Flag para controle de atualização
        self._back_pixmap = QPixmap(self.view_width, self.view_height)  # Backbuffer
        self._front_pixmap = QPixmap(self.view_width, self.height())  # Frontbuffer

        # Gerenciar auto_flip
        self.initialized.emit()

    def set_auto_flip(self, enabled: bool):
        """Define se o flip() é automático após render_frame()"""
        self._auto_flip = enabled

    def request_single_frame(self):
        ''' Força para renderização de um único frame'''
        self._force_next_frame = True 
        self.render_frame()

    # =================== Função principal de desenho
    def render_frame(self):
        """
            Renderiza apenas no backbuffer (QPixmap) sem atualizar a tela.
            A atualização só ocorre quando flip() é chamado
        """        
        self._back_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(self._back_pixmap)
        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.SmoothPixmapTransform 
        )


        try:
            # 1. Desenha o background (se existir)
            if self._background_image and self._background_image.is_valid():
                bg_img = self._background_image.get_qimage()
                if bg_img:
                    # Mantém a proporção e centraliza
                    img_ratio = bg_img.width() / bg_img.height()
                    widget_ratio = self.width() / self.height()
                    
                    if widget_ratio > img_ratio:
                        # Ajusta pela altura
                        scaled_height = self.height()
                        scaled_width = int(scaled_height * img_ratio)
                    else:
                        # Ajusta pela largura
                        scaled_width = self.width()
                        scaled_height = int(scaled_width / img_ratio)
                    
                    x = (self.width() - scaled_width) // 2
                    y = (self.height() - scaled_height) // 2
                    
                    painter.drawImage(
                        x, y,
                        bg_img.scaled(scaled_width, scaled_height,
                                    Qt.AspectRatioMode.KeepAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation)
                    )

            # 2. Processa os draw calls (usando seu método existente)
            if not self._render_paused or self._force_next_frame:
                for call in sorted(self.back_buffer.get_calls(), key=lambda x: x.layer):
                    self._process_draw_call(painter, call)  # Usa seu método existente

            self._needs_flip = True 

        except Exception as e:
            print(f"Erro durante renderização: {str(e)}")
            # Opcional: desenha mensagem de erro no framebuffer
            error_msg = f"Render Error: {str(e)}"
            painter.setPen(QColor(255, 0, 0))
            painter.drawText(10, 30, error_msg)
        finally:
            painter.end()
            self._force_next_frame = False  # Reseta o flag após renderizar
            if not self._force_next_frame:
                self.back_buffer.clear()

        if self._auto_flip: #Flip automático se habilitado
            self.flip()

    def flip(self):
        """
        Atualiza a tela (frontbuffer) com o conteúdo do backbuffer
        """
        if self._needs_flip:
            # Swap buffers
            self._front_pixmap, self._back_pixmap = self._back_pixmap, self._front_pixmap 
            self.update()
            self._needs_flip = False

    def paintEvent(self, event):
        """
        Desenha apenas o frontbuffer na tela
        """
        if not self.isVisible():
            return
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._front_pixmap)
        painter.end()

    # Processo de desenho organizado pela classe 
    def _process_draw_call(self, painter:QPainter, call:DrawCall):
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
    def _render_rect(self, painter:QPainter, x, y, w, h, color, thickness=1, fill=False):
        qcolor = QColor.fromRgbF(*color) if color else QColor(255,255,255)
        pen = QPen(qcolor)
        pen.setWidth(thickness)
        painter.setPen(pen)
        if fill:
            painter.setBrush(QBrush(qcolor))
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(int(x), int(y), int(w), int(h))

    def _render_line(self, painter:QPainter, x1, y1, x2, y2, color, thickness=1):
        qcolor = QColor.fromRgbF(*color) if color else QColor(255,255,255)
        pen = QPen(qcolor)
        pen.setWidth(thickness)
        painter.setPen(pen)
        painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def _render_circle(self, painter:QPainter, x, y, radius, color, segments=32, thickness=1):
        qcolor = QColor.fromRgbF(*color) if color else QColor(255,255,255)
        pen = QPen(qcolor)
        pen.setWidth(thickness)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(int(x - radius), int(y - radius), int(radius * 2), int(radius * 2))

    def _render_polygon(self, painter:QPainter, points, color, thickness=1):
        if not points or len(points) < 3:
            return
        qcolor = QColor.fromRgbF(*color) if color else QColor(255,255,255)
        pen = QPen(qcolor)
        pen.setWidth(thickness)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        qpoints = [QPointF(float(px), float(py)) for px, py in points]
        painter.drawPolygon(*qpoints)

    def _render_text(self, painter:QPainter, x, y, text, color):
        if not text or not color or len(color) < 4:
            return
        qcolor = QColor.fromRgbF(*color)
        painter.setPen(qcolor)
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(int(x), int(y), text)

    def _render_arrow(self, painter:QPainter, x1, y1, x2, y2, color, width=1):
        qcolor = QColor.fromRgbF(*color) if color else QColor(255,255,255)
        pen = QPen(qcolor)
        pen.setWidth(width)
        painter.setPen(pen)
        
        # Desenha a linha principal
        painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        angle = np.arctan2(y2 - y1, x2 - x1)
        head_len = 10 * width
        head_angle = np.pi / 6
        left_x = x2 - head_len * np.cos(angle - head_angle)
        left_y = y2 - head_len * np.sin(angle - head_angle)
        right_x = x2 - head_len * np.cos(angle + head_angle)
        right_y = y2 - head_len * np.sin(angle + head_angle)
        painter.drawPolygon(
            QPointF(x2, y2),
            QPointF(left_x, left_y),
            QPointF(right_x, right_y)
        )

    def _render_image(self, painter:QPainter, image_obj: Image, x: float, y: float,
                     scale: float = 1.0, angle: float = 0.0, alpha: float = 1.0):
        if not image_obj or not image_obj.is_valid():
            return
        img = image_obj.get_qimage()
        if img is None:
            return
        painter.save()
        painter.setOpacity(alpha)
        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.SmoothPixmapTransform
        )
        # Centraliza a imagem no ponto (x, y)
        w = img.width()
        h = img.height()

        #rotacionar no painter
        painter.translate(x, y)
        if angle != 0:
            painter.rotate(-angle)
        
        #Desenho centralizado
        painter.drawImage(-w // 2, -h // 2, img)
        painter.restore()

    # =================== Métodos de configuração =====================================
    def set_background_image(self, image: Image):
        """
        Define a imagem de fundo (campo) que será desenhada sempre antes dos demais elementos.
        Redimensiona a imagem para o tamanho do widget.
        """
        if image and image.is_valid():
            # Não faz cópia nem escala aqui, apenas guarda a imagem original
            self._background_image = image
        else:
            self._background_image = None

    def resizeEvent(self, event):
        # Atualiza view_width/view_height ao redimensionar e força redraw do fundo
        self.view_width = self.width()
        self.view_height = self.height()
        self.render_frame()
        super().resizeEvent(event)
        if not self._auto_flip:
            self.flip()

    # Eventos de clique
    def mousePressEvent(self, event):
        pos = event.position() if hasattr(event, "position") else event.pos()
        self.click_position = (int(pos.x()), int(pos.y()))
        print(f"Click registrado em: {self.click_position}")

    def get_click_position(self):
        return self.click_position

    def cleanup(self):
        self.back_buffer.clear()

    def set_render_paused(self, paused: bool):
        """Habilita ou desabilita a renderização"""
        self._render_paused = paused

    def hideEvent(self, event):
        self.set_render_paused(True)

    def showEvent(self, event):
        self.set_render_paused(False)
    
    def closeEvent(self, event):
        self.cleanup()
        super().closeEvent(event)
