import numpy as np
from simulator.intelligence.bt_core import Node, Status
from simulator.intelligence.bt_config import (
    FIELD_LIMITS,
    ROBOT_RADIUS,
    BALL_RADIUS,
    AVOID_RADIUS,
    MAX_WHEEL_SPEED,
    GOALIE_MAX_SPEED,
    SUPPORT_SPEED_FACTOR,
    EMERGENCY_REVERSE_SPEED,
    EMERGENCY_STOP_DISTANCE,
    EMERGENCY_FRONTAL_COS,
    MIN_SUPPORT_TO_BALL_DIST_STANDARD,
)


def limit_wheel_speeds(vl, vr, max_speed):
    """Limita a velocidade máxima das rodas mantendo a proporção de curva."""
    max_current = max(abs(vl), abs(vr))
    if max_current > max_speed:
        ratio = max_speed / max_current
        vl *= ratio
        vr *= ratio
    return vl, vr


def _get_obstacles(robot, team, enemy_team, ignore_enemies=False):
    """
    Lista de robôs considerados obstáculos para o robô atual.

    Extraído para função própria porque a mesma filtragem (companheiros
    exceto eu mesmo, + adversários) era repetida em check_emergency_collision
    e apply_tangential_avoidance — agora há um único lugar para manter essa
    regra (por exemplo, se um dia obstáculos passarem a incluir postes ou
    outros objetos do campo).
    """
    obstacles = [r for r in team.robots if r.id_robot != robot.id_robot]
    if not ignore_enemies:
        obstacles = obstacles + list(enemy_team.robots)
    return obstacles


def check_emergency_collision(robot, team, enemy_team, ignore_enemies=False):
    """
    Verifica colisão iminente com o obstáculo à frente mais próximo e, se
    necessário, calcula uma ré que afasta o robô DAQUELE obstáculo — não
    apenas uma ré reta "às cegas".

    Duas correções em relação à versão original:

    1) Cone frontal mais realista: antes, `dot(direction, vec_to_obs) > 0`
       cobria 180° (todo o hemisfério frontal), fazendo o robô frear/recuar
       para obstáculos que mal estavam no seu caminho. Agora o cone é de
       ~140° (EMERGENCY_FRONTAL_COS), mais fiel a uma colisão realmente
       iminente.

    2) Ré direcionada: antes a resposta era sempre (-18, -18), reto para
       trás, independente de onde estava o obstáculo. Isso fazia o robô
       recuar, sair da distância de segurança, e no próximo tick avançar de
       novo reto para o mesmo alvo — reencostando no mesmo obstáculo em
       ciclo ("bate-recua-bate"). Agora a ré tem uma leve componente de giro
       que afasta o robô do LADO onde está o obstáculo.

    ignore_enemies:
        Quando True, apenas colisões com ALIADOS disparam a ré de
        emergência. Usado em manobras de chute (SpinShootNode,
        WallClearanceSpinNode), onde encostar num ADVERSÁRIO disputando a
        bola é uma situação normal de jogo e não deve abortar a jogada —
        mas encostar em um companheiro de time continua sendo sempre
        indesejado.
    """
    obstacles = _get_obstacles(robot, team, enemy_team, ignore_enemies)

    nearest_dist = float('inf')
    nearest_dir = None

    for obs in obstacles:
        vec_to_obs = obs.position - robot.position
        dist = np.linalg.norm(vec_to_obs)
        if dist < EMERGENCY_STOP_DISTANCE and dist < nearest_dist:
            direction = vec_to_obs / dist if dist > 1e-6 else robot.direction
            if np.dot(robot.direction, direction) > EMERGENCY_FRONTAL_COS:
                nearest_dist = dist
                nearest_dir = direction

    if nearest_dir is None:
        return False, 0.0, 0.0

    # Ré com leve curva para o lado OPOSTO ao obstáculo, evitando reencostar
    # nele assim que a distância de segurança for reestabelecida.
    side = np.cross(robot.direction, nearest_dir)
    w = -6.0 if side > 0 else 6.0

    v = -EMERGENCY_REVERSE_SPEED
    L = robot.distance_wheels
    vl = v - (w * L / 2.0)
    vr = v + (w * L / 2.0)
    vl, vr = limit_wheel_speeds(vl, vr, EMERGENCY_REVERSE_SPEED)
    return True, vl, vr


