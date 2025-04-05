import numpy as np

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
ROBOT_SIZE = int(20 * SCALE)  # Tamanho dos robôs em pixels (7cm escalados)

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
#tempo da partida
TIMER_PARTY = 60  # Tempo da partida em segundos (5 minutos)


#Posições importante dos robôs na imagem:# Coordenadas relativas dos pontos "+" (em cm, baseadas no campo original)
RELATIVE_POSITIONS = [
    (100, 100),  # Exemplo: canto superior esquerdo
    (200, 100),  # Exemplo: ponto superior central
    (300, 100),  # Exemplo: canto superior direito
    (100, 300),  # Exemplo: canto inferior esquerdo
    (200, 300),  # Exemplo: ponto inferior central
    (300, 300),  # Exemplo: canto inferior direito
]


# Margens internas do campo (ajuste conforme necessário)
FIELD_MARGIN_TOP = 20
FIELD_MARGIN_BOTTOM = 20
FIELD_MARGIN_LEFT = 20
FIELD_MARGIN_RIGHT = 20

# Ajustar os limites do campo
FIELD_INTERNAL_WIDTH = FIELD_WIDTH - FIELD_MARGIN_LEFT - FIELD_MARGIN_RIGHT
FIELD_INTERNAL_HEIGHT = FIELD_HEIGHT - FIELD_MARGIN_TOP - FIELD_MARGIN_BOTTOM



#Pontos importantes do campo para o simulador:
#extremos do campo virtual
fieldP1v  =   np.array([97,12])
fieldP2v  =   np.array([547,12])
fieldP3v  =   np.array([547,402])
fieldP4v  =   np.array([97,402])

#centro do campo virtual
fieldCenterv  =   np.array([322,207])
#pivots virtual
PA1v   =   np.array([210,87])
PA2v   =   np.array([210,207])
PA3v   =   np.array([210,327])
PE1v   =   np.array([435,87])
PE2v   =   np.array([435,207])
PE3v   =   np.array([435,327])
#area goleiro aliado virtual
GA1v   =   np.array([97,102])
GA2v   =   np.array([142,102])    
GA3v   =   np.array([142,312])  
GA4v   =   np.array([97,312])
#area interna do goleiro aliado virtual
GAI1v  =   np.array([67,147])
GAI2v  =   np.array([97,147])
GAI3v  =   np.array([97,267])
GAI4v  =   np.array([67,267])

#area goleiro aliado virtual
GE1v   =   np.array([502,102])
GE2v   =   np.array([547,102])    
GE3v   =   np.array([547,312])  
GE4v   =   np.array([502,312])
#area interna do goleiro aliado virtual
GEI1v  =   np.array([547,147])
GEI2v  =   np.array([577,147])
GEI3v  =   np.array([577,267])
GEI4v  =   np.array([547,267])
#area a aliada
#meios dos lados virtual
fieldP12v  =   np.array([322,12])
fieldP34v  =   np.array([322,402])

# ============================
# Parâmetros da física do simulador
# ============================

#Tipos de objetos do sistema
ROBOT_OBJECT = "ROBOT"
BALL_OBJECT = "BALL"
FIELD_OBJECT = "FIELD"
LINE_OBJECT  = "LINE"
POINT_OBJECT = "POINT"

# 

#Coeficientes de restituição das colisões (e)
COEFFICIENT_RESTITUTION_BALL_ROBOT = 0.6  # Colisão bola-robô
COEFFICIENT_RESTITUTION_BALL_FIELD = 0.8  # Colisão bola-campo
COEFFICIENT_RESTITUTION_ROBOT_ROBOT = 0.4  # Colisão robô-robô 
COEFFICIENT_RESTITUTION_ROBOT_FIELD = 0.0 # Colisão robô-campo (sem restituição)


#Coeficiente de Arrasto para a bola