import math
import numpy as np
from .bt_core import Node, Status
from ui.interface_config import fieldC, MID_GOALAREA_A, GOALKEEPER, ATACKER1, ATACKER2
from ..errt import *

def is_closest_field_robot(robot, ball, team, hysteresis=5.0):
    """
    Verifica se o robô atual é o mais próximo da bola entre os atacantes de linha (ATACKER1 e ATACKER2).
    O goleiro (GOALKEEPER) é totalmente ignorado nesta avaliação.

    NOTA: esta função utilitária foi mantida para compatibilidade, mas a
    logica de historese usada de fato pela BT agora vive dentro de
    IsClosestToBall (bt_conditions.py), pois lá é possivel manter estado
    compartilhado entre os dois atacantes tick a tick.
    """
    # 1. Se o próprio robô for o goleiro, ele nunca assume papel de atacante de linha/suporte
    if getattr(robot, 'role', None) == GOALKEEPER:
        return False

    # 2. Filtra a equipe para considerar APENAS os atacantes de linha
    field_attackers = [
        t for t in team 
        if getattr(t, 'role', None) in [ATACKER1, ATACKER2] or getattr(t, 'role', None) != GOALKEEPER
    ]
    
    if not field_attackers:
        return True

    my_dist = robot.distance_to(ball.x, ball.y)
    
    # 3. Calcula a distância dos OUTROS atacantes de linha até a bola
    other_dists = [
        t.distance_to(ball.x, ball.y) 
        for t in field_attackers 
        if t.id_robot != robot.id_robot
    ]
    
    if not other_dists:
        return True
        
    # Retorna True se a distância do robô for menor que a do colega mais próximo
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
        
        # Aponta no sentido contrário de onde o gol está (olhando para dentro do campo)
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
    """
    Retorna a direção horizontal (não normalizada) que afasta a bola do
    próprio gol, para dentro do campo. Usa o mesmo critério já usado em
    DefendGoalNode: se o gol aliado está no lado esquerdo do campo, a
    direção segura é +x; se está no lado direito, é -x.
    """
    return np.array([1.0, 0.0]) if ally_goal_x < field_center_x else np.array([-1.0, 0.0])


def wall_escape_direction(ball_pos, field_bounds, margin=20.0):
    """
    Retorna uma direção (não normalizada) que afasta a bola da(s) parede(s)
    mais próxima(s). Perto de um canto, soma as contribuições dos dois eixos
    para não empurrar a bola de uma parede direto para a outra.
    """
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
        # Não está perto de nenhuma parede (não deveria acontecer já que
        # este nó só é chamado com IsBallNearWall == SUCCESS, mas por
        # segurança aponta para o centro do campo).
        cx, cy = (x_min + x_max) / 2.0, (y_min + y_max) / 2.0
        push = np.array([cx - bx, cy - by])

    return push


def compute_repulsion_vector(robot_pos, robot_id, all_robots, influence_radius, min_dist_safety=3.0):
    """
    Calcula o vetor de repulsão (campo potencial) de um robô em relação a
    todos os outros robôs dentro de influence_radius. Compartilhado entre
    PotentialFieldAvoidNode (recuperação reativa) e SupportAttackNode
    (desvio proativo durante o movimento normal).
    """
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
            # Sem vizinhos dentro do raio de influência — não deveria
            # acontecer logo após IsTangledWithRobot ter disparado, mas por
            # segurança apenas mantém o robô parado em vez de mover às cegas.
            robot.set_wheel_speeds(0.0, 0.0, priority=True)
            return Status.RUNNING

        escape_dir = repulsion / norm_rep
        target_pos = robot_pos + escape_dir * self.influence_radius

        v_l, v_r = robot.go_to_point(target_pos, target_angle=None, dt=dt)

        # Satura a velocidade de fuga para não criar uma nova colisão em
        # alta velocidade contra outro robô mais além.
        v_l = np.clip(v_l, -self.escape_speed, self.escape_speed)
        v_r = np.clip(v_r, -self.escape_speed, self.escape_speed)

        robot.set_wheel_speeds(v_l, v_r, priority=True)
        return Status.RUNNING