def apply_tangential_avoidance(robot, target_pos, team, enemy_team, avoid_radius=AVOID_RADIUS):
    """
    Campo potencial tangencial que utiliza a VELOCIDADE dos outros robôs
    para prever colisões e desviar suavemente sem andar de ré.
    """
    vec_to_target = target_pos - robot.position
    dist_to_target = np.linalg.norm(vec_to_target)

    if dist_to_target < (ROBOT_RADIUS + BALL_RADIUS + 1.0):
        return target_pos

    dir_to_target = vec_to_target / dist_to_target if dist_to_target > 0 else np.array([1.0, 0.0])
    tangential_offset = np.array([0.0, 0.0], dtype=float)
    obstacles = _get_obstacles(robot, team, enemy_team)

    for obs in obstacles:
        # Predição de posição futura do obstáculo baseada na velocidade dele (0.2s à frente)
        obs_velocity = getattr(obs, 'velocity', np.zeros(2))
        predicted_obs_pos = obs.position + obs_velocity * 0.2

        vec_to_obs = predicted_obs_pos - robot.position
        dist_obs = np.linalg.norm(vec_to_obs)

        if 0.5 < dist_obs < avoid_radius:
            dir_to_obs = vec_to_obs / dist_obs
            if np.dot(dir_to_obs, dir_to_target) > -0.3:
                tangent_1 = np.array([-dir_to_obs[1], dir_to_obs[0]])
                tangent_2 = np.array([dir_to_obs[1], -dir_to_obs[0]])

                chosen_tangent = tangent_1 if np.dot(tangent_1, dir_to_target) >= np.dot(tangent_2, dir_to_target) else tangent_2
                weight = ((avoid_radius - dist_obs) / avoid_radius) ** 2
                tangential_offset += chosen_tangent * weight * 16.0

    return target_pos + tangential_offset


def compute_forward_steering(robot, target_pos, target_angle=None, max_speed=MAX_WHEEL_SPEED, kp_angular=6.0, kp_linear=2.5):
    """
    Algoritmo de controle diferencial 100% focado em movimento FRONTAL.
    Gira no próprio eixo se estiver desalinhado antes de acelerar.
    """
    vec = target_pos - robot.position
    dist = np.linalg.norm(vec)

    # Zona morta de chegada
    if dist < 0.8:
        if target_angle is not None:
            angle_err = robot.normalize_angle(target_angle - robot.angle)
            w = angle_err * kp_angular
            vl = -w * robot.distance_wheels / 2.0
            vr = w * robot.distance_wheels / 2.0
            return limit_wheel_speeds(vl, vr, max_speed)
        return 0.0, 0.0

    angle_to_target = np.arctan2(vec[1], vec[0])
    heading_error = robot.normalize_angle(angle_to_target - robot.angle)

    # 1. Se estiver muito desalinhado (> 45°), prioriza girar no próprio eixo de FRENTE
    if abs(heading_error) > (np.pi / 4.0):
        v = 0.0  # Não anda pra frente nem de ré enquanto não alinhar a frente
        w = np.sign(heading_error) * min(max_speed / (robot.distance_wheels / 2.0), abs(heading_error) * kp_angular)
    else:
        # 2. Alinhado de frente: avança proporcionalmente à distância e alinhamento
        v = min(max_speed, dist * kp_linear) * max(0.0, np.cos(heading_error))

        if target_angle is not None and dist < 8.0:
            final_angle_err = robot.normalize_angle(target_angle - robot.angle)
            w = final_angle_err * kp_angular
        else:
            w = heading_error * kp_angular

    L = robot.distance_wheels
    vl = v - (w * L / 2.0)
    vr = v + (w * L / 2.0)
    return limit_wheel_speeds(vl, vr, max_speed)


