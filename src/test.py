import sys
import numpy as np
from PyQt5.QtGui import QSurfaceFormat

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import *
from ui.pages.objects.imageGL import Image
from ui.pages.objects.openGLWidgets import GL2DWidget

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Teste GL2DWidget - Corrigido")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Configura o widget OpenGL com tratamento de erros
        try:
            self.gl_widget = GL2DWidget()
            self.gl_widget.initialized.connect(self.on_gl_initialized)
            layout.addWidget(self.gl_widget)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao criar GL2DWidget: {str(e)}")
            sys.exit(1)
        
        # Carrega imagem ou fallback
        try:
            self.image = Image("src/assets/ETA1.png")  # Substitua pelo caminho correto
            if not self.image.is_valid():
                raise FileNotFoundError
        except:
            print("Usando fallback texture...")
            self.image = Image.create_fallback_texture(256, (0, 255, 0, 255))
        
        self.angle = 0
        self.timer = None
    
    def on_gl_initialized(self):
        """Chamado quando o OpenGL está pronto"""
        if not self.gl_widget._is_initialized:
            QMessageBox.warning(self, "Aviso", "Inicialização OpenGL incompleta")
            return
        
        # Inicia a animação somente após o OpenGL estar pronto
        self.timer = self.gl_widget.startTimer(16)  # ~60 FPS
        self.draw_scene()
    
    def timerEvent(self, event):
        if event.timerId() == self.timer:
            self.angle = (self.angle + 1) % 360
            self.draw_scene()
    
    def draw_scene(self):
        if not hasattr(self, 'gl_widget') or not self.gl_widget._is_initialized:
            return
            
        try:
            self.gl_widget.back_buffer.clear()
            
            # Desenha a imagem
            if self.image.is_valid():
                self.gl_widget.back_buffer.draw_img(
                    image_obj=self.image,
                    x=400, y=300,
                    angle=self.angle,
                    scale=0.5,
                    alpha=0.8,
                    layer=1
                )
            
            # Desenha linhas
            self.gl_widget.back_buffer.draw_line(100, 100, 700, 100, (1,0,0,1), 2)
            self.gl_widget.back_buffer.draw_line(100, 100, 100, 500, (0,1,0,1), 2)
            self.gl_widget.back_buffer.draw_line(100, 100, 700, 500, (0,0,1,1), 2)
            
            # Desenha seta
            self.gl_widget.back_buffer.draw_arrow(400, 400, 600, 400, (1,1,0,1), 3)
            
            self.gl_widget.render_frame()
        except Exception as e:
            print(f"Erro ao renderizar: {str(e)}")

    def closeEvent(self, event):
        if hasattr(self, 'timer') and self.timer:
            self.gl_widget.killTimer(self.timer)
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Configuração para melhor compatibilidade OpenGL
    fmt = QSurfaceFormat()
    fmt.setVersion(3, 3)
    fmt.setProfile(QSurfaceFormat.CoreProfile)
    fmt.setSamples(4)
    QSurfaceFormat.setDefaultFormat(fmt)
    
    try:
        window = TestWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(None, "Erro Fatal", f"Erro na aplicação: {str(e)}")
        sys.exit(1)