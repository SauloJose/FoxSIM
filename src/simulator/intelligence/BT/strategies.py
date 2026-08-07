from .bt_core import Selector, Sequence
from .bt_conditions import *
from .bt_actions import *
from ui.interface_config import GOALKEEPER, ATACKER1, ATACKER2, MID_GOALAREA_E, MID_GOALAREA_A, fieldC

# =============================================================================
# CONSTANTES FÍSICAS E DE COMPORTAMENTO
# =============================================================================
# --- PARÂMETROS DO GOLEIRO ---
GK_EMERGENCY_SPIN_DIST = 6.5 
GK_EMERGENCY_SPIN_SPEED = 85.0 
GK_INTERCEPT_DIST = 25.0 
GK_MAX_OUT_DIST = 25.0

# --- PARÂMETROS DO ATACANTE ---
# CORRIGIDO: Margem aumentada para considerar o raio da bola (2.13cm) + folga
ATK_WALL_MARGIN = 4.5      # Margem de segurança da parede (em cm)
ATK_WALL_SPIN_DIST = 7.0    # Distância para iniciar o giro (maior que o raio físico do robô)
ATK_WALL_SPIN_SPEED = 85.0  # Velocidade de rotação para tirar a bola da parede

# --- PARÂMETROS DO SUPORTE ---
SUP_SPEED = 15.0  # Velocidade máxima de aproximação do suporte
SUP_AVOID_RADIUS = 15.0  # Raio de desvio proativo de outros robôs durante o suporte
SUP_AVOID_WEIGHT = 2.5   # Peso da repulsão frente à atração pela bola no suporte

# --- MULTIPLICADORES DE PERFIL ---
PROFILE_AGGRESSIVE_MULT = 1.4
PROFILE_BALANCED_MULT = 1.0
PROFILE_DEFENSIVE_MULT = 0.8

# --- PARÂMETROS DE RECUPERAÇÃO / ANTI-TRAVAMENTO (CORREÇÃO 1) ---
TANGLE_MIN_DIST = 6.0        # Distância abaixo da qual consideramos colisão com outro robô
TANGLE_BALL_IGNORE_DIST = 18.0  # Se a bola estiver mais perto que isso, não foge da disputa (limiar que ignora a recuperação)
RECOVERY_INFLUENCE_RADIUS = 25.0  # Raio de influência do campo potencial de repulsão
RECOVERY_ESCAPE_SPEED = 20.0      # Velocidade máxima ao fugir de uma colisão

# --- PARÂMETROS DE HISTERESE DE PAPEL (CORREÇÃO 4) ---
CLOSEST_TO_BALL_HYSTERESIS = 5.0

# --- LIMITES DE CAMPO E GIRO DIRECIONADO (CORREÇÃO 6) ---
# Usados para decidir o sentido do giro em SpinClearanceNode, garantindo que
# a bola seaja sempre empurrada para longe do gol (goleiro) ou da parede/canto
# (atacantes), nunca na direção contrária.
FIELD_BOUNDS = (0.0, fieldC[0] * 2.0, 0.0, fieldC[1] * 2.0)
WALL_ESCAPE_MARGIN = 20.0


class TeamStrategy:
    def __init__(self, enemy_goal_pos=MID_GOALAREA_E, ally_goal_x=MID_GOALAREA_A[0]):
        self.enemy_goal_pos = enemy_goal_pos
        self.ally_goal_x = ally_goal_x

    def create_goalkeeper_tree(self):
        ally_goal_x = self.ally_goal_x


        def gk_escape_direction(robot, ball, team, enemy_team):
            return goal_escape_direction(ally_goal_x, fieldC[0])

        return Selector([
            Sequence([
                IsTangledWithRobot(min_dist=TANGLE_MIN_DIST, ball_ignore_dist=TANGLE_BALL_IGNORE_DIST),
                PotentialFieldAvoidNode(influence_radius=RECOVERY_INFLUENCE_RADIUS, escape_speed=RECOVERY_ESCAPE_SPEED)
            ]),
            # 1. Chute de emergência se a bola estiver colada no goleiro
            Sequence([
                IsBallWithinDistance(max_distance=GK_EMERGENCY_SPIN_DIST),
                SpinClearanceNode(spin_speed=GK_EMERGENCY_SPIN_SPEED, away_direction_fn=gk_escape_direction)
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

        def wall_escape(robot, ball, team, enemy_team):
            return wall_escape_direction(ball.position, FIELD_BOUNDS, margin=WALL_ESCAPE_MARGIN)

        return Selector([
            Sequence([
                IsTangledWithRobot(min_dist=TANGLE_MIN_DIST, ball_ignore_dist=TANGLE_BALL_IGNORE_DIST),
                PotentialFieldAvoidNode(influence_radius=RECOVERY_INFLUENCE_RADIUS, escape_speed=RECOVERY_ESCAPE_SPEED)
            ]),

            Sequence([
                IsClosestToBall(hysteresis=CLOSEST_TO_BALL_HYSTERESIS),
                Selector([
                    # A. SE A BOLA ESTIVER NA PAREDE: Chega perto e gira para soltar
                    Sequence([
                        IsBallNearWall(margin=ATK_WALL_MARGIN),
                        IsBallWithinDistance(max_distance=ATK_WALL_SPIN_DIST),
                        SpinClearanceNode(spin_speed=ATK_WALL_SPIN_SPEED, away_direction_fn=wall_escape)
                    ]),
                    
                    # B. CONDUÇÃO NORMAL: Se a bola estiver livre no campo
                    # (agora com pontos-alvo sempre clampados aos limites do
                    # campo e checagem de lado, evitando alvos inalcançáveis)
                    SmartPushToGoalNode(
                        enemy_goal_pos=self.enemy_goal_pos,
                        ally_goal_x=self.ally_goal_x,
                        aggressiveness_multiplier=aggressiveness
                    )
                ])
            ]),

            # =========================================================================
            # SUPORTE / SEGUNDO JOGADOR (Fallback obrigatório para o 2º atacante)
            # =========================================================================
            SupportAttackNode(
                ally_goal_x=self.ally_goal_x,
                enemy_goal_pos=self.enemy_goal_pos,
                support_speed=SUP_SPEED,
                avoid_radius=SUP_AVOID_RADIUS,
                avoid_weight=SUP_AVOID_WEIGHT
            )
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
                trees[robot.id_robot] = self.factory.create_attacker_tree(aggressiveness=agg)
                
        return trees