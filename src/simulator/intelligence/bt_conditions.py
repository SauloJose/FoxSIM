import numpy as np
from simulator.intelligence.bt_core import Node, Status
from simulator.intelligence.bt_config import FIELD_LIMITS, CORNER_SIZE, WALL_MARGIN, DEFENSE_RADIUS
from ui.interface_config import GOALKEEPER


class IsRoleNode(Node):
    """Verifica se o robô possui a função especificada de forma tolerante a tipo."""
    def __init__(self, role):
        self.role = role

    def tick(self, robot, ball, team, enemy_team, dt):
        return Status.SUCCESS if str(robot.role).lower() == str(self.role).lower() else Status.FAILURE


class IsClosestAttackerNode(Node):
    """
    Garante matematicamente que apenas UM robô seja o atacante principal, com
    histerese por margem de distância + desempate por id.

    Nota de arquitetura: este nó é seguro mesmo se a mesma instância for usada
    para tickar vários robôs, porque não guarda nenhum estado em `self` — o
    resultado é recalculado do zero a cada tick, a partir apenas das posições
    atuais. Isso o torna diferente (e mais seguro) dos nós de temporização em
    bt_actions.py, que precisaram ser corrigidos para não compartilhar estado.

    Limitação conhecida: a margem evita alternância rápida quando as
    distâncias oscilam perto do limiar, mas não é uma histerese "com
    memória" (não sabe quem era o atacante no tick anterior). Para times
    com muito ruído de posição, considere evoluir para um mecanismo de
    debounce temporal (só troca de atacante após N ticks consecutivos de
    vantagem), o que exigiria um "quadro" de estado compartilhado por time
    e por tick — não implementado aqui para não reintroduzir o mesmo tipo
    de bug de estado compartilhado corrigido nesta revisão.
    """
    def __init__(self, hysteresis_margin=5.0):
        self.margin = hysteresis_margin

    def tick(self, robot, ball, team, enemy_team, dt):
        attackers = [r for r in team.robots if str(r.role).lower() != str(GOALKEEPER).lower()]

        dist_self = robot.distance_to(ball.x, ball.y)

        for other in attackers:
            if other.id_robot != robot.id_robot:
                dist_other = other.distance_to(ball.x, ball.y)

                # Desempate estrito com margem para evitar alternância rápida de papéis
                if (dist_other + self.margin) < dist_self:
                    return Status.FAILURE
                elif abs(dist_other - dist_self) <= self.margin and other.id_robot < robot.id_robot:
                    return Status.FAILURE

        return Status.SUCCESS


class IsBallInCornerNode(Node):
    """Verifica se a bola está presa nos cantos do campo."""
    def __init__(self, field_limits=FIELD_LIMITS, corner_size=CORNER_SIZE):
        self.limit_x, self.limit_y = field_limits
        self.corner_size = corner_size

    def tick(self, robot, ball, team, enemy_team, dt):
        in_x_corner = abs(ball.x) > (self.limit_x / 2.0 - self.corner_size)
        in_y_corner = abs(ball.y) > (self.limit_y / 2.0 - self.corner_size)

        if in_x_corner and in_y_corner:
            return Status.SUCCESS
        return Status.FAILURE


class IsBallInDefenseZoneNode(Node):
    """Verifica se a bola está na área defensiva próxima ao gol próprio."""
    def __init__(self, own_goal, defense_radius=DEFENSE_RADIUS):
        self.own_goal = own_goal
        self.defense_radius = defense_radius

    def tick(self, robot, ball, team, enemy_team, dt):
        dist_to_goal = np.linalg.norm(ball.position - self.own_goal)
        if dist_to_goal <= self.defense_radius:
            return Status.SUCCESS
        return Status.FAILURE


class CanShootDirectlyNode(Node):
    """
    Autoriza o SpinShoot apenas quando, simultaneamente:
      1) o robô está perto o suficiente da bola;
      2) o robô está de frente para a bola;
      3) a bola está de fato "entre" o robô e o gol adversário (o robô está
         posicionado na linha de tiro), dentro de uma margem angular.

    CORREÇÃO: a versão original só checava (1) e (2) — ou seja, um robô
    virado para a bola em QUALQUER lugar do campo, mesmo de costas para o
    gol adversário, recebia sinal verde para "chutar". Isso permitia giros
    de chute (SpinShootNode) sem nenhuma relação com a direção do gol,
    resultando em chutes que não iam a lugar nenhum ou saíam para fora.
    """
    def __init__(self, enemy_goal, max_dist=7.5, min_goal_alignment=0.5):
        self.enemy_goal = enemy_goal
        self.max_dist = max_dist
        self.min_goal_alignment = min_goal_alignment

    def tick(self, robot, ball, team, enemy_team, dt):
        dist_to_ball = robot.distance_to(ball.x, ball.y)
        if dist_to_ball > self.max_dist:
            return Status.FAILURE

        dir_robot_to_ball = (ball.position - robot.position) / (dist_to_ball if dist_to_ball > 0 else 1.0)

        if np.dot(robot.direction, dir_robot_to_ball) <= 0.5:
            return Status.FAILURE

        vec_ball_to_goal = self.enemy_goal - ball.position
        dist_goal = np.linalg.norm(vec_ball_to_goal)
        if dist_goal < 1e-6:
            return Status.FAILURE
        dir_ball_to_goal = vec_ball_to_goal / dist_goal

        # A direção robô->bola precisa continuar, aproximadamente, na direção bola->gol
        if np.dot(dir_robot_to_ball, dir_ball_to_goal) < self.min_goal_alignment:
            return Status.FAILURE

        return Status.SUCCESS


class IsNearWallNode(Node):
    """
    Verifica se a BOLA está presa contra uma parede lateral, com o robô
    próximo o suficiente para agir sobre ela.

    CORREÇÃO: a versão original disparava também quando apenas o ROBÔ
    (e não a bola) estava perto de qualquer parede, mesmo com a bola livre
    no meio do campo. Isso acionava WallClearanceSpinNode (um giro de
    ~0.25s) sem necessidade real, toda vez que o robô simplesmente
    transitava perto da lateral do campo com a bola grudada nele.
    """
    def __init__(self, field_limits=FIELD_LIMITS, wall_margin=WALL_MARGIN, max_ball_dist=8.5):
        self.limit_x, self.limit_y = field_limits
        self.wall_margin = wall_margin
        self.max_ball_dist = max_ball_dist

    def tick(self, robot, ball, team, enemy_team, dt):
        dist_ball = robot.distance_to(ball.x, ball.y)
        if dist_ball > self.max_ball_dist:
            return Status.FAILURE

        half_x = self.limit_x / 2.0
        half_y = self.limit_y / 2.0

        ball_near_x = abs(ball.x) > (half_x - self.wall_margin)
        ball_near_y = abs(ball.y) > (half_y - self.wall_margin)

        return Status.SUCCESS if (ball_near_x or ball_near_y) else Status.FAILURE