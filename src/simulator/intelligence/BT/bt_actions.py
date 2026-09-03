import math
import numpy as np
from .bt_core import Node, Status
from ui.interface_config import fieldC, MID_GOALAREA_A, GOALKEEPER, ATACKER1, ATACKER2
from ..basicControl import go_to_point
from ..errt import *

def is_closest_field_robot(robot, ball, team, hysteresis=5.0):
    """
    Verifica se o robô atual é o mais próximo da bola entre os atacantes de linha (ATACKER1 e ATACKER2).
    O goleiro (GOALKEEPER) é totalmente ignorado nesta avaliação.
    """
    if getattr(robot, 'role', None) == GOALKEEPER:
        return False

    field_attackers = [
        t for t in team
        if getattr(t, 'role', None) in [ATACKER1, ATACKER2]
    ]
    
    if not field_attackers:
        return True

    my_dist = robot.distance_to(ball.x, ball.y)
    
    other_dists = [
        t.distance_to(ball.x, ball.y) 
        for t in field_attackers 
        if t.id_robot != robot.id_robot
    ]
    
    if not other_dists:
        return True
        
    return my_dist < (min(other_dists) + hysteresis)


class DefendGoalNode(Node):
    def __init__(self, goal_x=MID_GOALAREA_A[0], goal_y_center=MID_GOALAREA_A[1], goal_width=40.0):
        self.goal_x = goal_x
        self.goal_y_center = goal_y_center
        self.y_min = goal_y_center - (goal_width / 2.0)
        self.y_max = goal_y_center + (goal_width / 2.0)

    def tick(self, robot, ball, team, enemy_team, dt):
        target_y = np.clip(ball.y, self.y_min, self.y_max)
        target_pos = np.array([self.goal_x, target_y])
        target_angle = 0.0 if self.goal_x < fieldC[0] else math.pi

        dist_to_target = np.linalg.norm(target_pos - robot.position)
        
        if dist_to_target > 5.0:
            v_l, v_r = robot.go_to_point(target_pos, target_angle=target_angle, dt=dt)
            robot.set_wheel_speeds(v_l, v_r)
        else:
            current_angle = robot.body.angle 
            angle_error = target_angle - current_angle
            angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))
            kp_spin = 40.0 
            spin_speed = angle_error * kp_spin
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
        vec_to_goal = self.enemy_goal_pos - ball.position
        target_angle = math.atan2(vec_to_goal[1], vec_to_goal[0])
        v_l, v_r = robot.go_to_point(ball.position, target_angle=target_angle, dt=dt)
        robot.set_wheel_speeds(v_l * self.agg_mult, v_r * self.agg_mult)
        return Status.RUNNING


def goal_escape_direction(ally_goal_x, field_center_x):
    return np.array([1.0, 0.0]) if ally_goal_x < field_center_x else np.array([-1.0, 0.0])


def wall_escape_direction(ball_pos, field_bounds, margin=20.0):
    x_min, x_max, y_min, y_max = field_bounds
    bx, by = ball_pos[0], ball_pos[1]
    push = np.array([0.0, 0.0])

    dist_left = bx - x_min
    dist_right = x_max - bx
    dist_bottom = by - y_min
    dist_top = y_max - by

    if dist_left < margin:
        push += np.array([1.0, 0.0]) * (margin - dist_left)
    if dist_right < margin:
        push += np.array([-1.0, 0.0]) * (margin - dist_right)
    if dist_bottom < margin:
        push += np.array([0.0, 1.0]) * (margin - dist_bottom)
    if dist_top < margin:
        push += np.array([0.0, -1.0]) * (margin - dist_top)

    if np.linalg.norm(push) < 1e-6:
        cx, cy = (x_min + x_max) / 2.0, (y_min + y_max) / 2.0
        push = np.array([cx - bx, cy - by])

    return push