class DefendGoalNode(Node):
    """
    Goleiro inteligente:
    1. Fica olhando continuamente para a bola.
    2. Corre lateralmente na linha do gol mantendo o alinhamento frontal com a bola.
    3. Quando a bola entra na área de corte (< 22cm), sai da linha e ataca a bola de frente.
    """
    def __init__(self, own_goal, forward_angle, max_speed=GOALIE_MAX_SPEED, intercept_dist=22.0):
        self.own_goal = own_goal
        self.forward_angle = forward_angle
        self.max_speed = max_speed
        self.intercept_dist = intercept_dist

    def tick(self, robot, ball, team, enemy_team, dt):
        # Ré de emergência se travado com outro robô
        is_stuck, vl_stuck, vr_stuck = check_emergency_collision(robot, team, enemy_team)
        if is_stuck:
            robot.set_wheel_speeds(vl_stuck, vr_stuck)
            return Status.RUNNING

        dist_ball = np.linalg.norm(ball.position - robot.position)
        vec_to_ball = ball.position - robot.position
        angle_to_ball = np.arctan2(vec_to_ball[1], vec_to_ball[0])

        # 1. Defesa Rápida / Chute de Rebatida se colado na bola
        if dist_ball < 8.5:
            spin_dir = 1.0 if ball.y > robot.y else -1.0
            robot.set_wheel_speeds(self.max_speed * spin_dir, -self.max_speed * spin_dir)
            return Status.RUNNING

        # 2. ATAQUE / CORTE DE ENTRADA: Sai do gol para cortar a bola se ela estiver próxima
        if dist_ball < self.intercept_dist and abs(ball.x - self.own_goal[0]) < 45.0:
            target_pos = ball.position
            vl, vr = compute_forward_steering(robot, target_pos, angle_to_ball, max_speed=self.max_speed)
        else:
            # 3. POSICIONAMENTO NA LINHA DO GOL: Corre na linha X acompanhando o Y da bola
            vx = getattr(ball, 'vx', 0.0)
            vy = getattr(ball, 'vy', 0.0)
            target_y = ball.y

            # Predição rápida de trajetória
            dir_x_to_goal = self.own_goal[0] - ball.x
            if abs(vx) > 0.05 and (vx * dir_x_to_goal > 0):
                time_to_goal = abs(dir_x_to_goal / vx)
                target_y = ball.y + vy * time_to_goal

            target_y = np.clip(target_y, self.own_goal[1] - 15.0, self.own_goal[1] + 15.0)
            target_pos = np.array([self.own_goal[0], target_y], dtype=float)

            # Navega até o ponto na linha do gol mantendo sempre a FRENTE virada para a bola
            vl, vr = compute_forward_steering(robot, target_pos, angle_to_ball, max_speed=self.max_speed)

        robot.set_wheel_speeds(vl, vr)
        return Status.RUNNING


class AttackBallNode(Node):
    """Ataque 100% frontal com alinhamento rigoroso atrás da bola em direção ao gol adversário."""
    def __init__(self, enemy_goal, max_speed=MAX_WHEEL_SPEED):
        self.enemy_goal = enemy_goal
        self.max_speed = max_speed

    def tick(self, robot, ball, team, enemy_team, dt):
        is_stuck, vl_stuck, vr_stuck = check_emergency_collision(robot, team, enemy_team)
        if is_stuck:
            robot.set_wheel_speeds(vl_stuck, vr_stuck)
            return Status.RUNNING

        ball_pos = ball.position
        vec_ball_to_goal = self.enemy_goal - ball_pos
        dist_b2g = np.linalg.norm(vec_ball_to_goal)
        dir_b2g = vec_ball_to_goal / dist_b2g if dist_b2g > 0 else np.array([1.0, 0.0])

        OFFSET_BEHIND = 11.0  # Posiciona 11cm atrás da bola na linha do gol
        p_behind = ball_pos - dir_b2g * OFFSET_BEHIND

        vec_robot_to_ball = ball_pos - robot.position
        is_behind_ball = np.dot(vec_robot_to_ball, dir_b2g) > 0

        if not is_behind_ball:
            # Faz a volta pelo lado usando campo potencial tangencial
            target_pos = apply_tangential_avoidance(robot, p_behind, team, enemy_team)
            target_angle = np.arctan2(dir_b2g[1], dir_b2g[0])
        else:
            # Posicionado atrás: carrega/ataca a bola de frente mirando no gol
            target_pos = apply_tangential_avoidance(robot, ball_pos, team, enemy_team)
            target_angle = np.arctan2(dir_b2g[1], dir_b2g[0])

        vl, vr = compute_forward_steering(robot, target_pos, target_angle, max_speed=self.max_speed)
        robot.set_wheel_speeds(vl, vr)
        return Status.RUNNING


