from .bt_core import Selector, Sequence
from .bt_conditions import *
from .bt_actions import *
from ui.interface_config import GOALKEEPER, ATACKER1, ATACKER2, MID_GOALAREA_E, MID_GOALAREA_A, fieldC

# =============================================================================
# CONSTANTES FÍSICAS E DE COMPORTAMENTO
# =============================================================================
GK_EMERGENCY_SPIN_DIST = 6.5 
GK_EMERGENCY_SPIN_SPEED = 85.0 
GK_INTERCEPT_DIST = 25.0 
GK_MAX_OUT_DIST = 25.0

ATK_WALL_MARGIN = 4.5      
ATK_WALL_SPIN_DIST = 7.0    
ATK_WALL_SPIN_SPEED = 85.0  

SUP_SPEED = 15.0  
SUP_AVOID_RADIUS = 0        # Desativado (era 15.0)
SUP_AVOID_WEIGHT = 0.0      # Desativado (era 2.5)

PROFILE_AGGRESSIVE_MULT = 1.4
PROFILE_BALANCED_MULT = 1.0
PROFILE_DEFENSIVE_MULT = 0.8

TANGLE_MIN_DIST = 8.0        
TANGLE_BALL_IGNORE_DIST = 18.0  
RECOVERY_ESCAPE_SPEED = 5.0      # Para o ReverseNode (não usado no APF)

CLOSEST_TO_BALL_HYSTERESIS = 10.0   # Aumentado de 5.0 para 10.0

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
            # Recuperação de colisão: agora usa ReverseNode (ré simples) em vez de APF
            Sequence([
                IsTangledWithRobot(min_dist=TANGLE_MIN_DIST, ball_ignore_dist=TANGLE_BALL_IGNORE_DIST),
                ReverseNode(reverse_speed=RECOVERY_ESCAPE_SPEED)
            ]),
            Sequence([
                IsBallWithinDistance(max_distance=GK_EMERGENCY_SPIN_DIST),
                SpinClearanceNode(spin_speed=GK_EMERGENCY_SPIN_SPEED, away_direction_fn=gk_escape_direction)
            ]),
            Sequence([
                IsBallWithinDistance(max_distance=GK_INTERCEPT_DIST),
                IsBallInGKZone(ally_goal_x=self.ally_goal_x, max_dist_x=GK_MAX_OUT_DIST),
                InterceptBallNode() 
            ]),
            DefendGoalNode(goal_x=self.ally_goal_x)
        ])

    def _recovery_branch(self):
        return Sequence([
            IsTangledWithRobot(
                min_dist=TANGLE_MIN_DIST,
                ball_ignore_dist=TANGLE_BALL_IGNORE_DIST,
            ),
            ReverseNode(reverse_speed=RECOVERY_ESCAPE_SPEED),
        ])

    def _wall_escape_branch(self):
        def wall_escape(robot, ball, team, enemy_team):
            return wall_escape_direction(
                ball.position,
                FIELD_BOUNDS,
                margin=WALL_ESCAPE_MARGIN,
            )

        return Sequence([
            IsBallNearWall(margin=ATK_WALL_MARGIN),
            IsBallWithinDistance(max_distance=ATK_WALL_SPIN_DIST),
            SpinClearanceNode(
                spin_speed=ATK_WALL_SPIN_SPEED,
                away_direction_fn=wall_escape,
            ),
        ])

    def _primary_attacker_branch(self, aggressiveness):
        return Sequence([
            IsClosestToBall(hysteresis=CLOSEST_TO_BALL_HYSTERESIS),
            Selector([
                self._wall_escape_branch(),
                SimplePushToGoalNode(
                    enemy_goal_pos=self.enemy_goal_pos,
                    push_dist=18.0,
                    approach_dist=12.0,
                    speed_mult=aggressiveness,
                ),
            ]),
        ])

    def _support_branch(self):
        return SupportAttackNode(
            ally_goal_x=self.ally_goal_x,
            enemy_goal_pos=self.enemy_goal_pos,
            support_speed=SUP_SPEED,
            avoid_radius=SUP_AVOID_RADIUS,
            avoid_weight=SUP_AVOID_WEIGHT,
        )

    def create_attacker_tree(self, aggressiveness=PROFILE_BALANCED_MULT):
        """Monta a árvore de um atacante a partir de comportamentos nomeados."""
        return Selector([
            self._recovery_branch(),
            self._primary_attacker_branch(aggressiveness),
            self._support_branch(),
        ])

    def create_tree_for_robot(self, robot, aggressiveness=PROFILE_BALANCED_MULT):
        """Seleciona a árvore pelo papel do robô."""
        if robot.role == GOALKEEPER:
            return self.create_goalkeeper_tree()
        if robot.role in (ATACKER1, ATACKER2):
            return self.create_attacker_tree(aggressiveness)
        raise ValueError(f"Papel de robô não suportado: {robot.role}")


class StrategyManager:
    """Constrói uma árvore independente para cada robô de uma equipe."""

    def __init__(self, profile="balanced", factory=None):
        self.factory = factory or TeamStrategy()
        self.profile = profile

    def build_trees_for_team(self, robots):
        agg = PROFILE_BALANCED_MULT
        if self.profile == "aggressive":
            agg = PROFILE_AGGRESSIVE_MULT
        elif self.profile == "defensive":
            agg = PROFILE_DEFENSIVE_MULT

        return {
            robot.id_robot: self.factory.create_tree_for_robot(
                robot,
                aggressiveness=agg,
            )
            for robot in robots
        }