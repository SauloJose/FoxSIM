import numpy as np

# ============================
# Configurações da Janela
# ============================
WINDOW_WIDTH            = 645  # Largura da janela em pixels
WINDOW_HEIGHT           = 600  # Altura da janela em pixels

## Todas essas posições são dadas em pixels
ORIGIN_SYSTEM_PX = np.array([67,452])       # Coordenada do ponto de origem do novo sistema de coordenadas

# ============================
# Configurações da área útil da janela do campo. Considerando espaços que não tem campo.
# ============================
ORIGINAL_WINDOWS_FIELD_WIDTH_PX     = 645  # Largura original do campo em cm
ORIGINAL_WINDOWS_FIELD_HEIGHT_PX    = 413  # Altura original do campo em cm
WINDOWS_FIELD_WIDTH_PX              = 645  # Largura do campo em pixels
SCALE_CM2PX                         = WINDOWS_FIELD_WIDTH_PX / ORIGINAL_WINDOWS_FIELD_WIDTH_PX 
WINDOWS_FIELD_HEIGHT_PX             = int(ORIGINAL_WINDOWS_FIELD_HEIGHT_PX * SCALE_CM2PX)  # Altura do campo em pixels (escalada)

FIELD_INTERNAL_HEIGHT_IN_PX   = 390 # px
FIELD_INTERNAL_WIDTH_IN_PX    = 450 # px

REAL_FIELD_INTERNAL_WIDTH_CM  = int(150)  ##centimetros
REAL_FIELD_INTERNAL_HEIGHT_CM = int(130)  ## centímetros

# ====================  Escala para transformar de pixéls para centímetros
SCALE_PX_TO_CM              = REAL_FIELD_INTERNAL_WIDTH_CM/FIELD_INTERNAL_WIDTH_IN_PX #= 0,333 cm/px
#===========================================================================================
# Definição de funções para passar de coordenadas na interface (desenho) para coordenadas virtuais (cálculos)

## Funções para transformar pontos virtuais e indices da imagem
def virtual_to_screen(pos_cm):
    """
    Converte posição do campo (em cm) para posição na tela (em pixels).
    `pos_cm` deve ser um np.array([x, y]) em centímetros.

    
    """
    x_px = int((pos_cm[0] / SCALE_PX_TO_CM) + ORIGIN_SYSTEM_PX[0])
    y_px = int((-pos_cm[1] / SCALE_PX_TO_CM) + ORIGIN_SYSTEM_PX[1])
    return np.array([x_px, y_px])

# um ponto na interface para o espaço virtual
def screen_to_virtual(pos_px):  
    """
    Converte posição da tela (em pixels) para posição no campo virtual (em cm).
    `pos_px` deve ser um np.array([x, y]) em pixels.

    Resumo: pega um ponto na tela e transforma para as coordenadas adequadas
    virtualizadas e com boa aproximação.

    return: 
        np.array([x_cm,y_cm])
    """
    x_cm = (pos_px[0] - ORIGIN_SYSTEM_PX[0])*SCALE_PX_TO_CM
    y_cm = -(pos_px[1] - ORIGIN_SYSTEM_PX[1])*SCALE_PX_TO_CM

    return np.array([x_cm, y_cm])

# Função para transformar vetores, visto que mudou o eixo y
def virtual_direction_to_screen(vector_cm):
    return np.array([vector_cm[0], -vector_cm[1]])
# ==================== Distâncias para desenhos.
PADDING_BALL_OK_CM            = 2
PADDING_BALL_OK_PX            = PADDING_BALL_OK_CM/SCALE_PX_TO_CM

# ============================
# Configurações das Áreas
# ============================
SCOREBOARD_HEIGHT_PX       = 50  # Altura do placar em pixels
SIDEBAR_WIDTH_PX           = 400  # Largura das janelas laterais em pixels
CONFIG_HEIGHT_PX           = 160  # Altura da área de configurações em pixels

# ============================
# Configurações dos Gols
# ============================
GOAL_WIDTH              = int(10)  # Largura do gol em pixels (10cm escalados)
GOAL_HEIGHT             = int(40)  # Altura do gol em pixels (40cm escalados)



# ============================
# Cores
# ============================
FIELD_COLOR             = (144, 238, 144)  # Cor do campo (verde claro)
LINE_COLOR              = (255, 255, 255)  # Cor das linhas do campo (branco)

# Cores dos times
TEAM_BLUE_COLOR         = (0, 0, 255)  # Cor do time azul
TEAM_RED_COLOR          = (255, 0, 0)  # Cor do time vermelho

# Cores do placar
SCOREBOARD_COLOR        = (50, 50, 50)  # Cor do fundo do placar (cinza escuro)

# Cores das janelas laterais
SIDEBAR_COLOR_1         = (100, 100, 100)  # Cor da Janela 1 (cinza médio)
SIDEBAR_COLOR_2         = (150, 150, 150)  # Cor da Janela 2 (cinza claro)

# Cor da área de configurações
CONFIG_COLOR            = (30, 30, 30)  # Cor do fundo da área de configurações (cinza muito escuro)

# ============================
# Configurações dos Botões (px)
# ============================
BUTTON_WIDTH            = 120  # Largura dos botões em pixels
BUTTON_HEIGHT           = 50  # Altura dos botões em pixels
BUTTON_SPACING          = 10  # Espaçamento entre os botões em pixels

# ============================
# Configurações do Fundo
# ============================
BACKGROUND_COLOR        = (0, 0, 0)  # Cor do fundo (preto)


