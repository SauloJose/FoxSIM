# ============================================================
# FoxSIM - Arquivo de Configurações da Simulação de Futebol de Robôs
# Este arquivo centraliza constantes, parâmetros e funções auxiliares
# para configuração da simulação, como dimensões do campo, cores,
# física dos objetos, e conversões de coordenadas.
# ============================================================

# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------
import numpy as np

#VERSÃO ATUAL DO CÓDIGO
VERSION = 0.7363

# ------------------------------------------------------------
# CONFIGURAÇÕES DA JANELA
# ------------------------------------------------------------
WINDOW_WIDTH = 645                         # Largura da janela (px)
WINDOW_HEIGHT = 600                        # Altura da janela (px)
ORIGIN_SYSTEM_PX = np.array([67, 452])     # Origem do sistema de coordenadas (px)

# ------------------------------------------------------------
# ESCALAS E DIMENSÕES DO CAMPO (REAL E EM PIXELS)
# ------------------------------------------------------------
# COMPRIMENTOS PARA UTILIZAR NA JANELA
ORIGINAL_WINDOWS_FIELD_WIDTH_PX = 645
ORIGINAL_WINDOWS_FIELD_HEIGHT_PX = 413
WINDOWS_FIELD_WIDTH_PX = 645
SCALE_CM2PX = WINDOWS_FIELD_WIDTH_PX / ORIGINAL_WINDOWS_FIELD_WIDTH_PX
WINDOWS_FIELD_HEIGHT_PX = int(ORIGINAL_WINDOWS_FIELD_HEIGHT_PX * SCALE_CM2PX)

# VALOR EM PIXELS DA IMAGEM DO CAMPO
FIELD_INTERNAL_WIDTH_IN_PX = 450
FIELD_INTERNAL_HEIGHT_IN_PX = 390

# VALOR REAL EM CENTÍMETROS DAS DIMENSÕES DO CAMPO
REAL_FIELD_INTERNAL_WIDTH_CM = int(150)
REAL_FIELD_INTERNAL_HEIGHT_CM = int(130)

#ESCALA DE CONVERSÃO DE PX PARA CM
SCALE_PX_TO_CM = REAL_FIELD_INTERNAL_WIDTH_CM / FIELD_INTERNAL_WIDTH_IN_PX

# ------------------------------------------------------------
# FUNÇÕES DE CONVERSÃO DE COORDENADAS
# ------------------------------------------------------------
def virtual_to_screen(pos_cm):
    x_px = int((pos_cm[0] / SCALE_PX_TO_CM) + ORIGIN_SYSTEM_PX[0])
    y_px = int((-pos_cm[1] / SCALE_PX_TO_CM) + ORIGIN_SYSTEM_PX[1])
    return np.array([x_px, y_px])

def screen_to_virtual(pos_px):
    x_cm = (pos_px[0] - ORIGIN_SYSTEM_PX[0]) * SCALE_PX_TO_CM
    y_cm = -(pos_px[1] - ORIGIN_SYSTEM_PX[1]) * SCALE_PX_TO_CM
    return np.array([x_cm, y_cm])

def virtual_direction_to_screen(vector_cm):
    return np.array([vector_cm[0], -vector_cm[1]])

def rotate_vector(v, angle_degrees):
    angle_rad = np.radians(angle_degrees)
    rotation_matrix = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad)],
        [np.sin(angle_rad),  np.cos(angle_rad)]
    ])
    v = np.array(v)
    return rotation_matrix @ v

# ------------------------------------------------------------
# ELEMENTOS DE INTERFACE E ESTÉTICA
# ------------------------------------------------------------
PADDING_BALL_OK_CM = 3.5
PADDING_BALL_OK_PX = int(PADDING_BALL_OK_CM / SCALE_PX_TO_CM)

#IDENTIFICADOR DA PONTUAÇÃO
SCOREBOARD_HEIGHT_PX = 50
SIDEBAR_WIDTH_PX = 400
CONFIG_HEIGHT_PX = 160

#BUTÃO
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 50
BUTTON_SPACING = 10

#CORES
BACKGROUND_COLOR = (0, 0, 0)
FIELD_COLOR = (144, 238, 144)
LINE_COLOR = (255, 255, 255)
TEAM_BLUE_COLOR = (0, 0, 255)
TEAM_RED_COLOR = (255, 0, 0)
SCOREBOARD_COLOR = (50, 50, 50)
SIDEBAR_COLOR_1 = (100, 100, 100)
SIDEBAR_COLOR_2 = (150, 150, 150)
CONFIG_COLOR = (30, 30, 30)

# ------------------------------------------------------------
# CONFIGURAÇÕES DOS GOLS
# ------------------------------------------------------------
GOAL_WIDTH = int(10)
GOAL_HEIGHT = int(40)

