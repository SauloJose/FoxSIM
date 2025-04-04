# ============================
# Configurações da Janela
# ============================
WINDOW_WIDTH = 1200  # Largura da janela em pixels
WINDOW_HEIGHT = 600  # Altura da janela em pixels

# ============================
# Configurações do Campo
# ============================
ORIGINAL_FIELD_WIDTH = 645  # Largura original do campo em cm
ORIGINAL_FIELD_HEIGHT = 413  # Altura original do campo em cm
FIELD_WIDTH = 645  # Largura do campo em pixels
SCALE = FIELD_WIDTH / ORIGINAL_FIELD_WIDTH  # Escala para ajustar o campo (1px = 1cm)
FIELD_HEIGHT = int(ORIGINAL_FIELD_HEIGHT * SCALE)  # Altura do campo em pixels (escalada)

# ============================
# Configurações das Áreas
# ============================
SCOREBOARD_HEIGHT = 50  # Altura do placar em pixels
SIDEBAR_WIDTH = 400  # Largura das janelas laterais em pixels
CONFIG_HEIGHT = 160  # Altura da área de configurações em pixels

# ============================
# Configurações dos Gols
# ============================
GOAL_WIDTH = int(10 * SCALE)  # Largura do gol em pixels (10cm escalados)
GOAL_HEIGHT = int(40 * SCALE)  # Altura do gol em pixels (40cm escalados)

# ============================
# Configurações dos Robôs
# ============================
ROBOT_SIZE = int(10 * SCALE)  # Tamanho dos robôs em pixels (7cm escalados)

# ============================
# Cores
# ============================
FIELD_COLOR = (144, 238, 144)  # Cor do campo (verde claro)
LINE_COLOR = (255, 255, 255)  # Cor das linhas do campo (branco)

# Cores dos times
TEAM_BLUE_COLOR = (0, 0, 255)  # Cor do time azul
TEAM_RED_COLOR = (255, 0, 0)  # Cor do time vermelho

# Cores do placar
SCOREBOARD_COLOR = (50, 50, 50)  # Cor do fundo do placar (cinza escuro)

# Cores das janelas laterais
SIDEBAR_COLOR_1 = (100, 100, 100)  # Cor da Janela 1 (cinza médio)
SIDEBAR_COLOR_2 = (150, 150, 150)  # Cor da Janela 2 (cinza claro)

# Cor da área de configurações
CONFIG_COLOR = (30, 30, 30)  # Cor do fundo da área de configurações (cinza muito escuro)

# ============================
# Configurações dos Botões
# ============================
BUTTON_WIDTH = 120  # Largura dos botões em pixels
BUTTON_HEIGHT = 50  # Altura dos botões em pixels
BUTTON_SPACING = 10  # Espaçamento entre os botões em pixels

# ============================
# Configurações do Fundo
# ============================
BACKGROUND_COLOR = (0, 0, 0)  # Cor do fundo (preto)

# ============================
# Configurações da Bola
# ============================
BALL_RADIUS = int(2 * SCALE)  # Raio da bola em pixels (2cm escalados)
BALL_COLOR = (255, 165, 0)  # Cor da bola (laranja)


# ============================
# Configurações de exibição
# ============================
FPS = 60



#Posições importante dos robôs na imagem:# Coordenadas relativas dos pontos "+" (em cm, baseadas no campo original)
RELATIVE_POSITIONS = [
    (100, 100),  # Exemplo: canto superior esquerdo
    (200, 100),  # Exemplo: ponto superior central
    (300, 100),  # Exemplo: canto superior direito
    (100, 300),  # Exemplo: canto inferior esquerdo
    (200, 300),  # Exemplo: ponto inferior central
    (300, 300),  # Exemplo: canto inferior direito
]