class SpinShootNode(Node):
    """
    Giro tático no contato com a bola (chute por rotação).

    CORREÇÕES:
    1) Timer por robô: `self.elapsed` (escalar) virou um dicionário indexado
       por `robot.id_robot`. Se a mesma instância deste nó for compartilhada
       entre robôs (árvore construída uma vez por time), a versão original
       vazava o cronômetro de um robô para outro, produzindo giros de
       duração incorreta. Com o dicionário, cada robô tem seu próprio
       contador, independentemente de como a árvore é instanciada.
    2) Checagem de colisão adicionada (o único nó de ação que não tinha
       nenhuma): usa `ignore_enemies=True`, pois durante uma tentativa de
       chute perto do gol é normal e esperado haver contato com um
       adversário disputando a jogada — o que não pode acontecer é o robô
       ficar empurrando um companheiro de time enquanto gira.
    """
    def __init__(self, enemy_goal, duration=0.20):
        self.enemy_goal = enemy_goal
        self.duration = duration
        self._elapsed_by_robot = {}

    def tick(self, robot, ball, team, enemy_team, dt):
        is_stuck, vl_stuck, vr_stuck = check_emergency_collision(robot, team, enemy_team, ignore_enemies=True)
        if is_stuck:
            robot.set_wheel_speeds(vl_stuck, vr_stuck)
            return Status.RUNNING

        rid = robot.id_robot
        elapsed = self._elapsed_by_robot.get(rid, 0.0) + dt
        self._elapsed_by_robot[rid] = elapsed

        spin_dir = 1.0 if robot.y < self.enemy_goal[1] else -1.0

        vl = MAX_WHEEL_SPEED * spin_dir
        vr = -MAX_WHEEL_SPEED * spin_dir
        robot.set_wheel_speeds(vl, vr)

        if elapsed >= self.duration:
            self._elapsed_by_robot[rid] = 0.0
            return Status.SUCCESS

        return Status.RUNNING


class SupportAttackerNode(Node):
    """
    Suporte tático: posiciona-se de frente acompanhando o ataque e olhando
    para a bola, mantendo uma distância mínima da bola.

    CORREÇÃO: a versão original não tinha nenhum piso de distância — quando
    a bola estava perto do próprio gol, `ball.position*0.45 + own_goal*0.55`
    convergia para muito perto do atacante principal (também disputando a
    bola), fazendo os dois robôs do mesmo time brigarem fisicamente pelo
    mesmo espaço. Agora o alvo é "empurrado" para fora de um raio mínimo
    (`min_ball_distance`) em torno da bola antes do desvio tangencial.
    """
    def __init__(self, own_goal, max_speed=MAX_WHEEL_SPEED * SUPPORT_SPEED_FACTOR,
                 min_ball_distance=MIN_SUPPORT_TO_BALL_DIST_STANDARD):
        self.own_goal = own_goal
        self.max_speed = max_speed
        self.min_ball_distance = min_ball_distance

    def tick(self, robot, ball, team, enemy_team, dt):
        is_stuck, vl_stuck, vr_stuck = check_emergency_collision(robot, team, enemy_team)
        if is_stuck:
            robot.set_wheel_speeds(vl_stuck, vr_stuck)
            return Status.RUNNING

        base_target = ball.position * 0.45 + self.own_goal * 0.55

        vec_from_ball = base_target - ball.position
        dist_from_ball = np.linalg.norm(vec_from_ball)
        if dist_from_ball < self.min_ball_distance:
            if dist_from_ball > 1e-6:
                push_dir = vec_from_ball / dist_from_ball
            else:
                fallback = self.own_goal - ball.position
                fallback_norm = np.linalg.norm(fallback)
                push_dir = fallback / fallback_norm if fallback_norm > 1e-6 else np.array([1.0, 0.0])
            base_target = ball.position + push_dir * self.min_ball_distance

        final_target = apply_tangential_avoidance(robot, base_target, team, enemy_team)

        vec_to_ball = ball.position - robot.position
        target_angle = np.arctan2(vec_to_ball[1], vec_to_ball[0])

        vl, vr = compute_forward_steering(robot, final_target, target_angle, max_speed=self.max_speed)
        robot.set_wheel_speeds(vl, vr)
        return Status.RUNNING


