# src/intelligence/strategies.py
from .bt_core import Selector, Sequence
from .bt_conditions import *
from .bt_actions import *
from ui.interface_config import GOALKEEPER, ATACKER1, ATACKER2, MID_GOALAREA_E, MID_GOALAREA_A

# =============================================================================
# CONSTANTES FÍSICAS E DE COMPORTAMENTO
# =============================================================================
# --- PARÂMETROS DO GOLEIRO ---
GK_EMERGENCY_SPIN_DIST = 6.5 
GK_EMERGENCY_SPIN_SPEED = 85.0 
GK_INTERCEPT_DIST = 25.0 
GK_MAX_OUT_DIST = 25.0

# --- PARÂMETROS DO ATACANTE ---
ATK_WALL_MARGIN = 5.5 
ATK_WALL_SPIN_DIST = 6.5 
ATK_WALL_SPIN_SPEED = 70.0 

# --- PARÂMETROS DO SUPORTE ---
SUP_DISTANCE = 25.0 

# --- MULTIPLICADORES DE PERFIL ---
PROFILE_AGGRESSIVE_MULT = 1.3
PROFILE_BALANCED_MULT = 1.0
PROFILE_DEFENSIVE_MULT = 0.8


class TeamStrategy:
    def __init__(self, enemy_goal_pos=MID_GOALAREA_E, ally_goal_x=MID_GOALAREA_A[0]):
        self.enemy_goal_pos = enemy_goal_pos
        self.ally_goal_x = ally_goal_x

    def create_goalkeeper_tree(self):
        return Selector([
            # 1. Chute de emergência se a bola estiver colada no goleiro
            Sequence([
                IsBallWithinDistance(max_distance=GK_EMERGENCY_SPIN_DIST),
                SpinClearanceNode(spin_speed=GK_EMERGENCY_SPIN_SPEED) 
            ]),
            # 2. Interceptação curta na pequena área
            Sequence([
                IsBallWithinDistance(max_distance=GK_INTERCEPT_DIST),
                IsBallInGKZone(ally_goal_x=self.ally_goal_x, max_dist_x=GK_MAX_OUT_DIST),
                InterceptBallNode() 
            ]),
            # 3. Patrulha na linha do gol
            DefendGoalNode(goal_x=self.ally_goal_x)
        ])

    def create_attacker_tree(self, aggressiveness=PROFILE_BALANCED_MULT):
        return Selector([
            # =========================================================================
            # PRIORIDADE ABSOLUTA: ATACANTE VAI DIRETO PARA A BOLA
            # =========================================================================
            # Se for o mais próximo da bola, ele navega e empurra a bola em direção ao gol
            Sequence([
                IsClosestToBall(),
                SmartPushToGoalNode(self.enemy_goal_pos, aggressiveness_multiplier=aggressiveness)
            ]),

            # =========================================================================
            # AJUDANTE / SUPORTE
            # =========================================================================
            # Se não for o mais próximo, posiciona-se taticamente em suporte
            SupportAttackNode(ally_goal_x=self.ally_goal_x, support_distance=SUP_DISTANCE)
        ])


class StrategyManager:
    def __init__(self, profile="balanced"):
        self.factory = TeamStrategy()
        self.profile = profile

    def build_trees_for_team(self, robots):
        trees = {}
        
        agg = PROFILE_BALANCED_MULT
        if self.profile == "aggressive":
            agg = PROFILE_AGGRESSIVE_MULT
        elif self.profile == "defensive":
            agg = PROFILE_DEFENSIVE_MULT

        for robot in robots:
            if robot.role == GOALKEEPER:
                trees[robot.id_robot] = self.factory.create_goalkeeper_tree()
            elif robot.role in [ATACKER1, ATACKER2]:
                trees[robot.id_robot] = self.factory.create_attacker_tree(aggressiveness=agg)
            else:
                trees[robot.id_robot] = self.factory.create_attacker_tree()
                
        return trees