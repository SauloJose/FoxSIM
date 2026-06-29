# 🖼️ **GL2DWidget - Renderização 2D com OpenGL**

O **GL2DWidget** é um componente de renderização 2D baseado em `QOpenGLWidget` (PyQt5) que utiliza OpenGL para criar uma interface gráfica performática e flexível. Ele é projetado para simulações visuais, como o futebol de robôs, permitindo o desenho de imagens, formas geométricas e elementos gráficos com alto desempenho.

---

## 📐 **Arquitetura do GL2DWidget**

O **GL2DWidget** é o núcleo da renderização 2D no projeto. Ele encapsula a lógica de renderização com OpenGL e utiliza um sistema de **back buffer** para organizar e processar as chamadas de desenho. A arquitetura é composta pelos seguintes componentes principais:

### **1. GL2DWidget**
- **Descrição**: Widget principal que gerencia o contexto OpenGL e renderiza os elementos gráficos.
- **Responsabilidades**:
  - Configurar o contexto OpenGL.
  - Gerenciar o ciclo de renderização (`initializeGL`, `resizeGL`, `paintGL`).
  - Processar eventos de interação, como cliques do mouse.
  - Renderizar elementos gráficos com base nas chamadas armazenadas no **BackBuffer2D**.

### **2. BackBuffer2D**
- **Descrição**: Sistema de buffer que organiza as chamadas de desenho (draw calls) antes de enviá-las para o OpenGL.
- **Responsabilidades**:
  - Armazenar chamadas de desenho em uma lista organizada por camadas (`LAYER_BACKGROUND`, `LAYER_OBJECTS`, `LAYER_DEBUG`).
  - Fornecer métodos para desenhar primitivas, imagens e texto.
  - Garantir que as chamadas sejam processadas de forma eficiente e ordenada.

### **3. DrawCall**
- **Descrição**: Representa uma única chamada de desenho, contendo todas as informações necessárias para renderizar um elemento gráfico.
- **Responsabilidades**:
  - Armazenar os parâmetros de desenho, como posição, escala, cor, camada e tipo de objeto.
  - Garantir consistência nos dados de cada chamada.

### **4. Image**
- **Descrição**: Classe auxiliar para carregar, transformar e gerenciar imagens.
- **Responsabilidades**:
  - Carregar imagens de arquivos (`.png`, `.jpg`, etc.).
  - Aplicar transformações como rotação, escala e espelhamento.
  - Preparar os dados da imagem para renderização no OpenGL.

---

## 🔧 **GL2DWidget**

### **Principais Métodos**

#### **1. `initializeGL()`**
- Configura o contexto OpenGL inicial.
- Ativa o blending para suportar transparência.
- Define o viewport e as configurações básicas de projeção.

#### **2. `resizeGL(w, h)`**
- Ajusta o viewport e a projeção ao redimensionar a janela.
- Garante que os elementos gráficos sejam renderizados corretamente em diferentes tamanhos de tela.

#### **3. `paintGL()`**
- Método principal de renderização.
- Processa todas as chamadas de desenho armazenadas no **BackBuffer2D**.
- Renderiza elementos gráficos na ordem das camadas (`LAYER_BACKGROUND`, `LAYER_OBJECTS`, `LAYER_DEBUG`).

#### **4. `mousePressEvent(event)`**
- Captura eventos de clique do mouse.
- Armazena a posição do clique para interações futuras.

#### **5. `render_to_back_buffer()`**
- Renderiza os elementos gráficos diretamente no back buffer.
- Garante que as chamadas de desenho sejam processadas antes de atualizar o widget.

---

## 🗂️ **BackBuffer2D**

O **BackBuffer2D** organiza as chamadas de desenho antes de enviá-las para o OpenGL. Ele permite que diferentes tipos de elementos gráficos sejam desenhados de forma eficiente e ordenada.

### **Principais Métodos**

#### **1. `draw_rect(x, y, w, h, color, layer, fill)`**
- Desenha um retângulo com ou sem preenchimento.
- Parâmetros:
  - `x, y`: Posição do retângulo.
  - `w, h`: Largura e altura.
  - `color`: Cor no formato RGBA.
  - `layer`: Camada de desenho.
  - `fill`: Define se o retângulo será preenchido.