class ClearBallNode(Node):
    """
    Bico de emergência: ataca a bola de frente para isolar da área defensiva.

    CORREÇÃO: passou a usar `apply_tangential_avoidance` no alvo, assim como
    AttackBallNode/SupportAttackerNode/DefensiveWallNode. Antes, este nó
    navegava em linha reta até a bola e só reagia a um companheiro no
    caminho quando já estava quase encostando nele (colisão reativa de
    emergência), o que produzia o padrão "avança reto -> encosta -> ré reta
    -> avança reto de novo pro mesmo alvo -> encosta de novo".
    """
    def __init__(self, max_speed=MAX_WHEEL_SPEED):
        self.max_speed = max_speed

    def tick(self, robot, ball, team, enemy_team, dt):
        is_stuck, vl_stuck, vr_stuck = check_emergency_collision(robot, team, enemy_team)
        if is_stuck:
            robot.set_wheel_speeds(vl_stuck, vr_stuck)
            return Status.RUNNING

        target_pos = apply_tangential_avoidance(robot, ball.position, team, enemy_team)

        vec_to_ball = ball.position - robot.position
        target_angle = np.arctan2(vec_to_ball[1], vec_to_ball[0])

        vl, vr = compute_forward_steering(robot, target_pos, target_angle, max_speed=self.max_speed)
        robot.set_wheel_speeds(vl, vr)
        return Status.RUNNING


class UnstuckCornerNode(Node):
    """
    Retira a bola presa no canto do campo.

    CORREÇÃO (sinal invertido): a versão original calculava
        offset_dir = np.sign(ball.position) * -1.0
        target = ball.position + offset_dir * 8.0
    o que posicionava o alvo do lado do CENTRO do campo em relação à bola —
    ou seja, mais perto do meio-campo do que a própria bola. Como o robô
    navega até esse alvo (não até a bola), ele parava curto, sem nunca ficar
    "atrás" da bola (do lado do canto) para empurrá-la para fora. Na prática
    a bola ficava presa, ou era empurrada ainda mais para o canto durante a
    aproximação.

    Agora o alvo fica do lado do CANTO em relação à bola (posição para o
    robô "abraçar" a bola por trás, do ponto de vista do canto, e empurrá-la
    para o centro ao avançar), sempre limitado (clip) para nunca ultrapassar
    fisicamente os limites do campo.
    """
    def __init__(self, field_limits=FIELD_LIMITS, max_speed=MAX_WHEEL_SPEED, approach_offset=9.0):
        self.limit_x, self.limit_y = field_limits
        self.max_speed = max_speed
        self.approach_offset = approach_offset

    def tick(self, robot, ball, team, enemy_team, dt):
        is_stuck, vl_stuck, vr_stuck = check_emergency_collision(robot, team, enemy_team)
        if is_stuck:
            robot.set_wheel_speeds(vl_stuck, vr_stuck)
            return Status.RUNNING

        half_x = self.limit_x / 2.0
        half_y = self.limit_y / 2.0

        corner_dir = np.sign(ball.position)
        corner_dir = np.where(corner_dir == 0, 1.0, corner_dir)

        raw_target = ball.position + corner_dir * self.approach_offset
        target = np.array([
            np.clip(raw_target[0], -half_x + ROBOT_RADIUS, half_x - ROBOT_RADIUS),
            np.clip(raw_target[1], -half_y + ROBOT_RADIUS, half_y - ROBOT_RADIUS),
        ])

        vec_to_ball = ball.position - robot.position
        target_angle = np.arctan2(vec_to_ball[1], vec_to_ball[0])

        vl, vr = compute_forward_steering(robot, target, target_angle, max_speed=self.max_speed)
        robot.set_wheel_speeds(vl, vr)
        return Status.RUNNING