def compute_repulsion_vector(robot_pos, robot_id, all_robots, influence_radius, min_dist_safety=3.0):
    repulsion = np.array([0.0, 0.0])
    for obs in all_robots:
        if obs.id_robot == robot_id:
            continue
        delta = robot_pos - obs.position
        dist = np.linalg.norm(delta)
        if dist < 1e-6:
            delta = np.array([1.0, 0.0])
            dist = min_dist_safety
        if dist < influence_radius:
            dist_safe = max(dist, min_dist_safety)
            magnitude = (influence_radius - dist_safe) / influence_radius
            repulsion += (delta / dist_safe) * magnitude
    return repulsion


class ReverseNode(Node):
    def __init__(self, reverse_speed=60.0):
        self.reverse_speed = reverse_speed

    def tick(self, robot, ball, team, enemy_team, dt):
        robot.set_wheel_speeds(-self.reverse_speed, -self.reverse_speed, priority=True)
        return Status.RUNNING


class PotentialFieldAvoidNode(Node):
    """
    Nó de recuperação de colisão baseado em campo potencial repulsivo.
    (Não será mais utilizado, mantido apenas para compatibilidade.)
    """
    def __init__(self, influence_radius=25.0, escape_speed=45.0, min_dist_safety=3.0):
        self.influence_radius = influence_radius
        self.escape_speed = escape_speed
        self.min_dist_safety = min_dist_safety

    def tick(self, robot, ball, team, enemy_team, dt):
        robot_pos = robot.position
        all_robots = team + enemy_team

        repulsion = compute_repulsion_vector(
            robot_pos, robot.id_robot, all_robots,
            self.influence_radius, self.min_dist_safety
        )

        norm_rep = np.linalg.norm(repulsion)

        if norm_rep < 1e-6:
            center = np.array([fieldC[0], fieldC[1]])
            escape_dir = center - robot_pos
            if np.linalg.norm(escape_dir) < 1e-6:
                escape_dir = np.array([1.0, 0.0])
            else:
                escape_dir = escape_dir / np.linalg.norm(escape_dir)
            target_pos = robot_pos + escape_dir * self.influence_radius
        else:
            escape_dir = repulsion / norm_rep
            target_pos = robot_pos + escape_dir * self.influence_radius

        v_l, v_r = robot.go_to_point(target_pos, target_angle=None, dt=dt)
        v_l = np.clip(v_l, -self.escape_speed, self.escape_speed)
        v_r = np.clip(v_r, -self.escape_speed, self.escape_speed)

        robot.set_wheel_speeds(v_l, v_r, priority=True)
        return Status.RUNNING


class SupportAttackNode(Node):
    """
    Fica orientado para a bola e avança lentamente na direção dela para dar apoio.
    A repulsão proativa pode ser desativada definindo avoid_weight <= 0.
    """
    def __init__(self, ally_goal_x, enemy_goal_pos=MID_GOALAREA_A, support_speed=5.0,
                 avoid_radius=20.0, avoid_weight=1.5, min_dist_safety=3.0):
        self.ally_goal_x = ally_goal_x
        self.enemy_goal_pos = np.array(enemy_goal_pos)
        self.support_speed = support_speed
        self.avoid_radius = avoid_radius
        self.avoid_weight = avoid_weight
        self.min_dist_safety = min_dist_safety

    def tick(self, robot, ball, team, enemy_team, dt):
        robot_pos = robot.position

        delta_y = ball.y - robot.y
        delta_x = ball.x - robot.x
        target_angle = math.atan2(delta_y, delta_x)

        vec_to_ball = ball.position - robot_pos
        dist_to_ball = np.linalg.norm(vec_to_ball)
        attraction_dir = vec_to_ball / dist_to_ball if dist_to_ball > 1e-6 else np.array([0.0, 0.0])

        # Repulsão só é calculada se o peso for positivo
        if self.avoid_weight > 0 and self.avoid_radius > 0:
            all_robots = team + enemy_team
            repulsion = compute_repulsion_vector(
                robot_pos, robot.id_robot, all_robots,
                self.avoid_radius, self.min_dist_safety
            )
        else:
            repulsion = np.array([0.0, 0.0])

        combined = attraction_dir + repulsion * self.avoid_weight
        norm_combined = np.linalg.norm(combined)
        norm_repulsion = np.linalg.norm(repulsion)

        if norm_combined > 1e-6:
            combined_dir = combined / norm_combined
        else:
            combined_dir = attraction_dir

        lookahead = min(dist_to_ball, 40.0) if dist_to_ball > 1e-6 else 0.0
        target_pos = robot_pos + combined_dir * lookahead

        # Se houver repulsão, não forçar ângulo para evitar travamento
        if norm_repulsion > 1e-3:
            target_angle = None

        v_l, v_r = robot.go_to_point(target_pos, target_angle=target_angle, dt=dt)
        v_l = np.clip(v_l, -self.support_speed, self.support_speed)
        v_r = np.clip(v_r, -self.support_speed, self.support_speed)

        robot.set_wheel_speeds(v_l, v_r)
        return Status.RUNNING


