# ============================================================
# FoxSIM - Arquivo de Configurações da Simulação de Futebol de Robôs
# Este arquivo centraliza constantes, parâmetros e funções auxiliares
# para configuração da simulação, como dimensões do campo, cores,
# física dos objetos, e conversões de coordenadas.
#
# Por: Saulo José Almeida Silva
# ============================================================
VERSION = 1.2

# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------
import numpy as np
from enum import Enum
import json 
import os
from simulator.objects.robot import BotRoles, BotId

# ==============================| ENUMERAÇÕES PADRÕES DA SIMULAÇÃO | =============================
# Categorizar eventos no sistema (Apenas uma ideia)
class EventType(Enum):
    GOAL_SCORED = "goal"
    COLLISION = "collision"
    SIMULATION_START = "sim_start"
    ROBOT_STUCK = "robot_stuck"
    PENALTY = "penalty"

class SimulatorVariables:
    def __init__(self):
        # Parâmetros padrão iniciais — serão sobrescritos se os arquivos forem carregados com sucesso
        self.FPS = 60
        self.party_time = 60
        self.vel_sim = 1

        self.robot_length = 8.0
        self.robot_max = 1.0
        self.robot_max_speed = 100
        self.robot_max_ang_speed = 25
        self.robot_wheels_distance = 8.0
        self.robot_wheels_radius = 6.0

        self.ball_radius = 2.135
        self.ball_mass = 0.045
        self.ball_max_speed = 95

        self.fric_rr = 0.01
        self.fric_rf = 0.92
        self.fric_bw = 0.58
        self.fric_br = 0.95

        self.rest_rb = 0.95
        self.rest_rr = 0.6
        self.rest_bf = 0.8

        self.visual_debug = True
        self.has_logs = True

        self.PID_dist_kp = 6.0
        self.PID_dist_ki = 0.0
        self.PID_dist_kd = 0.5

        self.PID_angle_kp = 4.0
        self.PID_angle_ki = 0.1
        self.PID_angle_kd = 0.1

        self.PID_final_angle_kp = 1.0
        self.PID_final_angle_ki = 0.5
        self.PID_final_angle_kd = -0.5

    def load_all_configs(self,
                         param_path="src/data/temp/ParamSimu.json",
                         bot_path="src/data/temp/BotConf.json",
                         pid_path="src/data/temp/PIDvar.json"):
        """
        Carrega todos os parâmetros de simulação.
        Retorna: (has_error: bool, error_message: str)
        """
        erros = []

        if not self.get_param_simu(param_path):
            erros.append("Erro ao carregar o arquivo: ParamSimu.json")

        if not self.get_Bot_conf(bot_path):
            erros.append("Erro ao carregar o arquivo: BotConf.json")

        if not self.get_PID_cont(pid_path):
            erros.append("Erro ao carregar o arquivo: PIDvar.json")

        if erros:
            return (True, f"Erro ao carregar arquivos de configuração: {', '.join(erros)}. Usando valores padrão.")
        
        return (False, "")

    def get_param_simu(self, path: str) -> bool:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.FPS = data.get("fps", self.FPS)
                self.party_time = data.get("tempo_partida", self.party_time)
                self.vel_sim = data.get("velocidade_simulacao", self.vel_sim)
                self.fric_rr = data.get("fric_rr", self.fric_rr)
                self.fric_rf = data.get("fric_rf", self.fric_rf)
                self.fric_bw = data.get("fric_bw", self.fric_bw)
                self.fric_br = data.get("fric_br", self.fric_br)
                self.rest_rb = data.get("rest_rb", self.rest_rb)
                self.rest_rr = data.get("rest_rr", self.rest_rr)
                self.rest_bf = data.get("rest_bf", self.rest_bf)
                self.visual_debug = data.get("debug", self.visual_debug)
                self.has_logs = data.get("logs", self.has_logs)
            return True
        except Exception:
            return False

    def get_Bot_conf(self, path: str) -> bool:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.robot_length = data.get("robot_length", self.robot_length)
                self.robot_max = data.get("robot_mass", self.robot_max)
                self.robot_max_speed = data.get("robot_max_speed", self.robot_max_speed)
                self.robot_max_ang_speed = data.get("robot_max_ang_speed", self.robot_max_ang_speed)
                self.robot_wheels_distance = data.get("wheel_distance", self.robot_wheels_distance)
                self.robot_wheels_radius = data.get("wheel_radius", self.robot_wheels_radius)
                self.ball_radius = data.get("ball_radius", self.ball_radius)
                self.ball_mass = data.get("ball_mass", self.ball_mass)
                self.ball_max_speed = data.get("ball_max_speed", self.ball_max_speed)
            return True
        except Exception:
            return False

    def get_PID_cont(self, path: str) -> bool:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                pid = data.get("pid", {})
                dist = pid.get("dist", [])
                angle = pid.get("angle", [])
                final_angle = pid.get("final_angle", [])

                if len(dist) == 3:
                    self.PID_dist_kp = float(dist[0])
                    self.PID_dist_ki = float(dist[1])
                    self.PID_dist_kd = float(dist[2])

                if len(angle) == 3:
                    self.PID_angle_kp = float(angle[0])
                    self.PID_angle_ki = float(angle[1])
                    self.PID_angle_kd = float(angle[2])

                if len(final_angle) == 3:
                    self.PID_final_angle_kp = float(final_angle[0])
                    self.PID_final_angle_ki = float(final_angle[1])
                    self.PID_final_angle_kd = float(final_angle[2])
            return True
        except Exception:
            return False