class SupportAttackNode(Node):
    """
    Fica orientado para a bola e avança lentamente na direção dela para dar
    apoio ao atacante principal.

    Além da atração pela bola, agora soma uma repulsão proativa (mesmo campo
    potencial usado em PotentialFieldAvoidNode) em relação a robôs próximos,
    para curvar o caminho e desviar deles ANTES de colidir — em vez de só
    reagir depois, quando IsTangledWithRobot/PotentialFieldAvoidNode já
    detectou contato. As duas camadas se complementam: esta é preventiva,
    aquela é o último recurso caso a colisão aconteça mesmo assim.
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

        # Mantém a orientação original: sempre de frente para a bola
        delta_y = ball.y - robot.y
        delta_x = ball.x - robot.x
        target_angle = math.atan2(delta_y, delta_x)

        # Direção de atração (rumo à bola)
        vec_to_ball = ball.position - robot_pos
        dist_to_ball = np.linalg.norm(vec_to_ball)
        attraction_dir = vec_to_ball / dist_to_ball if dist_to_ball > 1e-6 else np.array([0.0, 0.0])

        # Direção de repulsão (longe de robôs próximos)
        all_robots = team + enemy_team
        repulsion = compute_repulsion_vector(
            robot_pos, robot.id_robot, all_robots,
            self.avoid_radius, self.min_dist_safety
        )

        combined = attraction_dir + repulsion * self.avoid_weight
        norm_combined = np.linalg.norm(combined)
        norm_repulsion = np.linalg.norm(repulsion)

        if norm_combined > 1e-6:
            combined_dir = combined / norm_combined
        else:
            combined_dir = attraction_dir

        # Ponto-alvo "virtual": segue a direção combinada, limitado à
        # distância até a bola, para não mirar muito além dela.
        lookahead = min(dist_to_ball, 40.0) if dist_to_ball > 1e-6 else 0.0
        target_pos = robot_pos + combined_dir * lookahead

        # CORREÇÃO DO TRAVAMENTO: quando há repulsão significativa (robô
        # próximo de outro), não força mais o ângulo de chegada = direção da
        # bola. Se essa direção estiver longe do sentido de fuga necessário,
        # o robô tentava girar no lugar para alinhar antes de se mover,
        # travando visualmente. Nesse caso usamos target_angle=None (mesmo
        # padrão de InterceptBallNode) para priorizar sair do caminho do
        # obstáculo sem exigir um ângulo exato. Sem robôs por perto
        # (repulsão ~0), mantém o comportamento original de ficar de frente
        # para a bola.
        if norm_repulsion > 1e-3:
            target_angle = None
        # else: mantém o target_angle calculado acima (de frente para a bola)

        v_l, v_r = robot.go_to_point(target_pos, target_angle=target_angle, dt=dt)

        # Saturação de velocidade para aproximação lenta
        v_l = np.clip(v_l, -self.support_speed, self.support_speed)
        v_r = np.clip(v_r, -self.support_speed, self.support_speed)

        robot.set_wheel_speeds(v_l, v_r)
        return Status.RUNNING

class SpinClearanceNode(Node):
    """
    Gira o robô no lugar para tirar a bola de uma situação perigosa (colada
    no gol ou na parede).

    O SENTIDO do giro (horário ou anti-horário) não é mais fixo: é escolhido
    a cada tick de forma que o contato do robô com a bola a empurre para uma
    direção segura (away_direction_fn), nunca para o lado perigoso (gol
    próprio ou mais para dentro da parede/canto).

    Física considerada: para um robô diferencial girando no próprio eixo com
    velocidade das rodas (v_l, v_r) = (-s, s) (s>0), a rotação é
    anti-horária (mesma convenção usada em DefendGoalNode). Nesse caso, o
    ponto de contato com a bola (a uma direção r_hat do centro do robô) é
    empurrado tangencialmente na direção "r_hat rotacionado +90°". Girando
    no sentido oposto (v_l, v_r) = (s, -s), o empurrão é "r_hat rotacionado
    -90°". Escolhemos o sentido cujo empurrão resultante tem maior produto
    escalar com a direção seg ura desejada.

    away_direction_fn: função (robot, ball, team, enemy_team) -> vetor 2D
        (não precisa ser normalizado) apontando para a direção segura. Se
        None, mantém o comportamento antigo (giro anti-horário fixo).
    """
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

                # Direção do empurrão tangencial da bola para cada sentido de giro
                ccw_push_dir = np.array([-r_hat[1], r_hat[0]])  # r_hat girado +90°
                cw_push_dir = np.array([r_hat[1], -r_hat[0]])   # r_hat girado -90°

                ccw_score = np.dot(ccw_push_dir, away_hat)
                cw_score = np.dot(cw_push_dir, away_hat)

                clockwise = cw_score > ccw_score

        if clockwise:
            robot.set_wheel_speeds(speed, -speed, priority=True)
        else:
            robot.set_wheel_speeds(-speed, speed, priority=True)

        return Status.RUNNING

class SmartPushToGoalNode(Node):
    def __init__(self, enemy_goal_pos, ally_goal_x=MID_GOALAREA_A[0], aggressiveness_multiplier=1.0,
                 field_bounds=None, field_margin=10.0, side_alignment_threshold=0.15):
        self.enemy_goal_pos = np.array(enemy_goal_pos)
        self.ally_goal_x = ally_goal_x
        self.agg_mult = aggressiveness_multiplier
        self.planner = ERRTPlanner()
        self.path = []
        self.replan_cooldown = 0
        self.push_engagement_dist = 18.0

        # CORREÇÃO 2: limites reais do campo para clampar pontos-alvo.
        # Se não for informado explicitamente, assume-se que fieldC é o
        # centro geometrico do campo (campo simetrico de (0,0) a (2*fieldC)).
        if field_bounds is None:
            field_bounds = (0.0, fieldC[0] * 2.0, 0.0, fieldC[1] * 2.0)
        self.x_min, self.x_max, self.y_min, self.y_max = field_bounds
        self.field_margin = field_margin

        # CORREÇÃO 5: o quão alinhado (produto escalar) o vetor robo->bola
        # precisa estar com a direção bola->gol para considerarmos que o
        # robô está "atrás" da bola e pode empurrar direto.
        self.side_alignment_threshold = side_alignment_threshold

    def _clamp_to_field(self, point):
        clamped_x = np.clip(point[0], self.x_min + self.field_margin, self.x_max - self.field_margin)
        clamped_y = np.clip(point[1], self.y_min + self.field_margin, self.y_max - self.field_margin)
        return np.array([clamped_x, clamped_y])

    def tick(self, robot, ball, team, enemy_team, dt):
        robot_pos = robot.position
        ball_pos = ball.position
        dist_to_ball = robot.distance_to(ball.x, ball.y)
        
        vec_ball_to_goal = self.enemy_goal_pos - ball_pos
        dist_goal = np.linalg.norm(vec_ball_to_goal)
        dir_goal = vec_ball_to_goal / dist_goal if dist_goal > 0.1 else np.array([1.0, 0.0])
        target_angle_to_goal = math.atan2(dir_goal[1], dir_goal[0])

        # CORREÇÃO 5: só empurra direto se o robô já estiver "atrás" da bola
        # em relação ao gol (senão empurraria a bola para o lado errado).
        vec_robot_to_ball = ball_pos - robot_pos
        dist_robot_to_ball = np.linalg.norm(vec_robot_to_ball)
        if dist_robot_to_ball > 0.1:
            dir_robot_to_ball = vec_robot_to_ball / dist_robot_to_ball
            alignment = np.dot(dir_robot_to_ball, dir_goal)
        else:
            alignment = 1.0
        robot_is_behind_ball = alignment >= self.side_alignment_threshold

        # Condução direta da bola ao gol
        if dist_to_ball <= self.push_engagement_dist and robot_is_behind_ball:
            target_pos = self._clamp_to_field(ball_pos + (dir_goal * 15.0))
            v_l, v_r = robot.go_to_point(target_pos, target_angle=target_angle_to_goal, dt=dt)
            robot.set_wheel_speeds(v_l * self.agg_mult, v_r * self.agg_mult)
            self.path = []
            return Status.RUNNING

        # Posicionamento atrás da bola via ERRT
        all_robots = team + enemy_team
        obstacles = [obs.position for obs in all_robots if obs.id_robot != robot.id_robot]
        approach_pos = self._clamp_to_field(ball_pos - (dir_goal * 12.0))
        
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
            
            v_l, v_r = robot.go_to_point(next_waypoint, target_angle=target_angle_to_goal, dt=dt)
            robot.set_wheel_speeds(v_l * self.agg_mult, v_r * self.agg_mult)
        else:
            v_l, v_r = robot.go_to_point(approach_pos, target_angle=target_angle_to_goal, dt=dt)
            robot.set_wheel_speeds(v_l * self.agg_mult, v_r * self.agg_mult)

        return Status.RUNNING