class DefensiveWallNode(Node):
    """Barreira defensiva: posiciona-se entre a bola e o gol olhando de frente para a bola."""
    def __init__(self, own_goal, offset_distance=20.0):
        self.own_goal = own_goal
        self.offset_distance = offset_distance

    def tick(self, robot, ball, team, enemy_team, dt):
        is_stuck, vl_stuck, vr_stuck = check_emergency_collision(robot, team, enemy_team)
        if is_stuck:
            robot.set_wheel_speeds(vl_stuck, vr_stuck)
            return Status.RUNNING

        vec_ball_to_goal = self.own_goal - ball.position
        norm = np.linalg.norm(vec_ball_to_goal)
        dir_vector = vec_ball_to_goal / norm if norm > 0 else np.array([1.0, 0.0])

        target_pos = ball.position + dir_vector * self.offset_distance
        target_pos = apply_tangential_avoidance(robot, target_pos, team, enemy_team)
        target_angle = np.arctan2(-dir_vector[1], -dir_vector[0])

        vl, vr = compute_forward_steering(robot, target_pos, target_angle, max_speed=MAX_WHEEL_SPEED * SUPPORT_SPEED_FACTOR)
        robot.set_wheel_speeds(vl, vr)
        return Status.RUNNING


class WallClearanceSpinNode(Node):
    """
    Executa um giro tático direcionado para expulsar a bola da parede
    e lançá-la em direção ao centro do campo ou gol adversário.

    Mesma correção de timer por robô aplicada em SpinShootNode, pelo mesmo
    motivo (evita vazamento de cronômetro entre robôs caso o nó seja
    compartilhado). Também usa `ignore_enemies=True` na checagem de
    colisão, já que empurrar a bola presa na parede frequentemente envolve
    contato com um adversário disputando a mesma bola.
    """
    def __init__(self, enemy_goal, field_limits=FIELD_LIMITS, duration=0.25, max_speed=MAX_WHEEL_SPEED):
        self.enemy_goal = enemy_goal
        self.limit_x, self.limit_y = field_limits
        self.duration = duration
        self.max_speed = max_speed
        self._elapsed_by_robot = {}

    def tick(self, robot, ball, team, enemy_team, dt):
        is_stuck, vl_stuck, vr_stuck = check_emergency_collision(robot, team, enemy_team, ignore_enemies=True)
        if is_stuck:
            robot.set_wheel_speeds(vl_stuck, vr_stuck)
            return Status.RUNNING

        rid = robot.id_robot
        elapsed = self._elapsed_by_robot.get(rid, 0.0) + dt
        self._elapsed_by_robot[rid] = elapsed

        half_x = self.limit_x / 2.0
        half_y = self.limit_y / 2.0

        # Determina a direção do giro conforme a parede mais próxima
        if abs(robot.y) > (half_y - 15.0):
            # Parede superior (+Y): gira no sentido horário (-1.0) para empurrar a bola para baixo
            # Parede inferior (-Y): gira no sentido anti-horário (1.0) para empurrar a bola para cima
            spin_dir = -1.0 if robot.y > 0 else 1.0
        elif abs(robot.x) > (half_x - 15.0):
            # Parede de fundo: gira varrendo para o centro do campo no eixo Y
            spin_dir = 1.0 if robot.y < 0 else -1.0
        else:
            # Padrão: gira voltado para o setor do gol adversário
            spin_dir = 1.0 if robot.y < self.enemy_goal[1] else -1.0

        vl = self.max_speed * spin_dir
        vr = -self.max_speed * spin_dir

        robot.set_wheel_speeds(vl, vr)

        if elapsed >= self.duration:
            self._elapsed_by_robot[rid] = 0.0
            return Status.SUCCESS

        return Status.RUNNING