#### **2. `draw_line(x1, y1, x2, y2, color, layer)`**
- Desenha uma linha entre dois pontos.
- Parâmetros:
  - `x1, y1`: Ponto inicial.
  - `x2, y2`: Ponto final.
  - `color`: Cor no formato RGBA.
  - `layer`: Camada de desenho.

#### **3. `draw_circle(x, y, radius, color, layer)`**
- Desenha um círculo.
- Parâmetros:
  - `x, y`: Centro do círculo.
  - `radius`: Raio.
  - `color`: Cor no formato RGBA.
  - `layer`: Camada de desenho.

#### **4. `draw_img(image_obj, x, y, angle, scale, alpha, layer)`**
- Desenha uma imagem.
- Parâmetros:
  - `image_obj`: Objeto da classe `Image`.
  - `x, y`: Posição da imagem.
  - `angle`: Ângulo de rotação.
  - `scale`: Escala.
  - `alpha`: Transparência.
  - `layer`: Camada de desenho.

---

## 🖼️ **Image**

A classe **Image** gerencia imagens e suas transformações antes de serem renderizadas no OpenGL.

### **Principais Métodos**

#### **1. `load(filepath)`**
- Carrega uma imagem de um arquivo.
- Suporta formatos como `.png` e `.jpg`.

#### **2. `rotate(angle)`**
- Rotaciona a imagem em um ângulo específico.
- Retorna uma nova instância da imagem rotacionada.

#### **3. `scale(factor)`**
- Escala a imagem por um fator multiplicativo.
- Retorna uma nova instância da imagem escalada.

#### **4. `flip(x, y)`**
- Espelha a imagem horizontalmente (`x=True`) ou verticalmente (`y=True`).
- Retorna uma nova instância da imagem espelhada.

#### **5. `draw(x, y, screen, layer, alpha)`**
- Desenha a imagem no **GL2DWidget**.
- Parâmetros:
  - `x, y`: Posição da imagem.
  - `screen`: Instância do **GL2DWidget**.
  - `layer`: Camada de desenho.
  - `alpha`: Transparência.

---

## 🖌️ **DrawCall**

A classe **DrawCall** representa uma única chamada de desenho. Cada instância contém todas as informações necessárias para renderizar um elemento gráfico.

### **Atributos Principais**
- `draw_type`: Tipo de desenho (`image`, `primitive`, `text`).
- `obj`: Objeto associado à chamada (ex.: imagem ou texto).
- `x, y`: Posição do elemento.
- `angle`: Ângulo de rotação.
- `scale`: Escala unificada.
- `color`: Cor no formato RGBA.
- `layer`: Camada de desenho.

---

## 🎮 **Ciclo de Renderização**

1. **Inicialização**:
   - O **GL2DWidget** configura o contexto OpenGL e inicializa o **BackBuffer2D**.

2. **Adição de Chamadas de Desenho**:
   - As chamadas de desenho são adicionadas ao **BackBuffer2D** usando métodos como `draw_rect`, `draw_img`, etc.

3. **Renderização**:
   - O método `paintGL()` processa as chamadas de desenho na ordem das camadas e as envia para o OpenGL.

4. **Atualização**:
   - O widget é atualizado continuamente por um `QTimer`, garantindo 60 FPS por padrão.

---

## 📦 **Requisitos**

Instale as dependências necessárias para usar o **GL2DWidget**:

```bash
pip install PyQt5 PyOpenGL Pillow numpy
```

---

## 🔮 **Extensões Futuras**

- Suporte a shaders OpenGL para efeitos visuais avançados.
- Integração com renderização 3D (robôs tridimensionais).
- Controles de zoom e movimentação de câmera.
- Exportação de imagens ou vídeos da simulação.

---

## 🧠 **Referências**

- [PyQt5 - QOpenGLWidget](https://doc.qt.io/qtforpython-5/PySide2/QtOpenGL/QOpenGLWidget.html)
- [OpenGL ES 2.0](https://www.khronos.org/opengles/2_X/)
- [PyOpenGL Documentation](http://pyopengl.sourceforge.net/documentation/)

---

Com este README, você tem uma visão detalhada do funcionamento do **GL2DWidget** e de suas classes auxiliares. Use-o como referência para entender e expandir o sistema de renderização! 🎉