#====================== Posições Iniciais em coordenada virtul
#Bola
# Posições iniciais no virtual:
XBALL_INIT = WINDOWS_FIELD_WIDTH_PX // 2
YBALL_INIT = SCOREBOARD_HEIGHT_PX + WINDOWS_FIELD_HEIGHT_PX // 2
XVBALL_INIT, YVBALL_INIT = screen_to_virtual([XBALL_INIT, YBALL_INIT])

# Campo


# Robôes

# ============================
# Dados físicos do simulador 
# ============================
# massa (kg), distancias (cm)
# Dos robôs
ROBOT_MASS                                 = 0.5                            # Massa do robô em kg
ROBOT_SIZE_CM                              = 8.0                            # Largura das laterais  cm
ROBOT_WHEELS_RADIUS_CM                     = 4                              # Raio da roda em pixels (3cm escalados)
ROBOT_DISTANCE_WHEELS_CM                   = 7                              # Distância entre as rodas em pixels (10cm escalados)
ROBOT_DISTANCE_WHEELS_TO_CENTER_CM         = ROBOT_DISTANCE_WHEELS_CM/2     # Distância do centro do robô até o meio das rodas em pixels (5cm escalados)


# Da bola
BALL_MASS               = 0.045  # Massa da bola em kg (100g)
BALL_RADIUS_CM          = 2.135  # Raio da bola em cm (5cm escalados)
BALL_COLOR              = (255, 165, 0)  # Cor da bola (laranja)


#Coeficientes de restituição das colisões (e)
COEFFICIENT_RESTITUTION_BALL_ROBOT      = 0.6  # Colisão bola-robô
COEFFICIENT_RESTITUTION_BALL_FIELD      = 0.8  # Colisão bola-campo
COEFFICIENT_RESTITUTION_ROBOT_ROBOT     = 0.4  # Colisão robô-robô 
COEFFICIENT_RESTITUTION_ROBOT_FIELD     = 0.0 # Colisão robô-campo (sem restituição

COEFICIENT_FRICTION_ROBOT_FIELD         = 0.1 # Coeficiente de atrito robô-campo (sem atrito)
COEFICIENT_FRICTION_ROBOT_ROBOT         = 0.1 # Coeficiente de atrito robô-robô (sem atrito)


# ============================ Configurações dos grids para detecção =====================================
#Quantidades de Células do GRID.
ROBOT_AREA                              = ROBOT_SIZE_CM*ROBOT_SIZE_CM 
CELL_AREA                               = 4 *ROBOT_AREA           # Suportar até 4 robôs num mesmo grid.
CELL_SIZE                               = int(np.sqrt(CELL_AREA)) 

GRID_ROWS                               = FIELD_INTERNAL_HEIGHT_IN_PX // CELL_SIZE
GRID_COLS                               = FIELD_INTERNAL_WIDTH_IN_PX // CELL_SIZE
QUANT_CELLS_GRID                        = (GRID_COLS, GRID_ROWS)


GRID_COLOR                              = (255,0,0)
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
FIELD_INTERNAL_WIDTH_IN_PX = WINDOWS_FIELD_WIDTH_PX - FIELD_MARGIN_LEFT - FIELD_MARGIN_RIGHT
FIELD_INTERNAL_HEIGHT_IN_PX = WINDOWS_FIELD_HEIGHT_PX - FIELD_MARGIN_TOP - FIELD_MARGIN_BOTTOM


## ========== Coordenadas dos pontos de referência na imagem para gerar os objetos
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

#Posições importante dos robôs na imagem:# Coordenadas relativas dos pontos "+" (em cm, baseadas no campo original)
RELATIVE_POSITIONS = [
    MID_GOALAREA_A,                     # Exemplo: Goleiro aliado 1
    ATK1_POSITION_SITUATION1_ALLY,      # Exemplo: Atacante aliado 1
    ATK2_POSITION_SITUATION2_ALLY,      # Exemplo: Atacante Aliado 2
    MID_GOALAREA_E,                     # Exemplo: Goleiro inimigo 1
    ATK1_POSITION_SITUATION1_ENEMY,     # Exemplo: atacante inimigo 1
    ATK2_POSITION_SITUATION2_ENEMY,     # Exemplo: Atacante inimigo 2
]

# ============================
# Parâmetros da física do simulador
# ============================
#TIPOS PRIMORDIAIS DE OBJETOS PARA A COLISÃO
MOVING_OBJECTS = "MOVING"
STRUCTURE_OBJECTS = "STRUCTURE"

#Tipos de objetos do sistema
ROBOT_OBJECT = "ROBOT"
BALL_OBJECT = "BALL"
FIELD_OBJECT = "FIELD"
LINE_OBJECT  = "LINE"
POINT_OBJECT = "POINT"

#Áreas para contagens de ponto (Tipos de objetos)
POSSIBLE_BOAL_PUT_OBJECT = "PUT_BALL"
ALLY_GOAL_OBJECT = "ALLY_GOAL"
ENEMY_GOAL_OBJECT = "ENEMY_GOAL"

#Áreas para garantir a posição dos goleiros
GOALKEEPER_AREA_OBJECT_ALLY = "GOALKEEPER_AREA"
GOALKEEPER_AREA_OBJECT_ENEMY = "GOALKEEPER_AREA_ENEMY"

#Tipos de jogadores 
GOALKEEPER = "GOALKEEPER" #goleiro
ATACKER = "ATTACKER"    #atacante

# Contabilizadores de pontos para indicar funcionamento do jogo
NO_POINT_YET = 0 
POINT_ALLY = 1
POINT_ENEMY = 2
