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
# Quadros por segundo
FPS = 60
#tempo da partida
TIMER_PARTY = 60  # Tempo da partida em segundos (5 minutos)


# Margens internas do campo (ajuste conforme necessário)
FIELD_MARGIN_TOP = 20
FIELD_MARGIN_BOTTOM = 20
FIELD_MARGIN_LEFT = 20
FIELD_MARGIN_RIGHT = 20

# Ajustar os limites do campo
FIELD_INTERNAL_WIDTH = FIELD_WIDTH - FIELD_MARGIN_LEFT - FIELD_MARGIN_RIGHT
FIELD_INTERNAL_HEIGHT = FIELD_HEIGHT - FIELD_MARGIN_TOP - FIELD_MARGIN_BOTTOM



# Pivots virtuais
PA1v   =   np.array([210,137])  # Atualizado
PA2v   =   np.array([210,257])  # Atualizado
PA3v   =   np.array([210,377])  # Atualizado
PE1v   =   np.array([435,137])  # Atualizado
PE2v   =   np.array([435,257])  # Atualizado
PE3v   =   np.array([435,377])  # Atualizado

# Área goleiro aliado virtual
GA1v   =   np.array([97,152])  # Atualizado
GA2v   =   np.array([142,152])  # Atualizado
GA3v   =   np.array([142,362])  # Atualizado
GA4v   =   np.array([97,362])  # Atualizado

# Área interna do goleiro aliado virtual
GAI1v  =   np.array([67,197])  # Atualizado
GAI2v  =   np.array([97,197])  # Atualizado
GAI3v  =   np.array([97,317])  # Atualizado
GAI4v  =   np.array([67,317])  # Atualizado

# Área goleiro inimigo virtual
GE1v   =   np.array([502,152])  # Atualizado
GE2v   =   np.array([547,152])  # Atualizado
GE3v   =   np.array([547,362])  # Atualizado
GE4v   =   np.array([502,362])  # Atualizado

# Área interna do goleiro inimigo virtual
GEI1v  =   np.array([547,197])  # Atualizado
GEI2v  =   np.array([577,197])  # Atualizado
GEI3v  =   np.array([577,317])  # Atualizado
GEI4v  =   np.array([547,317])  # Atualizado

# Meios dos lados virtuais
fieldP12v  =   np.array([322,62])  # Atualizado
fieldP34v  =   np.array([322,452])  # Atualizado

# Posições dos jogadores para tomar como base
MID_GOALAREA_A = np.array([119.5,157.0])  # Atualizado
ATK1_POSITION_SITUATION1_ALLY = PA1v
ATK2_POSITION_SITUATION2_ALLY = PA3v

MID_GOALAREA_E = np.array([524.5,157.0])  # Atualizado
ATK1_POSITION_SITUATION1_ENEMY = PE1v

#Posições dos jogadores para tomar como base 
MID_GOALAREA_A = np.array([119.5,257.0])
ATK1_POSITION_SITUATION1_ALLY = PA1v
ATK2_POSITION_SITUATION2_ALLY = PA3v

MID_GOALAREA_E = np.array([524.5,257.0])
ATK1_POSITION_SITUATION1_ENEMY = PE1v
ATK2_POSITION_SITUATION2_ENEMY = PE3v


#Posições importante dos robôs na imagem:# Coordenadas relativas dos pontos "+" (em cm, baseadas no campo original)
RELATIVE_POSITIONS = [
    MID_GOALAREA_A,  # Exemplo: Goleiro aliado 1
    ATK1_POSITION_SITUATION1_ALLY,  # Exemplo: Atacante aliado 1
    ATK2_POSITION_SITUATION2_ALLY,  # Exemplo: Atacante Aliado 2
    MID_GOALAREA_E,  # Exemplo: Goleiro inimigo 1
    ATK1_POSITION_SITUATION1_ENEMY,  # Exemplo: atacante inimigo 1
    ATK2_POSITION_SITUATION2_ENEMY,  # Exemplo: Atacante inimigo 2
]

# ============================
# Parâmetros da física do simulador
# ============================

#Tipos de objetos do sistema
ROBOT_OBJECT = "ROBOT"
BALL_OBJECT = "BALL"
FIELD_OBJECT = "FIELD"
LINE_OBJECT  = "LINE"
POINT_OBJECT = "POINT"

#Tipos de jogadores 
GOALKEEPER = "GOALKEEPER" #goleiro
ATACKER = "ATTACKER"    #atacante

#Coeficientes de restituição das colisões (e)
COEFFICIENT_RESTITUTION_BALL_ROBOT = 0.6  # Colisão bola-robô
COEFFICIENT_RESTITUTION_BALL_FIELD = 0.8  # Colisão bola-campo
COEFFICIENT_RESTITUTION_ROBOT_ROBOT = 0.4  # Colisão robô-robô 
COEFFICIENT_RESTITUTION_ROBOT_FIELD = 0.0 # Colisão robô-campo (sem restituição)


#Coeficiente de Arrasto para a bola