class ObjectTypes(Enum):
    '''
        Tipos de objetos de colisão
    '''
    MOVING_OBJECTS = "MOVING"
    STRUCTURE_OBJECTS = "STRUCTURE"

    def __str__(self):
        return self
    
class ObjectSimulationTypes(Enum):
    '''
        Tipos de objetos da simulação
    '''
    # TIPOS DE OBJETOS DO JOGO
    ROBOT_OBJECT = "ROBOT"
    BALL_OBJECT = "BALL"
    FIELD_OBJECT = "FIELD"
    LINE_OBJECT = "LINE"
    POINT_OBJECT = "POINT"

    # Tipos de estruturas para lógica
    # TIPOS DE ESTRUTURAS PARA LÓGICA
    POSSIBLE_BOAL_PUT_OBJECT = "PUT_BALL"
    ALLY_GOAL_OBJECT = "ALLY_GOAL"
    ENEMY_GOAL_OBJECT = "ENEMY_GOAL"

    #IDENTIFCADORES DAS ÁREAS
    GOALKEEPER_AREA_OBJECT_ALLY = "GOALKEEPER_AREA"
    GOALKEEPER_AREA_OBJECT_ENEMY = "GOALKEEPER_AREA_ENEMY"

    def __str__(self):
        return self
    
# ------------------------------------------------------------
# CONFIGURAÇÕES DA JANELA
# ------------------------------------------------------------
ORIGIN_SYSTEM_PX    = np.array([int(1.2*67), int(1.2*452)])     # Origem do sistema de coordenadas (px)

# ------------------------------------------------------------
# ESCALAS E DIMENSÕES DO CAMPO (REAL E EM PIXELS)
# ------------------------------------------------------------
# Tamanho da tela na simulação
SCREEN_WIDTH_IN_PX  = int(1.2*645)
SCREEN_HEIGHT_IN_PX = int(1.2*645)

# VALOR EM PIXELS DA IMAGEM DO CAMPO
FIELD_INTERNAL_WIDTH_IN_PX = int(450*1.2) #Tamanho novo do campo
FIELD_INTERNAL_HEIGHT_IN_PX = int(390*1.2)

# VALOR REAL EM CENTÍMETROS DAS DIMENSÕES DO CAMPO
REAL_FIELD_INTERNAL_WIDTH_CM = int(150)
REAL_FIELD_INTERNAL_HEIGHT_CM = int(130)

#ESCALA DE CONVERSÃO DE PX PARA CM
SCALE_PX_TO_CM = REAL_FIELD_INTERNAL_WIDTH_CM / (FIELD_INTERNAL_WIDTH_IN_PX)

# ------------------------------------------------------------
# FUNÇÕES DE CONVERSÃO DE COORDENADAS
# ------------------------------------------------------------

def _v2s_(pos_cm):
    '''
        Transforma das coordenadas da screen para as coordenadas
        da simulação.
    '''
    x_px = int((pos_cm[0] / SCALE_PX_TO_CM)+ ORIGIN_SYSTEM_PX[0])
    y_px = int((-pos_cm[1] / SCALE_PX_TO_CM) + ORIGIN_SYSTEM_PX[1])
    return np.array([x_px, y_px])

def _s2v_(pos_px):
    '''
        Transforma das coordenada da simulação para as coordenadas da screen
        para desenhar sem problemas.
    '''
    x_cm = (pos_px[0] - ORIGIN_SYSTEM_PX[0]) *SCALE_PX_TO_CM
    y_cm = -(pos_px[1] - ORIGIN_SYSTEM_PX[1]) *SCALE_PX_TO_CM
    return np.array([x_cm, y_cm])

def _v2s_direction_(vector_cm):
    return np.array([vector_cm[0], -vector_cm[1]])

def _rot_Vec_(v, angle_degrees):
    angle_rad = np.radians(angle_degrees)
    rotation_matrix = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad)],
        [np.sin(angle_rad),  np.cos(angle_rad)]
    ])
    v = np.array(v)
    return rotation_matrix @ v

# ------------------------------------------------------------
# CONFIGURAÇÕES DOS GOLS
# ------------------------------------------------------------
GOAL_WIDTH = int(10)
GOAL_HEIGHT = int(40)

# ------------------------------------------------------------
# POSIÇÃO INICIAL DA BOLA (VIRTUAL)
# ------------------------------------------------------------
XBALL_INIT = SCREEN_WIDTH_IN_PX // 2
YBALL_INIT = SCREEN_HEIGHT_IN_PX // 2
XVBALL_INIT, YVBALL_INIT = _s2v_([XBALL_INIT, YBALL_INIT])

