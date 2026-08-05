# src/intelligence/bt_actions.py
import math
import numpy as np
from .bt_core import Node, Status
from ui.interface_config import fieldC, MID_GOALAREA_A 
from ..errt import *

class DefendGoalNode(Node):
    def __init__(self, goal_x=MID_GOALAREA_A[0], goal_y_center=MID_GOALAREA_A[1], goal_width=40.0):
        self.goal_x = goal_x
        self.y_min = goal_y_center - (goal_width / 2.0)
        self.y_max = goal_y_center + (goal_width / 2.0)

    def tick(self, robot, ball, team, enemy_team, dt):
        target_y = np.clip(ball.y, self.y_min, self.y_max)
        target_pos = np.array([self.goal_x, target_y])
        
        # 1. Calcula a distância do robô até a posição ideal na linha do gol
        dist_to_target = np.linalg.norm(target_pos - robot.position)
        
        # 2. Se estiver longe (mais de 5 cm), prioriza correr para a posição
        if dist_to_target > 5.0:
            v_l, v_r = robot.go_to_point(target_pos, target_angle=None, dt=dt)
            robot.set_wheel_speeds(v_l, v_r)
            
        # 3. Se já estiver na posição, foca em GIRAR para olhar a bola
        else:
            delta_y = ball.y - robot.y
            delta_x = ball.x - robot.x
            target_angle = math.atan2(delta_y, delta_x)
            
            # Pega o ângulo atual do robô (assumindo que seja robot.theta no seu simulador)
            current_angle = robot.body.angle 
            
            # Calcula o erro angular e normaliza para o intervalo [-pi, pi]
            # Isso impede que o robô dê uma volta completa atoa
            angle_error = target_angle - current_angle
            angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))
            
            # Controlador P (Proporcional) para o giro. 
            # Multiplicamos o erro por uma força (Kp) para definir a velocidade da roda.
            kp_spin = 40.0 
            spin_speed = angle_error * kp_spin
            
            # Para girar no próprio eixo, uma roda vai pra frente e a outra pra trás
            robot.set_wheel_speeds(-spin_speed, spin_speed)
            
        return Status.RUNNING

class InterceptBallNode(Node):
    def tick(self, robot, ball, team, enemy_team, dt):
        v_l, v_r = robot.go_to_point(ball.position, target_angle=None, dt=dt)
        robot.set_wheel_speeds(v_l, v_r)
        
        return Status.RUNNING

class PushToGoalNode(Node):
    def __init__(self, enemy_goal_pos, aggressiveness_multiplier=1.0):
        self.enemy_goal_pos = np.array(enemy_goal_pos)
        self.agg_mult = aggressiveness_multiplier

    def tick(self, robot, ball, team, enemy_team, dt):
        v_l, v_r = robot.go_to_point(ball.position, target_angle=None, dt=dt)
        robot.set_wheel_speeds(v_l * self.agg_mult, v_r * self.agg_mult)
        
        return Status.RUNNING

class ReverseNode(Node):
    def __init__(self, reverse_speed=60.0):
        self.reverse_speed = reverse_speed

    def tick(self, robot, ball, team, enemy_team, dt):
        robot.set_wheel_speeds(-self.reverse_speed, -self.reverse_speed, priority=True)
        return Status.RUNNING

class SupportAttackNode(Node):
    def __init__(self, ally_goal_x, support_distance=70.0, field_width=150.0):
        self.ally_goal_x = ally_goal_x
        self.support_distance = support_distance
        self.field_width = field_width

    def tick(self, robot, ball, team, enemy_team, dt):
        if self.ally_goal_x < ball.x:
            target_x = ball.x - self.support_distance
        else:
            target_x = ball.x + self.support_distance
            
        target_x = np.clip(target_x, 15.0, self.field_width - 15.0)
        target_y = np.clip(ball.y, 15.0, 115.0) 
        
        target_pos = np.array([target_x, target_y])
        
        v_l, v_r = robot.go_to_point(target_pos, target_angle=None, dt=dt)
        robot.set_wheel_speeds(v_l, v_r)
        
        return Status.RUNNING

class SpinClearanceNode(Node):
    def __init__(self, spin_speed=80.0):
        self.spin_speed = spin_speed

    def tick(self, robot, ball, team, enemy_team, dt):
        robot.set_wheel_speeds(-self.spin_speed, self.spin_speed, priority=True)
        return Status.RUNNING

class SmartPushToGoalNode(Node):
    def __init__(self, enemy_goal_pos, aggressiveness_multiplier=1.0):
        self.enemy_goal_pos = np.array(enemy_goal_pos)
        self.agg_mult = aggressiveness_multiplier
        self.planner = ERRTPlanner()
        self.path = []
        self.replan_cooldown = 0
        self.push_engagement_dist = 18.0 

    def tick(self, robot, ball, team, enemy_team, dt):
        robot_pos = robot.position
        ball_pos = ball.position
        dist_to_ball = robot.distance_to(ball.x, ball.y)
        
        if dist_to_ball <= self.push_engagement_dist:
            vec_to_goal = self.enemy_goal_pos - ball_pos
            vec_to_goal = vec_to_goal / np.linalg.norm(vec_to_goal)
            
            target_pos = ball_pos + (vec_to_goal * 10.0)
            
            v_l, v_r = robot.go_to_point(target_pos, target_angle=None, dt=dt)
            robot.set_wheel_speeds(v_l * self.agg_mult, v_r * self.agg_mult)
            
            self.path = []
            return Status.RUNNING

        all_robots = team + enemy_team
        obstacles = [obs.position for obs in all_robots if obs.id_robot != robot.id_robot]
        
        vec_ball_to_goal = self.enemy_goal_pos - ball_pos
        dist_goal = np.linalg.norm(vec_ball_to_goal)
        dir_goal = vec_ball_to_goal / dist_goal if dist_goal > 0.1 else np.array([1.0, 0.0])
        approach_pos = ball_pos - (dir_goal * 10.0)
        
        self.replan_cooldown -= 1
        
        path_is_blocked = False
        if len(self.path) > 0:
            if not self.planner.is_collision_free(robot_pos, self.path[0], obstacles, safety_radius=14.0):
                path_is_blocked = True

        if self.replan_cooldown <= 0 or path_is_blocked or len(self.path) == 0:
            self.path = self.planner.plan(robot_pos, approach_pos, obstacles)
            self.replan_cooldown = 5 
            
        if len(self.path) > 0:
            next_waypoint = self.path[0]
            
            if np.linalg.norm(robot_pos - next_waypoint) < 8.0:
                self.path.pop(0)
                if len(self.path) > 0:
                    next_waypoint = self.path[0]
            
            v_l, v_r = robot.go_to_point(next_waypoint, target_angle=None, dt=dt)
            robot.set_wheel_speeds(v_l * self.agg_mult, v_r * self.agg_mult)
        else:
            v_l, v_r = robot.go_to_point(approach_pos, target_angle=None, dt=dt)
            robot.set_wheel_speeds(v_l * self.agg_mult, v_r * self.agg_mult)

        return Status.RUNNING