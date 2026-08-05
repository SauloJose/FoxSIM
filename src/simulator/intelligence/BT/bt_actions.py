# src/intelligence/bt_actions.py
import numpy as np
from .bt_core import Node, Status
# Importa o centro do campo e o centro da área do goleiro aliado
from ui.interface_config import fieldC, MID_GOALAREA_A 

class DefendGoalNode(Node):
    """
    Goleiro patrulha a linha do gol acompanhando a bola no eixo Y.
    """
    def __init__(self, goal_x=MID_GOALAREA_A[0], goal_y_center=MID_GOALAREA_A[1]):
        self.goal_x = goal_x
        self.goal_y_center = goal_y_center

    def tick(self, robot, ball, team, enemy_team, dt):
        # Limita o Y usando as traves virtuais (aproximadamente +- 20cm do centro)
        target_y = np.clip(ball.y, self.goal_y_center - 20, self.goal_y_center + 20)
        target_pos = np.array([self.goal_x, target_y])
        
        v_l, v_r = robot.go_to_point(target_pos, target_angle=np.pi/2, dt=dt, allow_reverse=True)
        robot.set_wheel_speeds(v_l, v_r)
        
        return Status.RUNNING

class InterceptBallNode(Node):
    """
    Goleiro abandona a linha do gol e vai direto na bola para rebatê-la.
    """
    def tick(self, robot, ball, team, enemy_team, dt):
        v_l, v_r = robot.go_to_point(ball.position, target_angle=None, dt=dt)
        robot.set_wheel_speeds(v_l, v_r)
        return Status.RUNNING

class PushToGoalNode(Node):
    """
    Atacante persegue a bola para tentar empurrá-la para o gol adversário.
    """
    def __init__(self, enemy_goal_pos, aggressiveness_multiplier=1.0):
        self.enemy_goal_pos = np.array(enemy_goal_pos)
        self.agg_mult = aggressiveness_multiplier

    def tick(self, robot, ball, team, enemy_team, dt):
        v_l, v_r = robot.go_to_point(ball.position, target_angle=None, dt=dt)
        robot.set_wheel_speeds(v_l * self.agg_mult, v_r * self.agg_mult)
        return Status.RUNNING

class SupportAttackNode(Node):
    """
    Atacante secundário aguarda sobra no centro do campo.
    """
    def __init__(self, wait_x=fieldC[0]):
        self.wait_x = wait_x

    def tick(self, robot, ball, team, enemy_team, dt):
        target_pos = np.array([self.wait_x, ball.y])
        v_l, v_r = robot.go_to_point(target_pos, target_angle=0.0, dt=dt)
        robot.set_wheel_speeds(v_l, v_r)
        return Status.RUNNING