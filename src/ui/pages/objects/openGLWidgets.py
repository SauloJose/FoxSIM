import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU  import *
import OpenGL 

from PIL import Image as PILImage
from ui.pages.objects.imageGL import *
from ui.pages.objects.backbuffer2D import *

class TextureCache:
    def __init__(self, max_size_mb=50):
        self.cache = {}
        self.max_size = max_size_mb * 1024 * 1024
        self.current_size = 0
        self.access_counter = 0

    def get(self, key):
        """Obtém textura do cache com LRU"""
        if key in self.cache:
            entry = self.cache[key]
            if glIsTexture(entry['id']):
                entry['last_used'] = self.access_counter
                self.access_counter += 1
                return entry['id']
            self._remove(key)
        return None

    def add(self, key, tex_id, size):
        """Adiciona textura ao cache com gerenciamento automático de tamanho"""
        if self.current_size + size > self.max_size:
            self._cleanup()
        
        self.cache[key] = {
            'id': tex_id,
            'size': size,
            'last_used': self.access_counter
        }
        self.current_size += size
        self.access_counter += 1

    def _cleanup(self):
        """Remove as texturas menos usadas recentemente"""
        entries = sorted(self.cache.items(), key=lambda x: x[1]['last_used'])
        for key, entry in entries[:len(entries)//2]:
            self._remove(key)

    def _remove(self, key):
        """Remove uma textura específica"""
        if key in self.cache:
            glDeleteTextures([self.cache[key]['id']])
            self.current_size -= self.cache[key]['size']
            del self.cache[key]

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
    initialized = pyqtSignal() # Sinal 

    def __init__(self, parent=None, width=None, height=None):
        '''
            Inicializa o widget, define largura e altura, carrega a imagem e configura um timer para atualização.

            Args:
                parent (QWidget): Widget pai.
                width (int): Largura opcional do widget.
                height (int): Altura opcional do widget.
        '''
        # AGORA chamamos o construtor da classe pai
        super().__init__(parent)

        fmt = QSurfaceFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QSurfaceFormat.CompatibilityProfile)
        fmt.setRenderableType(QSurfaceFormat.OpenGL)
        fmt.setSwapBehavior(QSurfaceFormat.DoubleBuffer)
        QSurfaceFormat.setDefaultFormat(fmt)  # <- ESSENCIAL
        self.setFormat(fmt)


        self.texture_cache = TextureCache(max_size_mb=50)
        
        # Definição de tamanhos com base no widget pai ou valores padrões
        self.view_width = max(1, width) if width is not None else 800
        self.view_height = max(1, height) if height is not None else 600
        self.setMinimumSize(self.view_width, self.view_height)

        # back_buffer do Widget
        self.back_buffer = BackBuffer2D()

        # GL resources
        self.fbo = None 
        self.texture = None 
        self.rbo = None 
        self._use_fbo = True 
        self._is_initialized = False 

        # Interação
        self.click_position = None 

    def initializeGL(self):
        print("[GL2DWidget]: Iniciando o GL")
        try:
            self.makeCurrent()

            ctx = QOpenGLContext.currentContext()
            if not self.isValid() or not ctx:
                print("initializeGL: contexto ainda não está disponível.")
                QTimer.singleShot(100, self.initializeGL)
                return

            print("OpenGL version:", glGetString(GL_VERSION).decode())
            print("GLSL version:", glGetString(GL_SHADING_LANGUAGE_VERSION).decode())

            extensions = []
            try:
                num_ext = glGetIntegerv(GL_NUM_EXTENSIONS)
                for i in range(num_ext):
                    ext = glGetStringi(GL_EXTENSIONS, i)
                    if ext:
                        extensions.append(ext.decode())
                print("Extensions:", extensions[:10])
            except Exception as e:
                print(f"[Aviso] Não foi possível obter extensões via glGetStringi: {e}")

            glClearColor(0.2, 0.2, 0.2, 1.0)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            self._is_initialized = True
            self.initialized.emit()

            QTimer.singleShot(0, self._setup_framebuffer)  # executa no próximo ciclo do event loop

            
        except Exception as e:
            print(f"Erro ao inicializar OpenGL: {e}")
            self._check_gl_error("initializeGL")
            QTimer.singleShot(1000, self.initializeGL)  # Tenta novamente
        finally:
            self.doneCurrent()

    def _fbo_ok(self):
        ''' Verifica o estado do fbo'''
        if not self.fbo or not glIsFramebuffer(self.fbo):
            return False
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        return status == GL_FRAMEBUFFER_COMPLETE

    def check_gl_ready(self):
        """Verifica se o contexto OpenGL foi inicializado corretamente."""
        try:
            version = glGetString(GL_VERSION)
            if not version:
                raise RuntimeError("Falha ao obter versão OpenGL.")
            print(f"OpenGL versão: {version}")
        except Exception as e:
            print(f"Erro ao verificar OpenGL: {e}")
            self.show_error("Falha ao inicializar contexto OpenGL.")

    # Atualize o _setup_framebuffer
    def _setup_framebuffer(self, retries=3):
        print("[GL2DWidget]: Setup do framebuffer;")
        if not self.isValid() or not QOpenGLContext.currentContext():
            print("FBO: contexto inválido")
            return

        # Verificação explícita das funções GL
        if not all(map(bool, [glGenFramebuffers, glBindFramebuffer, glGenTextures])):
            print("Funções GL ainda não estão disponíveis. Aguardando novo ciclo.")
            QTimer.singleShot(100, lambda: self._setup_framebuffer(retries - 1))
            return

        if retries <= 0:
            print("Falha crítica ao configurar FBO após múltiplas tentativas")
            return

        self.makeCurrent()
        try:
            # Limpeza segura
            self._cleanup_gl_resources()

            # Dimensões seguras
            w = max(1,self.view_width)
            h = max(1, self.view_height)

            # Cria FBO
            self.fbo = glGenFramebuffers(1)
            glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
            
            # Cria texture attachment
            self.texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            glTexImage2D(
                GL_TEXTURE_2D, 0, GL_RGBA, 
                w,h,
                0, GL_RGBA, GL_UNSIGNED_BYTE, None  
            )
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glFramebufferTexture2D(
                GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,
                GL_TEXTURE_2D, self.texture, 0
            )
            
            # Cria renderbuffer de profundidade
            self.rbo = glGenRenderbuffers(1)
            glBindRenderbuffer(GL_RENDERBUFFER, self.rbo)
            glRenderbufferStorage(
                GL_RENDERBUFFER, GL_DEPTH24_STENCIL8,
                w,h
            )
            glFramebufferRenderbuffer(
                GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT,
                GL_RENDERBUFFER, self.rbo
            )
            
            # Verificação completa do FBO
            status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
            if status != GL_FRAMEBUFFER_COMPLETE:
                raise RuntimeError(f"FBO incompleto, status: 0x{status:X}")
                
            print("FBO configurado com sucesso")
            
        except Exception as e:
            print(f"Erro ao configurar FBO (tentativa {4-retries}/3): {e}")
            self._cleanup_gl_resources()
            QTimer.singleShot(1000, lambda: self._setup_framebuffer(retries-1))
        finally:
            try:
                glBindFramebuffer(GL_FRAMEBUFFER, 0)
            except Exception as e:
                print(f"Erro ao desassociar framebuffer: {e}")
            self.doneCurrent()

            
    def resizeGL(self, w, h):
        """
        Chamado automaticamente quando o widget é redimensionado.
        Atualiza o viewport, a projeção ortográfica e o framebuffer (FBO).
        """
        if not self.isValid() or not QOpenGLContext.currentContext():
            print("resizeGL: contexto inválido.")
            return
    
        self.makeCurrent()  # Torna o contexto atual para operações OpenGL

        try:
            # Atualiza as dimensões da janela
            self.view_width = w
            self.view_height = h

            # Viewport e projeção ortográfica estilo pygame
            glViewport(0,0,w,h)

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glOrtho(0, w, h, 0, -1, 1)  # (left, right, bottom, top, near, far)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # Recia FBO com novo tamanho
            if self._is_initialized:
                self._setup_framebuffer()

        except Exception as e:
            print(f"Erro em resizeGL: {e}")
            self._check_gl_error("resizeGL")
        finally:
            self.doneCurrent()

    def _check_gl_functions(self):
        """Verifica se as funções necessárias estão disponíveis"""
        required_funcs = {
            'Framebuffers': bool(glGenFramebuffers),
            'Renderbuffers': bool(glGenRenderbuffers),
            'Textures': bool(glGenTextures)
        }
        
        missing = [name for name, available in required_funcs.items() if not available]
        if missing:
            raise RuntimeError(f"Funções OpenGL indisponíveis: {', '.join(missing)}")
        
    def _check_gl_error(self, context):
        if not QOpenGLContext.currentContext():
            print(f"[{context}] Sem contexto GL ativo para checar erro.")
            return

        error = glGetError()
        if error != GL_NO_ERROR:
            print(f"OpenGL erro em {context}: {error}")
            if error == 1282:
                print("Erro 1282: operação inválida — provavelmente por framebuffer incompleto ou função inválida.")

    ## == Método principal de desenho utilizando o open GL
    def paintGL(self):
        """
        Método principal de desenho utilizando o OpenGL. Realiza o processo de renderização,
        desenhando o conteúdo do FBO no buffer de exibição.
        """
        if not self._fbo_ok():
            print("paintGL: FBO não está válido")
            return

        self.makeCurrent()
        try:
            w = max(1, self.view_width)
            h = max(1, self.view_height)

            # Limpa o buffer principal
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            glBindFramebuffer(GL_READ_FRAMEBUFFER, self.fbo)
            glBindFramebuffer(GL_DRAW_FRAMEBUFFER,0)

            glBlitFramebuffer(0, 0, w, h,
                          0, 0, w, h,
                          GL_COLOR_BUFFER_BIT, GL_NEAREST)

            glBindFramebuffer(GL_READ_FRAMEBUFFER, 0)

            glFlush()


        except Exception as e:
            print(f"Erro fatal em paintGL: {str(e)}")
            self._is_initialized = False 
        
        finally:
            self.back_buffer.clear()  # Limpa as chamadas após desenhar
            self.doneCurrent()


    def render_to_back_buffer(self):
        '''
        Desenha todas as draw_calls acumuladas no FBO (backbuffer).
        O conteúdo só será exibido após um flip() (update → paintGL).  
          '''
        if not self._is_initialized:
            print("render_to_back_buffer: Widget ainda não inicializado.")
            return
                
        self.makeCurrent()

        try: 
            if not self._fbo_ok():
                print("Erro: framebuffer inválido ou não inicializado.")
                return

            # Use dimensões seguras
            w = max(1, self.view_width)
            h = max(1, self.view_height)

            # Desenha tudo no FBO (Back buffer)
            glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
            glViewport(0, 0, w,h)

            # Limpa o buffer
            glClearColor(0.2, 0.2, 0.2, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Ordena todas as chamadas por camada
            sorted_calls = sorted(self.back_buffer.get_calls(), key=lambda call: call.layer)
            for call in sorted_calls:
                try:
                    self._process_draw_call(call)
                except Exception as e:
                    print(f"[Erro] ao processar chamada de desenho: {e}")
                
        except Exception as e:
            print(f"[Erro] durante render_to_back_buffer: {e}")
            self._check_gl_error("render_to_back_buffer")
            
        finally:
            try:
                glBindFramebuffer(GL_FRAMEBUFFER, 0)
            except Exception as e:
                print(f"[Erro] ao disvincular FBO: {e}")
            self.doneCurrent()


    def _process_draw_call(self, call):
        """ Processa uma unica draw call de forma segura"""
        try:
            if call.draw_type == BackBuffer2D.DRAW_IMAGE:
                if call.obj:
                    self._render_image(call.obj, call.x, call.y, call.scale, call.angle, call.alpha)
                else:
                    print("[Aviso] DRAW_IMAGE com objeto nulo.")

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
                else:
                    print(f"[Aviso]: Objeto de primitiva desconhecido: {call.obj}")

            elif call.draw_type == BackBuffer2D.DRAW_TEXT:
                if isinstance(call.obj, str):
                    self._render_text(call.x, call.y, call.obj, call.color)
                else:
                    print("[Aviso]: DRAW_TEXT com objeto não textual.")
            
            else:
                print(f"[Aviso] Tipo de draw_call desconhecido: {call.draw_type}")
        except Exception as e:
            print(f"[Erro] Erro ao processar draw call: {str(e)}")

    def _cleanup_gl_resources(self):
        """Libera todos os recursos GL de forma segura"""
        self.makeCurrent()
        try:
            if self.texture and glIsTexture(self.texture):
                glDeleteTextures([self.texture])
            self.texture = None
            
            if self.rbo and glIsRenderbuffer(self.rbo):
                glDeleteRenderbuffers([self.rbo])
            self.rbo = None
            
            if self.fbo and glIsFramebuffer(self.fbo):
                glDeleteFramebuffers([self.fbo])
            self.fbo = None
            
            # Limpa cache de texturas
            for cache_type in self.texture_cache.values():
                for entry in cache_type.values():
                    if len(entry) > 0 and glIsTexture(entry[0]):
                        glDeleteTextures([entry[0]])
            
            self.texture_cache = {'text': {}, 'images': {}}
            self.texture_cache_size = 0
            
        except Exception as e:
            print(f"Erro ao liberar recursos GL: {e}")
        finally:
            self.doneCurrent()

    def update_widget(self):
        '''
            Método para forçar a atualização do widget
        '''
        self.update()

    def render_frame(self):
        '''
            Método único para ser chamado de fora. Atualizando o back_buffer e desenhando
            semelhante ao flip.
        '''
        if not self._is_initialized:
            return 
        self.render_to_back_buffer()
        self.update_widget()

    ## ==== Classes básicas de render para desenhos primitivos
    def _safe_gl_render(self, render_func, *args):
        """Wrapper seguro para funções de renderização"""
        if not self._is_initialized or not QOpenGLContext.currentContext():
            return
        
        self.makeCurrent()
        glPushAttrib(GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT | GL_LINE_BIT)
        try:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            render_func(*args)
        except Exception as e:
            print(f"Erro na renderização: {e}")
        finally:
            glPopAttrib()
            self.doneCurrent() 



    def _render_rect(self, x, y, w, h, color, thickness=1, fill=False):
        """Desenha um retângulo, com a opção de preenchimento ou apenas a borda."""
        def _draw():
            glPushMatrix()
            glColor4f(*color)
            if fill:
                glBegin(GL_QUADS)
            else:
                glLineWidth(thickness)
                glBegin(GL_LINE_LOOP)
            
            glVertex2f(x, y)
            glVertex2f(x + w, y)
            glVertex2f(x + w, y + h)
            glVertex2f(x, y + h)
            glEnd()
            glPopMatrix()
        
        self._safe_gl_render(_draw)


    def _render_line(self, x1, y1, x2, y2, color, thickness=1):
        '''
            Método padrão para renderizar uma linha
        '''
        def _draw():
            glLineWidth(thickness)
            glColor4f(*color)
            glBegin(GL_LINES)
            glVertex2f(x1, y1)
            glVertex2f(x2, y2)
            glEnd()
        
        self._safe_gl_render(_draw)


    def _render_circle(self, x, y, radius, color, segments=32, thickness=1):
        '''
            Método padrão para renderizar círculos
        '''
        def _draw():
            # Pré-computa os vértices uma vez
            vertices = []
            for i in range(segments + 1):
                angle = 2.0 * np.pi * i / segments
                vertices.append((radius * np.cos(angle), radius * np.sin(angle)))
            
            glPushMatrix()
            glTranslatef(x, y, 0)
            glColor4f(*color)
            glLineWidth(thickness)
            glBegin(GL_LINE_LOOP)
            for dx, dy in vertices:
                glVertex2f(dx, dy)
            glEnd()
            glPopMatrix()
        
        self._safe_gl_render(_draw)


    def _render_polygon(self, points, color, thickness=1):
        if not points or len(points) < 3:
            return
        
        def _draw():
            glColor4f(*color)
            glLineWidth(thickness)
            glBegin(GL_LINE_LOOP)
            for x, y in points:
                glVertex2f(x, y)
            glEnd()
        
        self._safe_gl_render(_draw)




    def _render_text(self, x, y, text, color):
        # Verificação inicial consolidada
        if not text or not color or len(color)<4:
            return

        def _draw():
            # Geração de chave de cache mais robusta
            cache_key = f"text_{hash(text)}_{hash(color.tobytes())}"
            
            texture = self.texture_cache.get(cache_key)
            if not texture:
                # Criação otimizada da textura
                texture = self._create_text_texture(text, color)
                if texture:
                    self.texture_cache.add(cache_key, texture['id'], texture['size'])

            if texture:
                self._draw_textured_quad(x, y, texture['width'], texture['height'], texture['id'])

        self._safe_gl_render(_draw)

    # Criando texturas de texto
    def _create_text_texture(self, text, color):
        """Cria textura para texto de forma otimizada"""
        font = QFont("Arial", 14, QFont.Bold)
        metrics = QFontMetrics(font)
        margin = 2
        size = metrics.size(0, text)
        
        image = QImage(size.width() + margin*2, size.height() + margin*2, 
                    QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setPen(QColor.fromRgbF(*color))
        painter.setFont(font)
        painter.drawText(margin, margin + metrics.ascent(), text)
        painter.end()

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width(), image.height(),
                    0, GL_BGRA, GL_UNSIGNED_BYTE, image.bits())
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        
        return {
            'id': texture_id,
            'width': image.width(),
            'height': image.height(),
            'size': image.width() * image.height() * 4
        }

    def _render_arrow(self, x1, y1, x2, y2, color, width=1):
        """Renderiza uma seta usando NumPy para cálculos vetoriais"""
        def _draw():
            # Converte pontos para arrays NumPy
            start = np.array([x1, y1])
            end = np.array([x2, y2])
            
            # Vetor de direção e ângulo
            direction = end - start
            angle = np.arctan2(direction[1], direction[0])
            
            # Parâmetros da cabeça da seta
            head_length = 10 * width
            head_angle = np.pi / 6  # 30 graus
            
            # Renderiza a linha principal
            self._render_line(x1, y1, x2, y2, color, width)
            
            # Calcula os vértices da cabeça usando NumPy
            angles = np.array([angle - head_angle, angle + head_angle])
            head_vectors = head_length * np.column_stack([
                np.cos(angles),
                np.sin(angles)
            ])
            
            # Pontos da cabeça relativos à ponta
            left_point = end - head_vectors[0]
            right_point = end - head_vectors[1]
            
            # Renderização otimizada
            glBegin(GL_TRIANGLES)
            glVertex2f(*end)
            glVertex2f(*left_point)
            glVertex2f(*right_point)
            glEnd()
        
        self._safe_gl_render(_draw)

    def _render_direct(self):
        try:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glViewport(0, 0, self.width(), self.height())
            
            # Sua lógica de renderização aqui
            for call in sorted(self.back_buffer.get_calls(), key=lambda x: x.layer):
                self._process_draw_call(call)
                
        except Exception as e:
            print(f"Erro na renderização direta: {e}")
            
    #Renderizando imagem
    def _render_image(self, image_obj: Image, x: float, y: float, 
                    scale: float = 1.0, angle: float = 0.0, alpha: float = 1.0) -> None:
        """
        Renderiza uma imagem com transformações, usando cache de texturas otimizado
        
        Args:
            image_obj: Objeto Image contendo os dados da imagem
            x, y: Posição na tela
            scale: Escala uniforme (1.0 = tamanho original)
            angle: Ângulo de rotação em graus
            alpha: Transparência (0.0 a 1.0)
        """
        # Validação inicial rápida
        if not self._is_initialized or not image_obj or not image_obj.is_valid():
            return

        def _draw():
            # Geração da chave de cache otimizada
            cache_key = self._generate_image_cache_key(image_obj)
            
            # Tentativa de obtenção do cache
            texture = self.texture_cache.get(cache_key)
            
            # Cache miss - criação da textura
            if not texture:
                if (prepared := image_obj._prepare_for_gl()):  # Operador walrus (Python 3.8+)
                    if (texture := self._create_gl_texture(prepared)):
                        self.texture_cache.add(cache_key, texture['id'], texture['size'])
                else:
                    return  # Falha na preparação da imagem

            # Renderização do quad texturizado
            if texture:
                # Cálculo de dimensões otimizado
                w = image_obj.width * scale
                h = image_obj.height * scale
                
                # Configuração de estados OpenGL
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, texture['id'])
                glColor4f(1.0, 1.0, 1.0, alpha)
                
                # Transformações geométricas
                glPushMatrix()
                glTranslatef(x, y, 0)
                glRotatef(angle, 0, 0, 1)  # Rotação em torno do centro
                
                # Renderização do quad
                glBegin(GL_QUADS)
                glTexCoord2f(0, 0); glVertex2f(-w/2, -h/2)  # Canto inferior esquerdo
                glTexCoord2f(1, 0); glVertex2f(w/2, -h/2)   # Canto inferior direito
                glTexCoord2f(1, 1); glVertex2f(w/2, h/2)    # Canto superior direito
                glTexCoord2f(0, 1); glVertex2f(-w/2, h/2)   # Canto superior esquerdo
                glEnd()
                
                glPopMatrix()
                
                # Limpeza de estados
                glDisable(GL_TEXTURE_2D)

        # Execução segura no contexto OpenGL
        self._safe_gl_render(_draw)
            
    def _draw_textured_quad(self, x, y, w, h, tex_id, angle=0.0, alpha=1.0):
        """Método compartilhado para renderização de quads texturizados"""
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glColor4f(1.0, 1.0, 1.0, alpha)
        
        glPushMatrix()
        glTranslatef(x, y, 0)
        glRotatef(angle, 0, 0, 1)
        
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(-w/2, -h/2)
        glTexCoord2f(1, 0); glVertex2f(w/2, -h/2)
        glTexCoord2f(1, 1); glVertex2f(w/2, h/2)
        glTexCoord2f(0, 1); glVertex2f(-w/2, h/2)
        glEnd()
        
        glPopMatrix()

    def _create_gl_texture(self, image_data):
        """
        Cria uma textura OpenGL a partir de dados de imagem preparados
        Args:
            image_data: Dict com:
                - 'data': bytes da imagem (formato RGBA)
                - 'size': (width, height)
        Returns:
            Dict com textura criada ou None em caso de erro
        """
        if not image_data or 'data' not in image_data or 'size' not in image_data:
            return None

        try:
            width, height = image_data['size']
            texture_id = glGenTextures(1)
            
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height,
                        0, GL_RGBA, GL_UNSIGNED_BYTE, image_data['data'])
            
            # Configurações padrão para filtragem
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            
            return {
                'id': texture_id,
                'width': width,
                'height': height,
                'size': width * height * 4  # 4 bytes por pixel (RGBA)
            }
            
        except Exception as e:
            print(f"Erro ao criar textura OpenGL: {e}")
            if 'texture_id' in locals() and glIsTexture(texture_id):
                glDeleteTextures([texture_id])
            return None

    def _generate_image_cache_key(self, image_obj: Image) ->str:
        """
        Gera uma chave de cache única para uma imagem e suas transformações
        Args:
            image_obj: Instância da classe Image
        Returns:
            String hash única para a combinação imagem+transformações
        """
        if not image_obj or not image_obj.is_valid():
            return "invalid_0"

        # Usamos o caminho do arquivo ou dados do fallback como base
        content_id = image_obj._filepath or f"fallback_{id(image_obj._source)}"
        
        # Hash das transformações atuais (com precisão controlada)
        transform_hash = hash((
            round(image_obj._current_angle, 2),    # Ângulo com 2 casas decimais
            round(image_obj._current_scale, 4),    # Escala com 4 casas decimais
            image_obj._flip_x,
            image_obj._flip_y,
            image_obj.width,                       # Dimensões finais
            image_obj.height
        ))
        
        return f"img_{hash(content_id)}_{transform_hash}"
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
    
    def cleanup(self):
        """
        Limpeza completa de todos os recursos OpenGL, incluindo FBOs, texturas e cache
        Versão otimizada para o novo sistema de gerenciamento de recursos
        """
        if not self.isValid():
            return

        self.makeCurrent()
        try:
            # 1. Limpeza de Framebuffers e Renderbuffers
            if hasattr(self, 'fbo') and self.fbo and glIsFramebuffer(self.fbo):
                glDeleteFramebuffers([self.fbo])
                self.fbo = None

            if hasattr(self, 'rbo') and self.rbo and glIsRenderbuffer(self.rbo):
                glDeleteRenderbuffers([self.rbo])
                self.rbo = None

            # 2. Limpeza do sistema de cache unificado
            if hasattr(self, 'texture_cache'):
                # Método mais eficiente para limpar todas as texturas
                all_textures = [entry['id'] for entry in self.texture_cache.cache.values()]
                if all_textures:
                    glDeleteTextures(all_textures)
                
                # Reset completo do cache
                self.texture_cache.cache.clear()
                self.texture_cache.current_size = 0
                self.texture_cache.access_counter = 0

            # 3. Limpeza adicional de recursos (se necessário)
            if hasattr(self, 'back_buffer'):
                self.back_buffer.clear()

            # 4. Forçar liberação de recursos da GPU
            glFlush()
            glFinish()

        except Exception as e:
            print(f"Erro durante cleanup: {e}")
            # Não relançar a exceção para evitar problemas no destrutor
        finally:
            self.doneCurrent()
            self._is_initialized = False  # Marca como não inicializado


    def closeEvent(self,event):
        '''
        Quando fecahr a janela
        '''
        self.cleanup()
        super().closeEvent(event)

    #Função para fazer chamadas seguras
    def _safe_gl_call(self, func, *args):
        if not self._is_initialized or not QOpenGLContext.currentContext():
            return
        try:
            func(*args)
            self._check_gl_error(func.__name__)
        except Exception as e:
            print(f"Erro em {func.__name__}: {e}")

    #função de debug
    def print_gl_info(self):
        self.makeCurrent()
        try:
            print("Vendor:", glGetString(GL_VENDOR).decode())
            print("Renderer:", glGetString(GL_RENDERER).decode())
            print("Version:", glGetString(GL_VERSION).decode())
            print("Extensions:", glGetString(GL_EXTENSIONS).decode())
        finally:
            self.doneCurrent()