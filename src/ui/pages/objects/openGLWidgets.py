import sys
import numpy as np
import cv2
from PIL import Image
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal,QElapsedTimer
from PyQt5.QtGui import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU  import *
import OpenGL 

from PIL import Image as PILImage
from ui.pages.objects.imageGL import *
from ui.pages.objects.backbuffer2D import *


# Classe de renderização principal
class GL2DWidget(QOpenGLWidget):
    '''
        Widget baseado em QOpenGLWidget que simula uma superfície de renderização similar ao Pygame,
        permitindo renderização customizada com OpenGL para objetos 2D, incluindo imagens, formas geométricas
        e elementos gráficos simulados.

        Este componente é ideal para sistemas de simulação visual como VSSS, permitindo controle total
        sobre o desenho de elementos com alto desempenho.

        Atributos:
            width (int): Largura do widget.
            height (int): Altura do widget.
            image (Image): Objeto de imagem usado para renderização básica (pode ser substituído).
            timer (QTimer): Timer responsável por atualizar o renderizador a cada frame.

        Métodos:
            initializeGL(): Configura o contexto OpenGL inicial.
            resizeGL(w, h): Ajusta o viewport e a projeção ao redimensionar a janela.
            paintGL(): Método principal de renderização (equivalente ao loop do Pygame).
            keyPressEvent(event): Captura eventos de teclado (exemplo de interação).
    '''
    def __init__(self, parent=None, width=None, height=None):
        '''
            Inicializa o widget, define largura e altura, carrega a imagem e configura um timer para atualização.

            Args:
                parent (QWidget): Widget pai.
                width (int): Largura opcional do widget.
                height (int): Altura opcional do widget.
        '''
        super(GL2DWidget, self).__init__(parent)
        self.texture_cache = {} #Cache de texturas (ex.: para texto)
        self.texture_cache_size = 0
        self.max_texture_cache_size = 50*1024*1024

        # Definição de tamanhos com base no widget pai ou valores padrões
        self.width = width if width else 800
        self.height = height if height else 600
        self.setMinimumSize(self.width, self.height)

        # back_buffer do Widget
        self.back_buffer = BackBuffer2D()

        # Flags que serão utilizadas para ações de eventos
        self.click_position = None 
        self.initialized = False #Flag de inicialização

        #Recursos do GL
        self.fbo = None 
        self.texture = None 
        self.rbo = None 

    def initializeGL(self):
        '''
            Configurações iniciais do contexto OpenGL: cor de fundo, textura e blending.
        '''
        self._check_gl_error("Pre-initializeGL")

        glClearColor(0.2, 0.2, 0.2, 1.0)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Configura o framebuffer
        self._setup_framebuffer()
        self.initialized = True  # ← Adicionar esta linha
        self._check_gl_error("Post-initializeGL")

    def _setup_framebuffer(self):
        """Configura o framebuffer e seus attachments"""
        # Libera recursos existentes
        self._cleanup_gl_resources()
        
        # Gera novos recursos
        self.fbo = glGenFramebuffers(1)
        self.texture = glGenTextures(1)
        self.rbo = glGenRenderbuffers(1)
        
        # Configura textura
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 
                    0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        # Configura renderbuffer
        glBindRenderbuffer(GL_RENDERBUFFER, self.rbo)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, self.width, self.height)
        
        # Anexa ao FBO
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.texture, 0)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, self.rbo)
        
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError(f"Framebuffer incompleto: {status}")
            
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        self._check_gl_error("_setup_framebuffer")

    def resizeGL(self, w, h):
        device_ratio = self.devicePixelRatio()
        self.width = w
        self.height = h

        glViewport(0, 0, self.width, self.height)
        
        # Atualiza projeção
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, h, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Redimensiona FBO
        self._setup_framebuffer()
        self._check_gl_error("resizeGL")

    def _check_gl_error(self, context):
        error = glGetError()
        if error != GL_NO_ERROR:
            print(f"OpenGL erro em {context}:{error}")

    ## == Método principal de desenho utilizando o open GL
    def paintGL(self):
        if not self.initialized or not self.isValid():
            return

        self.makeCurrent()
        try:
            # Limpa o buffer principal
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            # Renderiza o FBO na tela
            if glIsTexture(self.texture):  # Verifica se a textura ainda existe
                glBindFramebuffer(GL_READ_FRAMEBUFFER, self.fbo)
                glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
                glBlitFramebuffer(0, 0, self.width, self.height,
                                0, 0, self.width, self.height,
                                GL_COLOR_BUFFER_BIT, GL_NEAREST)
                
            glFlush()


        except Exception as e:
            print(f"Erro fatal em paintGL: {str(e)}")
            self.initialized = False 
        
        finally:
            self.back_buffer.clear()  # Limpa as chamadas após desenhar
            self.doneCurrent()

    def render_to_back_buffer(self):
        '''
            Método utilizado para desenhar no back buffer para manter uma metodologia
            de imagem persistente. Que só será desenhado novamento quando chamar update.
        '''
        if not self.initialized:
            return
            
        self.makeCurrent()
        try: 
            # Desenha tudo no FBO (Back buffer)
            glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
            glViewport(0,0,self.width, self.height)

            glClearColor(0.2, 0.2, 0.2, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            # Ordena todas as chamadas por camada
            sorted_calls = sorted(self.back_buffer.get_calls(), key=lambda call: call.layer)

            for call in sorted_calls:
                self._process_draw_call(call)

        except Exception as e:
            print(f"Erro durante render_to_back_buffer: {e}")
        finally:
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            self.doneCurrent()
            self._check_gl_error("render_to_back_buffer")


    def _process_draw_call(self, call):
        """ Processa uma unica draw call de forma segura"""
        try:
            if call.draw_type == BackBuffer2D.DRAW_IMAGE:
                self._render_image(call.obj, call.x, call.y, call.scale, call.angle, call.alpha)
                        
            elif call.draw_type == BackBuffer2D.DRAW_PRIMITIVE:
                if call.obj == "rect":
                    self._render_rect(call.x, call.y, call.scale_x, call.scale_y, call.color)
                            
                elif call.obj == "line":
                    self._render_line(call.x, call.y, call.end_x, call.end_y, call.color)
                            
                elif call.obj == "circle":
                    self._render_circle(call.x, call.y, call.radius, call.color)
                            
                elif call.obj == "polygon":
                    self._render_polygon(call.points, call.color)
                            
                elif call.obj == "arrow":
                    self._render_arrow(call.x, call.y, call.end_x, call.end_y, call.color)

            elif call.draw_type == BackBuffer2D.DRAW_TEXT:
                self._render_text(call.x, call.y, call.obj, call.color)
                
        except Exception as e:
            print(f"Erro ao processar draw call: {str(e)}")

    def _cleanup_gl_resources(self):
        """Libera todos os recursos GL de forma segura"""
        if self.texture:
            glDeleteTextures([self.texture])
            self.texture = None
            
        if self.rbo:
            glDeleteRenderbuffers([self.rbo])
            self.rbo = None
            
        if self.fbo:
            glDeleteFramebuffers([self.fbo])
            self.fbo = None
            
        # Limpa cache de texturas
        for tex_id, *_ in self.texture_cache.values():
            glDeleteTextures([tex_id])
        self.texture_cache.clear()
        self.texture_cache_size = 0

    def update_widget(self):
        '''
            Método para forçar a atualização do widget
        '''
        self.update()

    def render_frame(self):
        '''
            Método único para ser chamado de fora. Atualizando o back_buffer e desenhando
        '''

        self.render_to_back_buffer()
        self.update_widget()


    ## ==== Classes básicas de render para desenhos primitivos
    def _render_rect(self, x, y, w, h, color, thickness=1, fill=False):
        """Desenha um retângulo, com a opção de preenchimento ou apenas a borda."""
        
        glEnable(GL_BLEND)  # Habilita o blending para transparência
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  # Define a função de blending
        
        glPushMatrix()  # Salva o estado atual da matriz de transformação
        
        glColor4f(*color)  # Aplica a cor do retângulo
        
        if fill:
            # Se fill for True, desenha o retângulo preenchido
            glBegin(GL_QUADS)  # Começa a desenhar um quadrado
            glVertex2f(x, y)  # Vértice inferior esquerdo
            glVertex2f(x + w, y)  # Vértice inferior direito
            glVertex2f(x + w, y + h)  # Vértice superior direito
            glVertex2f(x, y + h)  # Vértice superior esquerdo
            glEnd()
        else:
            # Caso contrário, desenha apenas as bordas (retângulo vazio)
            glLineWidth(thickness)  # Define a espessura da linha
            glBegin(GL_LINE_LOOP)  # Começa a desenhar as linhas do retângulo
            glVertex2f(x, y)  # Vértice inferior esquerdo
            glVertex2f(x + w, y)  # Vértice inferior direito
            glVertex2f(x + w, y + h)  # Vértice superior direito
            glVertex2f(x, y + h)  # Vértice superior esquerdo
            glEnd()
        
        glPopMatrix()  # Restaura o estado da matriz de transformação
        glDisable(GL_BLEND)  # Desabilita o blending após o desenho


    def _render_line(self, x1, y1, x2, y2, color, thickness=1):


        glPushMatrix()
        glLineWidth(thickness)
        glColor4f(*color)
        glBegin(GL_LINES)
        glVertex2f(x1, y1)
        glVertex2f(x2, y2)
        glEnd()
        glPopMatrix()



    def _render_circle(self, x, y, radius, color, segments=32, thickness=1):


        glPushMatrix()
        glTranslatef(x,y,0) # Move para o centro do círculo

        glColor4f(*color)
        glLineWidth(thickness)

        glBegin(GL_LINE_LOOP)
        for i in range(segments + 1):
            angle = 2.0 * np.pi * i / segments
            dx = radius * np.cos(angle)
            dy = radius * np.sin(angle)
            glVertex2f(dx, dy) #Coordenadas relativas
        glEnd()

        glPopMatrix()


    def _render_polygon(self, points, color, thickness=1):

        glPushMatrix()
        glColor4f(*color)
        glLineWidth(thickness)
        glBegin(GL_LINE_LOOP)
        for x, y in points:
            glVertex2f(x, y)
        glEnd()
        glPopMatrix()



    def _render_text(self, x, y, text, color):
        # Verificação inicial consolidada
        if not text or not color or not self.isValid():
            return

        self.makeCurrent()
        try:
            # Chave de cache com precisão reduzida
            color_str = "_".join(f"{c:.3f}" for c in color)
            cache_key = f"{text}_{color_str}"
            
            # Verifica se a textura está em cache e ainda é válida
            texture_data = self.texture_cache.get(cache_key)
            if texture_data:
                texture_id, tex_width, tex_height = texture_data
                if not glIsTexture(texture_id):
                    # Textura inválida, remover do cache
                    self.texture_cache_size -= tex_width * tex_height * 4
                    del self.texture_cache[cache_key]
                    texture_data = None
            
            if not texture_data:
                # Configura a fonte
                font = QFont("Arial", 14)
                metrics = QFontMetrics(font)
                margins = 10  # 5px cada lado
                text_width = metrics.width(text) + margins
                text_height = metrics.height() + margins
                
                # Cria imagem com texto
                img = QImage(text_width, text_height, QImage.Format_ARGB32)
                img.fill(Qt.transparent)
                
                # Renderiza texto
                painter = QPainter(img)
                try:
                    painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
                    painter.setPen(QColor.fromRgbF(*color))
                    painter.setFont(font)
                    painter.drawText(5, metrics.ascent() + 5, text)
                finally:
                    painter.end()
                
                # Cria textura OpenGL
                texture_id = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, texture_id)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width(), img.height(), 
                            0, GL_BGRA, GL_UNSIGNED_BYTE, img.constBits().asstring(img.byteCount()))
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                
                # Armazena no cache
                tex_width, tex_height = img.width(), img.height()
                self.texture_cache[cache_key] = (texture_id, tex_width, tex_height)
                self.texture_cache_size += tex_width * tex_height * 4
                
                # Limpeza inteligente do cache (LRU)
                self._clean_texture_cache()

            # Renderização
            texture_id, tex_width, tex_height = self.texture_cache[cache_key]
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            glPushMatrix()
            glTranslatef(x, y, 0)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(0, 0)
            glTexCoord2f(1, 0); glVertex2f(tex_width, 0)
            glTexCoord2f(1, 1); glVertex2f(tex_width, tex_height)
            glTexCoord2f(0, 1); glVertex2f(0, tex_height)
            glEnd()
            glPopMatrix()
            
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)
            
        except Exception as e:
            print(f"Erro ao renderizar texto: {e}")
        finally:
            self.doneCurrent()

    def _clean_texture_cache(self):
        """Limpa o cache de texturas quando excede o tamanho máximo"""
        if self.texture_cache_size <= self.max_texture_cache_size:
            return
        
        # Converte para lista e ordena por tempo de acesso (se implementado)
        items = list(self.texture_cache.items())
        
        # Remove metade das entradas mais antigas
        for key, (tex_id, w, h) in items[:len(items)//2]:
            if glIsTexture(tex_id):
                glDeleteTextures([tex_id])
            self.texture_cache_size -= w * h * 4
            del self.texture_cache[key]
            
            if self.texture_cache_size <= self.max_texture_cache_size:
                break

    def _render_arrow(self, x1, y1, x2, y2, color, width=1):


        self._render_line(x1, y1, x2, y2, color, width)
        angle = np.arctan2(y2 - y1, x2 - x1)
        head_length = 10
        head_angle = np.pi / 6

        left_x = x2 - head_length * np.cos(angle - head_angle)
        left_y = y2 - head_length * np.sin(angle - head_angle)
        right_x = x2 - head_length * np.cos(angle + head_angle)
        right_y = y2 - head_length * np.sin(angle + head_angle)

        self._render_polygon([(x2, y2), (left_x, left_y), (right_x, right_y)], color)


    def _render_image(self, image_obj, x, y, scale=1.0, angle=0.0, alpha=1.0):
        if not image_obj or not image_obj.is_valid():
            return

        self.makeCurrent()  # Garantir o contexto
        try:
            # Verifica se a textura existe e é válida no contexto atual
            if (not hasattr(image_obj, 'texture_id') or not image_obj.texture_id) or (
                image_obj.texture_id and not glIsTexture(image_obj.texture_id)):
                
                if hasattr(image_obj, 'texture_id') and image_obj.texture_id:
                    glDeleteTextures([image_obj.texture_id])
                
                prepared = image_obj._prepare_for_gl()
                if not prepared:
                    print("Erro: Falha ao preparar textura OpenGL para imagem")
                    return
                    
                texture_id = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, texture_id)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 
                            prepared['size'][0], prepared['size'][1], 
                            0, GL_RGBA, GL_UNSIGNED_BYTE, prepared['data'])
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                image_obj.texture_id = texture_id
            
            # Usa o tamanho da imagem original
            w = int(image_obj._source.width * scale)
            h = int(image_obj._source.height * scale)

            glPushAttrib(GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT)
            try:
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                glEnable(GL_TEXTURE_2D)
                
                glBindTexture(GL_TEXTURE_2D, image_obj.texture_id)
                glColor4f(1.0, 1.0, 1.0, alpha)

                glPushMatrix()
                glTranslatef(x, y, 0)
                glRotatef(angle, 0, 0, 1)

                glBegin(GL_QUADS)
                glTexCoord2f(0.0, 0.0); glVertex2f(-w/2, -h/2)
                glTexCoord2f(1.0, 0.0); glVertex2f(w/2, -h/2)
                glTexCoord2f(1.0, 1.0); glVertex2f(w/2, h/2)
                glTexCoord2f(0.0, 1.0); glVertex2f(-w/2, h/2)
                glEnd()

                glPopMatrix()
            except Exception as e:
                print(f"Erro ao renderizar imagem: {e}")
                raise  # Re-lança a exceção após log
            finally:
                glPopAttrib()
        except Exception as e:
            print(f"Erro no processamento da imagem: {e}")
        finally:
            self.doneCurrent()

    # ======= Tratamento de eventos de click no Widget
    def mousePressEvent(self, event):
        '''
        Captura o evento de clique do mouse, armazena a posição relativa ao widget.
        '''
        # Posição do clique no widget
        pos = event.pos()
        self.click_position = (pos.x(), pos.y())
        print(f"Click registrado em: {self.click_position}")

        # Opcional: você pode passar o evento adiante se precisar de outras funcionalidades.
        # super().mousePressEvent(event)

    def get_click_position(self):
        '''
        Retorna a posição do clique armazenada.
        Se não houver clique, retorna None.
        '''
        return self.click_position
    
    # === Funções pra limpar os buffers
    def cleanup(self):
        if not self.isValid(): #Verifica se o contexto ainda é válido
            return 
        
        self.makeCurrent() #Garantir o contexto antes de deletar
        try: 
            if hasattr(self, 'texture') and self.texture:
                try:
                    glDeleteTextures([self.texture])
                except Exception as e:
                    print(f"Erro ao deletar textura: {e}")
                self.texture = None

            if hasattr(self, 'fbo') and self.fbo:
                try:
                    glDeleteFramebuffers(1, [self.fbo])
                except Exception as e:
                    print(f"Erro ao deletar framebuffer: {e}")
                self.fbo = None

            if hasattr(self, 'rbo') and self.rbo:
                try:
                    glDeleteRenderbuffers(1, [self.rbo])
                except Exception as e:
                    print(f"Erro ao deletar renderbuffer: {e}")
                self.rbo = None

            # Limpa cache de texturas
            for tex_id, *_ in self.texture_cache.values():
                glDeleteTextures([tex_id])
            self.texture_cache.clear()
            self.texture_cache_size = 0
        finally:
            self.doneCurrent()

    def closeEvent(self,event):
        '''
        Quando fecahr a janela
        '''
        self.cleanup()
        super().closeEvent(event)