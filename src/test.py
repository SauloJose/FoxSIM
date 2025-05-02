import sys
import numpy as np
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import *
from ui.pages.objects.imageGL import Image
from ui.pages.objects.openGLWidgets import GL2DWidget
from OpenGL.GL import *

# Configure OpenGL context before creating QApplication
format = QSurfaceFormat()
format.setVersion(3, 3)
format.setProfile(QSurfaceFormat.CoreProfile)
format.setSamples(4)  # Enable anti-aliasing
QSurfaceFormat.setDefaultFormat(format)

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("GL2DWidget Test")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        try:
            # Create widget with square aspect ratio for better visualization
            self.gl_widget = GL2DWidget(width=800, height=800)
            self.gl_widget.initialized.connect(self.on_gl_initialized)
            layout.addWidget(self.gl_widget)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create GL2DWidget: {str(e)}")
            sys.exit(1)
        
        self.image = None
        self.angle = 0
        self.timer = None
        self.frame_count = 0
        self.last_time = QTime.currentTime()
    
    def on_gl_initialized(self):
        """Called when OpenGL is ready"""
        if not hasattr(self.gl_widget, '_is_initialized') or not self.gl_widget._is_initialized:
            QMessageBox.warning(self, "Warning", "OpenGL initialization incomplete")
            return
        
        # Debug: Show OpenGL context info
        self.gl_widget.makeCurrent()
        try:
            print("\nOpenGL Information:")
            print("Vendor:", glGetString(GL_VENDOR).decode())
            print("Renderer:", glGetString(GL_RENDERER).decode())
            print("Version:", glGetString(GL_VERSION).decode())
            print("Using framebuffer:", glGetInteger(GL_FRAMEBUFFER_BINDING))
        finally:
            self.gl_widget.doneCurrent()
        
        # Load test image or create fallback
        try:
            self.image = Image("src/assets/ETA1.png")
            if not self.image.is_valid():
                self.image = Image.create_fallback_texture(256, (0, 255, 0, 255))
        except Exception as e:
            print(f"Error loading image: {str(e)}")
            self.image = Image.create_fallback_texture(256, (0, 255, 0, 255))
        
        print("OpenGL initialized successfully")
        self.timer = self.startTimer(16)  # ~60 FPS
        self.draw_scene()
    
    def timerEvent(self, event):
        if event.timerId() == self.timer:
            self.angle = (self.angle + 2) % 360  # Rotate 2 degrees per frame
            self.frame_count += 1
            
            # Calculate FPS every second
            current_time = QTime.currentTime()
            if self.last_time.msecsTo(current_time) >= 1000:
                fps = self.frame_count
                self.setWindowTitle(f"GL2DWidget Test - FPS: {fps}")
                self.frame_count = 0
                self.last_time = current_time
                
            self.draw_scene()
    
    def draw_scene(self):
        if not hasattr(self, 'gl_widget') or not self.gl_widget._is_initialized:
            return
            
        try:
            self.gl_widget.back_buffer.clear()
            
            # Draw grid (less dense)
            for i in range(0, 800, 100):
                self.gl_widget.back_buffer.draw_line(i, 0, i, 800, (0.15, 0.15, 0.15, 1), 1)
                self.gl_widget.back_buffer.draw_line(0, i, 800, i, (0.15, 0.15, 0.15, 1), 1)
            
            # Draw axes
            self.gl_widget.back_buffer.draw_line(0, 400, 800, 400, (1,0,0,0.7), 2)
            self.gl_widget.back_buffer.draw_line(400, 0, 400, 800, (0,1,0,0.7), 2)
            
            # Draw simple rotating quad first (no texture)
            self.gl_widget.back_buffer.draw_rect(
                400, 400,  # position
                150, 150,  # size
                (0.8, 0.2, 0.2, 0.7),
                fill = False 
            )
            
            # Then draw image if loaded
            if self.image and self.image.is_valid():
                self.gl_widget.back_buffer.draw_img(
                    image_obj=self.image,
                    x=400, y=400,
                    angle=self.angle,
                    scale=0.3,
                    alpha=0.8,
                    layer=1
                )
            
            # Draw simple shapes
            self.gl_widget.back_buffer.draw_circle(600, 200, 50, (0,0.5,1,1), 2)
            self.gl_widget.back_buffer.draw_arrow(
                400, 400,
                400 + 150 * np.cos(np.radians(self.angle)),
                400 + 150 * np.sin(np.radians(self.angle)),
                (1,1,0,1), 3
            )
            
            self.gl_widget.render_frame()
        except Exception as e:
            print(f"Rendering error: {str(e)}")
            self.gl_widget._check_gl_error("draw_scene")

    def closeEvent(self, event):
        if hasattr(self, 'timer') and self.timer:
            self.killTimer(self.timer)
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    try:
        window = TestWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(None, "Fatal Error", f"Application error: {str(e)}")
        sys.exit(1)