# ------------------------------------------------------------
# POSIÇÃO INICIAL DA BOLA (VIRTUAL)
# ------------------------------------------------------------
XBALL_INIT = WINDOWS_FIELD_WIDTH_PX // 2
YBALL_INIT = SCOREBOARD_HEIGHT_PX + WINDOWS_FIELD_HEIGHT_PX // 2
XVBALL_INIT, YVBALL_INIT = screen_to_virtual([XBALL_INIT, YBALL_INIT])

# ------------------------------------------------------------
# DADOS FÍSICOS DO ROBÔ E BOLA
# ------------------------------------------------------------
#ROBÔ
ROBOT_MASS = 0.7
ROBOT_SIZE_CM = 8.0
ROBOT_WHEELS_RADIUS_CM = 4.0
ROBOT_DISTANCE_WHEELS_CM = 8.0
ROBOT_DISTANCE_WHEELS_TO_CENTER_CM = ROBOT_DISTANCE_WHEELS_CM / 2
ROBOT_MAX_SPEED = 10

#BOLA
BALL_MASS = 0.045
BALL_RADIUS_CM = 2.135
BALL_COLOR = (255, 165, 0)


#COEFICIENTES DE RESTITUIÇÃO
COEFFICIENT_RESTITUTION_BALL_ROBOT = 0.95
COEFFICIENT_RESTITUTION_BALL_FIELD = 0.8
COEFFICIENT_RESTITUTION_ROBOT_ROBOT = 0.6
COEFFICIENT_RESTITUTION_ROBOT_FIELD = 0.2

#COEFICIENTES DE ATRITO
COEFICIENT_FRICTION_ROBOT_FIELD = 0.06
COEFICIENT_FRICTION_ROBOT_ROBOT = 0.01
COEFICIENT_FRICTION_BALL_FIELD = 0.0001
COEFICIENT_FRICTION_BALL_ROBOT = 0.3

# Máximo impulso do simulador.
MAX_IMPULSE = 10000 #(cm/s)*kg

# ------------------------------------------------------------
# GRID PARA DETECÇÃO DE COLISÕES (SPATIAL HASHING)
# ------------------------------------------------------------
ROBOT_AREA = ROBOT_SIZE_CM * ROBOT_SIZE_CM
CELL_AREA = 4 * ROBOT_AREA
CELL_SIZE = int(np.sqrt(CELL_AREA))

GRID_ROWS = FIELD_INTERNAL_HEIGHT_IN_PX // CELL_SIZE
GRID_COLS = FIELD_INTERNAL_WIDTH_IN_PX // CELL_SIZE
QUANT_CELLS_GRID = (GRID_COLS, GRID_ROWS)
GRID_COLOR = (255, 0, 0)

# ------------------------------------------------------------
# CONFIGURAÇÕES DE EXIBIÇÃO E TEMPO DE JOGO
# ------------------------------------------------------------
FPS = 144
TIMER_PARTY = 60

FIELD_MARGIN_TOP = 20
FIELD_MARGIN_BOTTOM = 20
FIELD_MARGIN_LEFT = 20
FIELD_MARGIN_RIGHT = 20

# ------------------------------------------------------------
# COORDENADAS VIRTUAIS DOS PONTOS DE REFERÊNCIA
# ------------------------------------------------------------
# Pivots virtuais
PA1v   =   screen_to_virtual(np.array([210,137]))  # Atualizado
PA2v   =   screen_to_virtual(np.array([210,257]))  # Atualizado
PA3v   =   screen_to_virtual(np.array([210,377]))  # Atualizado
PE1v   =   screen_to_virtual(np.array([435,137]))  # Atualizado
PE2v   =   screen_to_virtual(np.array([435,257]))  # Atualizado
PE3v   =   screen_to_virtual(np.array([435,377]))  # Atualizado

# Área goleiro aliado virtual
GA1v   =   screen_to_virtual(np.array([97,152]))  # Atualizado
GA2v   =   screen_to_virtual(np.array([142,152]))  # Atualizado
GA3v   =   screen_to_virtual(np.array([142,362]))  # Atualizado
GA4v   =   screen_to_virtual(np.array([97,362]))  # Atualizado

# Área interna do goleiro aliado virtual
GAI1v  =   screen_to_virtual(np.array([67,197]))  # Atualizado
GAI2v  =   screen_to_virtual(np.array([97,197]))  # Atualizado
GAI3v  =   screen_to_virtual(np.array([97,317]))  # Atualizado
GAI4v  =   screen_to_virtual(np.array([67,317]))  # Atualizado

# Área goleiro inimigo virtual
GE1v   =   screen_to_virtual(np.array([502,152]))  # Atualizado
GE2v   =   screen_to_virtual(np.array([547,152]))  # Atualizado
GE3v   =   screen_to_virtual(np.array([547,362]))  # Atualizado
GE4v   =   screen_to_virtual(np.array([502,362]))  # Atualizado

