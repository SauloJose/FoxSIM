# src/intelligence/bt_conditions.py
import numpy as np
from .bt_core import *
from ui.interface_config import * # Importa o centro do campo calculado

class IsBallNearWall(Node):
    def __init__(self, margin=3.5, field_bounds=None):
        """
        Verifica se a bola está dentro da margem de segurança das paredes do campo.
        field_bounds: (x_min, x_max, y_min, y_max)
        """
        self.margin = margin
        if field_bounds is None:
            field_bounds = (0.0, fieldC[0] * 2.0, 0.0, fieldC[1] * 2.0)
        self.x_min, self.x_max, self.y_min, self.y_max = field_bounds

    def tick(self, robot, ball, team, enemy_team, dt):
        near_x = (ball.x <= self.x_min + self.margin) or (ball.x >= self.x_max - self.margin)
        near_y = (ball.y <= self.y_min + self.margin) or (ball.y >= self.y_max - self.margin)
        
        if near_x or near_y:
            return Status.SUCCESS
        return Status.FAILURE
    
class IsClosestToBall(Node):
    _last_primary = {}

    def __init__(self, hysteresis=5.0):
        self.hysteresis = hysteresis

    def tick(self, robot, ball, team, enemy_team, dt):
        # 1. Goleiro nunca é atacante de linha
        if getattr(robot, 'role', None) == GOALKEEPER:
            return Status.FAILURE

        # 2. Considera apenas os jogadores de linha (ATACKER1 e ATACKER2)
        field_robots = [
            r for r in team 
            if getattr(r, 'role', None) in [ATACKER1, ATACKER2] or getattr(r, 'role', None) != GOALKEEPER
        ]

        if not field_robots:
            return Status.SUCCESS

        # 3. Distância de cada candidato até a bola
        distances = {r.id_robot: r.distance_to(ball.x, ball.y) for r in field_robots}

        # 4. Melhor candidato "puro" pela menor TUPLA (distancia, id_robot)
        # Isso garante DESEMPATE PERFEITO e impossibilita 2 atacantes ou 2 suportes
        best_candidate = min(field_robots, key=lambda r: (distances[r.id_robot], r.id_robot))
        best_id = best_candidate.id_robot

        # 5. Aplica histerese em relação a quem era o principal no tick anterior
        team_key = tuple(sorted(distances.keys()))
        last_id = IsClosestToBall._last_primary.get(team_key)

        if last_id is not None and last_id in distances and last_id != best_id:
            # Só troca de principal se o novo candidato estiver
            # significativamente mais perto que o atual titular.
            if distances[best_id] + self.hysteresis >= distances[last_id]:
                primary_id = last_id
            else:
                primary_id = best_id
        else:
            primary_id = best_id

        IsClosestToBall._last_primary[team_key] = primary_id

        if robot.id_robot == primary_id:
            return Status.SUCCESS
        
        return Status.FAILURE
    
class IsBallInGKZone(Node):
    """
    Verifica se a bola está dentro de uma distância máxima segura do gol aliado.
    Isso impede que o goleiro seja "arrastado" para fora da grande área.
    """
    def __init__(self, ally_goal_x, max_dist_x=40.0):
        self.ally_goal_x = ally_goal_x
        self.max_dist_x = max_dist_x

    def tick(self, robot, ball, team, enemy_team, dt):
        # Calcula a distância no eixo X entre a bola e a linha do gol
        dist_x = abs(ball.x - self.ally_goal_x)
        
        if dist_x <= self.max_dist_x:
            return Status.SUCCESS
            
        return Status.FAILURE
    
class IsNearWall(Node):
    """
    Retorna SUCCESS se o robô estiver muito perto das bordas do campo.
    """
    def __init__(self, margin=15.0, field_width=150.0, field_height=130.0):
        self.margin = margin
        self.field_width = field_width
        self.field_height = field_height

    def tick(self, robot, ball, team, enemy_team, dt):
        # Verifica se o X ou Y do robô estão nas zonas de margem (bordas)
        if (robot.x < self.margin or robot.x > self.field_width - self.margin or
            robot.y < self.margin or robot.y > self.field_height - self.margin):
            return Status.SUCCESS
        return Status.FAILURE

class IsBallInDefenseZone(Node):
    """
    Verifica se a bola está no nosso campo de defesa usando fieldC[0] (centro X).
    """
    def __init__(self, field_center_x=fieldC[0]):
        self.field_center_x = field_center_x

    def tick(self, robot, ball, team, enemy_team, dt):
        if ball.x < self.field_center_x:
            return Status.SUCCESS
        return Status.FAILURE

class IsBallWithinDistance(Node):
    """
    Verifica se a bola está a uma distância perigosa (muito próxima do robô).
    """
    def __init__(self, max_distance=35.0):
        self.max_distance = max_distance

    def tick(self, robot, ball, team, enemy_team, dt):
        dist = robot.distance_to(ball.x, ball.y)
        if dist <= self.max_distance:
            return Status.SUCCESS
        return Status.FAILURE


class IsTangledWithRobot(Node):
    """
    Retorna SUCCESS se o robô colidiu/encostou em outro robô (aliado ou inimigo).
    Porém, ignora a colisão se a bola estiver muito perto (para não fugir de divididas).
    """
    def __init__(self, min_dist=11.0, ball_ignore_dist=18.0):
        self.min_dist = min_dist
        self.ball_ignore_dist = ball_ignore_dist

    def tick(self, robot, ball, team, enemy_team, dt):
        # Se a bola estiver colada, é uma disputa de bola! Não podemos dar ré.
        if robot.distance_to(ball.x, ball.y) < self.ball_ignore_dist:
            return Status.FAILURE
            
        all_robots = team + enemy_team
        for obs in all_robots:
            # Ignora a si mesmo
            if obs.id_robot == robot.id_robot and obs.team == robot.team:
                continue
                
            # Se encostou em alguém
            if robot.distance_to(obs.x, obs.y) < self.min_dist:
                return Status.SUCCESS
                
        return Status.FAILURE