class SpinClearanceNode(Node):
    def __init__(self, spin_speed=80.0, away_direction_fn=None):
        self.spin_speed = abs(spin_speed)
        self.away_direction_fn = away_direction_fn

    def tick(self, robot, ball, team, enemy_team, dt):
        speed = self.spin_speed
        clockwise = False

        if self.away_direction_fn is not None:
            away_dir = np.asarray(self.away_direction_fn(robot, ball, team, enemy_team), dtype=float)
            r_vec = ball.position - robot.position

            norm_away = np.linalg.norm(away_dir)
            norm_r = np.linalg.norm(r_vec)

            if norm_away > 1e-6 and norm_r > 1e-6:
                r_hat = r_vec / norm_r
                away_hat = away_dir / norm_away

                ccw_push_dir = np.array([-r_hat[1], r_hat[0]])
                cw_push_dir = np.array([r_hat[1], -r_hat[0]])

                ccw_score = np.dot(ccw_push_dir, away_hat)
                cw_score = np.dot(cw_push_dir, away_hat)

                clockwise = cw_score > ccw_score

        if clockwise:
            robot.set_wheel_speeds(speed, -speed, priority=True)
        else:
            robot.set_wheel_speeds(-speed, speed, priority=True)

        return Status.RUNNING


# =============================================================================
# NOVO NÓ SIMPLIFICADO PARA O ATACANTE PRINCIPAL (SUBSTITUI SmartPushToGoalNode)
# =============================================================================
class SimplePushToGoalNode(Node):
    """
    Ação direta e sem planejamento para o atacante principal:
      - Se estiver perto da bola (<= push_dist), empurra em direção ao gol.
      - Senão, vai para trás da bola (approach_dist) sem forçar ângulo,
        evitando travamentos por orientação.
    """
    def __init__(self, enemy_goal_pos, push_dist=18.0, approach_dist=12.0, speed_mult=1.0):
        self.enemy_goal_pos = np.array(enemy_goal_pos)
        self.push_dist = push_dist
        self.approach_dist = approach_dist
        self.speed_mult = speed_mult

    def tick(self, robot, ball, team, enemy_team, dt):
        ball_pos = ball.position
        robot_pos = robot.position
        dist = np.linalg.norm(ball_pos - robot_pos)

        vec_goal = self.enemy_goal_pos - ball_pos
        norm = np.linalg.norm(vec_goal)
        if norm > 1e-6:
            dir_goal = vec_goal / norm
        else:
            dir_goal = np.array([1.0, 0.0])  # fallback

        if dist <= self.push_dist:
            # Empurra a bola para frente (um pouco à frente da bola)
            target = ball_pos + dir_goal * 15.0
            angle = math.atan2(dir_goal[1], dir_goal[0])
            v_l, v_r = robot.go_to_point(target, target_angle=angle, dt=dt)
        else:
            # Posiciona-se atrás da bola sem forçar ângulo (evita girar em falso)
            target = ball_pos - dir_goal * self.approach_dist
            v_l, v_r = robot.go_to_point(target, target_angle=None, dt=dt)

        robot.set_wheel_speeds(v_l * self.speed_mult, v_r * self.speed_mult)
        return Status.RUNNING