# Área interna do goleiro inimigo virtual
GEI1v  =   screen_to_virtual(np.array([547,197]))  # Atualizado
GEI2v  =   screen_to_virtual(np.array([577,197]))  # Atualizado
GEI3v  =   screen_to_virtual(np.array([577,317]))  # Atualizado
GEI4v  =   screen_to_virtual(np.array([547,317]))  # Atualizado

# Meios dos lados virtuais
fieldP12v  =   screen_to_virtual(np.array([322,62]))  # Atualizado
fieldP34v  =   screen_to_virtual(np.array([322,452]))  # Atualizado

#Extremos do Campo maior
fieldEx1= screen_to_virtual(np.array([97,62]))
fieldEx2= screen_to_virtual(np.array([547,62]))
fieldEx3= screen_to_virtual(np.array([547,452]))
fieldEx4= screen_to_virtual(np.array([97,452]))

#Centro do campo
fieldC = screen_to_virtual(np.array([322, 257]))  # Atualizado

# Quinas do campo
Q1A1v = screen_to_virtual(np.array([97,62+21]))
Q1A2v = screen_to_virtual(np.array([97+21,62]))

Q2A1v = screen_to_virtual(np.array([547-21,62]))
Q2A2v = screen_to_virtual(np.array([547,62+21]))

Q3A1v = screen_to_virtual(np.array([547,452-21]))
Q3A2v = screen_to_virtual(np.array([547-21,452]))

Q4A1v = screen_to_virtual(np.array([97+21,452]))
Q4A2v = screen_to_virtual(np.array([97,452-21]))

# LIMITES INFERIOR E SUPERIOR PARA ÁREA QUE POSSO COLOCAR A BOLA
BALL_INIT_MIN_X, BALL_INIT_MIN_Y = 97, 62
BALL_INIT_MAX_X, BALL_INIT_MAX_Y = 547, 452



# Posições dos jogadores para tomar como base
MID_GOALAREA_A = screen_to_virtual(np.array([119.5,257.0]))  # Atualizado
ATK1_POSITION_SITUATION1_ALLY = PA1v
ATK2_POSITION_SITUATION2_ALLY = PA3v

MID_GOALAREA_E = screen_to_virtual(np.array([524.5,257.0]))  # Atualizado
ATK1_POSITION_SITUATION1_ENEMY = PE1v
ATK2_POSITION_SITUATION2_ENEMY = PE3v


# ROLES DOS JOGADORES
GOALKEEPER = "GOALKEEPER"
ATACKER1 = "ATTACKER1"
ATACKER2 = "ATTACKER2"

#Cor dos times
BLUE_TEAM = "BLUE"
RED_TEAM = "RED"


#Posições importante dos robôs na imagem:# Coordenadas relativas dos pontos "+" (em cm, baseadas no campo original)
RELATIVE_POSITIONS = [
    [GOALKEEPER,MID_GOALAREA_A],                     # Exemplo: Goleiro aliado 1
    [ATACKER1,ATK1_POSITION_SITUATION1_ALLY],      # Exemplo: Atacante aliado 1
    [ATACKER2,ATK2_POSITION_SITUATION2_ALLY],      # Exemplo: Atacante Aliado 2
    [GOALKEEPER,MID_GOALAREA_E],                     # Exemplo: Goleiro inimigo 1
    [ATACKER1,ATK1_POSITION_SITUATION1_ENEMY],     # Exemplo: atacante inimigo 1
    [ATACKER2,ATK2_POSITION_SITUATION2_ENEMY],     # Exemplo: Atacante inimigo 2
]


# ------------------------------------------------------------
# TIPOS DE OBJETOS E ESTADOS PARA LÓGICA DE COLISÃO E PONTUAÇÃO
# ------------------------------------------------------------
# TIPOS DE OBJETO DE COLISÃO
MOVING_OBJECTS = "MOVING"
STRUCTURE_OBJECTS = "STRUCTURE"

# TIPOS DE OBJETOS DO JOGO
ROBOT_OBJECT = "ROBOT"
BALL_OBJECT = "BALL"
FIELD_OBJECT = "FIELD"
LINE_OBJECT = "LINE"
POINT_OBJECT = "POINT"


# TIPOS DE ESTRUTURAS PARA LÓGICA
POSSIBLE_BOAL_PUT_OBJECT = "PUT_BALL"
ALLY_GOAL_OBJECT = "ALLY_GOAL"
ENEMY_GOAL_OBJECT = "ENEMY_GOAL"

#IDENTIFCADORES DAS ÁREAS
GOALKEEPER_AREA_OBJECT_ALLY = "GOALKEEPER_AREA"
GOALKEEPER_AREA_OBJECT_ENEMY = "GOALKEEPER_AREA_ENEMY"


# Situação da partida
NO_POINT_YET = 0
POINT_ALLY = 1
POINT_ENEMY = 2