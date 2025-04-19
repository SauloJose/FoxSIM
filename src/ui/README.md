
# Interface Gráfica com PyQt5 + OpenGL

Este módulo implementa uma interface gráfica 2D baseada em `PyQt5` e `OpenGL`, com o objetivo de oferecer uma renderização performática e flexível para simulação de futebol de robôs. Ele funciona como uma alternativa moderna ao `pygame`, aproveitando o poder do OpenGL para desenhar objetos com mais controle, escalabilidade e desempenho.

## 📐 Arquitetura

A interface é composta por dois componentes principais:

- **`Image`**: Classe auxiliar para carregamento e transformação de imagens.
- **`GLWidget`**: Widget de renderização 2D baseado em `QOpenGLWidget`, com métodos utilitários para desenhar formas geométricas e imagens.

---

## 🔧 GLWidget

A classe `GLWidget` é um widget personalizado que se comporta como uma superfície gráfica 2D, semelhante ao `pygame.Surface`. Ela encapsula a lógica de renderização usando OpenGL e é atualizada continuamente por um `QTimer` (por padrão, 60 FPS).

### Funcionalidades principais:

- Desenho de **imagens com rotação e escala**.
- Desenho de **formas geométricas**:
  - Retângulos (cheios e contorno)
  - Círculos
  - Linhas e setas com espessura e ângulo
  - Polígonos (customizáveis)
- Redimensionamento interno via OpenGL (mais rápido que usar bibliotecas como Pillow).
- Suporte para múltiplas transformações e coordenadas no estilo cartesiano.

### Estrutura típica:

```python
widget = GLWidget(width=1024, height=768)
widget.image = Image("assets/field.png")
```

---

## 🖼️ Classe `Image`

Responsável por:

- Carregar imagens a partir de arquivos (`.png`, `.jpg`, etc.)
- Converter imagens para texturas OpenGL
- Gerar transformações como rotação e escalonamento
- Fornecer o `texture_id` para uso no `GLWidget`

Exemplo:

```python
image = Image("assets/ball.png")
widget.draw_image(image, x=100, y=100, angle=45)
```

---

## 🎮 Ciclo de Atualização

O `GLWidget` é atualizado automaticamente por um `QTimer`, que chama:

```python
self.update()  # dispara paintGL
```

Dentro de `paintGL`, todo o conteúdo é redesenhado com base no estado atual. O método `paintGL()` delega o controle da lógica ao simulador (ex: `Simulator.draw(widget)`), o que separa interface da lógica.

---

## 📁 Organização dos Arquivos

```
ui/                           # Interface do sistema
│
├── interface_config.py       # Parâmetros da interface (cores, tamanhos, FPS, etc.)
├── interface.py              # Inicialização e integração do widget com simulador
├── image.py                  # Classe Image (gerenciamento de texturas)
├── mainWindow/               # Interface principal (em construção)
├── pages/                    # Subpáginas (em construção)
|     └── objects/            # objetos das páginas (em construção)
|          ├── page/          # Subpáginas (em construção)
|          ├── openGLWidgets.py # Widgets que utilizam OpenGL (em construção)
|          └── pageObjects.py   # objetos (em construção)
└── scoreboard.py             # Placar visual (em construção)
```

---

## 💡 Como Usar

Você pode conectar sua lógica de simulação com o widget da seguinte forma:

```python
widget = GLWidget()
simulator = Simulator(widget)
widget.simulator = simulator  # A lógica é chamada dentro do paintGL
```

A simulação deve implementar um método `.draw(widget)` onde todos os objetos são renderizados usando os métodos de desenho do widget.

---

## 🔮 Extensões Futuras

- Suporte a shaders OpenGL para efeitos visuais
- Integração com renderização 3D (robôs tridimensionais)
- Controles de zoom e movimentação de câmera
- Possibilidade de exportar imagens ou vídeos da simulação

---

## 📦 Requisitos

Instale as dependências necessárias:

```bash
pip install PyQt5 PyOpenGL Pillow numpy
```

---

## 🧠 Referência

- [PyQt5 - QOpenGLWidget](https://doc.qt.io/qtforpython-5/PySide2/QtOpenGL/QOpenGLWidget.html)
- [OpenGL ES 2.0](https://www.khronos.org/opengles/2_X/)
- [PyOpenGL Documentation](http://pyopengl.sourceforge.net/documentation/)