# ------------------------------------------------------------
# GRID PARA DETECÇÃO DE COLISÕES (SPATIAL HASHING)
# ------------------------------------------------------------
# Essa parte pode ser construída dentro da simulação nova
ROBOT_AREA  = 8 * 8
CELL_AREA   = 4 * ROBOT_AREA
CELL_SIZE   = int(np.sqrt(CELL_AREA))

GRID_ROWS           = FIELD_INTERNAL_HEIGHT_IN_PX // CELL_SIZE
GRID_COLS           = FIELD_INTERNAL_WIDTH_IN_PX // CELL_SIZE
QUANT_CELLS_GRID    = (GRID_COLS, GRID_ROWS)
GRID_COLOR          = (255, 0, 0)

# ------------------------------------------------------------
# COORDENADAS VIRTUAIS DOS PONTOS DE REFERÊNCIA
# ------------------------------------------------------------
# Pivots virtuais
PA1v   =   _s2v_(np.array([210,137]))  # Atualizado
PA2v   =   _s2v_(np.array([210,257]))  # Atualizado
PA3v   =   _s2v_(np.array([210,377]))  # Atualizado
PE1v   =   _s2v_(np.array([435,137]))  # Atualizado
PE2v   =   _s2v_(np.array([435,257]))  # Atualizado
PE3v   =   _s2v_(np.array([435,377]))  # Atualizado

# Área goleiro aliado virtual
GA1v   =   _s2v_(np.array([97,152]))  # Atualizado
GA2v   =   _s2v_(np.array([142,152]))  # Atualizado
GA3v   =   _s2v_(np.array([142,362]))  # Atualizado
GA4v   =   _s2v_(np.array([97,362]))  # Atualizado

# Área interna do goleiro aliado virtual
GAI1v  =   _s2v_(np.array([67,197]))  # Atualizado
GAI2v  =   _s2v_(np.array([97,197]))  # Atualizado
GAI3v  =   _s2v_(np.array([97,317]))  # Atualizado
GAI4v  =   _s2v_(np.array([67,317]))  # Atualizado

# Área goleiro inimigo virtual
GE1v   =   _s2v_(np.array([502,152]))  # Atualizado
GE2v   =   _s2v_(np.array([547,152]))  # Atualizado
GE3v   =   _s2v_(np.array([547,362]))  # Atualizado
GE4v   =   _s2v_(np.array([502,362]))  # Atualizado

# Área interna do goleiro inimigo virtual
GEI1v  =   _s2v_(np.array([547,197]))  # Atualizado
GEI2v  =   _s2v_(np.array([577,197]))  # Atualizado
GEI3v  =   _s2v_(np.array([577,317]))  # Atualizado
GEI4v  =   _s2v_(np.array([547,317]))  # Atualizado

# Meios dos lados virtuais
fieldP12v  =   _s2v_(np.array([322,62]))  # Atualizado
fieldP34v  =   _s2v_(np.array([322,452]))  # Atualizado

#Extremos do Campo maior
fieldEx1= _s2v_(np.array([97,62]))
fieldEx2= _s2v_(np.array([547,62]))
fieldEx3= _s2v_(np.array([547,452]))
fieldEx4= _s2v_(np.array([97,452]))

#Centro do campo
fieldC = _s2v_(np.array([322, 257]))  # Atualizado

# Quinas do campo
Q1A1v = _s2v_(np.array([97,62+21]))
Q1A2v = _s2v_(np.array([97+21,62]))

Q2A1v = _s2v_(np.array([547-21,62]))
Q2A2v = _s2v_(np.array([547,62+21]))

Q3A1v = _s2v_(np.array([547,452-21]))
Q3A2v = _s2v_(np.array([547-21,452]))

Q4A1v = _s2v_(np.array([97+21,452]))
Q4A2v = _s2v_(np.array([97,452-21]))


# Posições dos jogadores para tomar como base
MID_GOALAREA_A = _s2v_(np.array([119.5,257.0]))  # Atualizado
ATK1_POSITION_SITUATION1_ALLY = PA1v
ATK2_POSITION_SITUATION2_ALLY = PA3v

MID_GOALAREA_E = _s2v_(np.array([524.5,257.0]))  # Atualizado
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
    [BotId.GK,MID_GOALAREA_A],                     # Exemplo: Goleiro aliado 1
    [BotId.ATK1,ATK1_POSITION_SITUATION1_ALLY],      # Exemplo: Atacante aliado 1
    [BotId.ATK2,ATK2_POSITION_SITUATION2_ALLY],      # Exemplo: Atacante Aliado 2
    [BotId.GK,MID_GOALAREA_E],                     # Exemplo: Goleiro inimigo 1
    [BotId.ATK1,ATK1_POSITION_SITUATION1_ENEMY],     # Exemplo: atacante inimigo 1
    [BotId.ATK2,ATK2_POSITION_SITUATION2_ENEMY],     # Exemplo: Atacante inimigo 2
]
