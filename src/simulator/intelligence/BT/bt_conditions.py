# src/intelligence/bt_conditions.py
import numpy as np
from .bt_core import Node, Status
from ui.interface_config import fieldC # Importa o centro do campo calculado

class IsClosestToBall(Node):
    """
    Verifica se este robô é o mais próximo da bola entre todos os aliados.
    """
    def tick(self, robot, ball, team, enemy_team, dt):
        my_dist = robot.distance_to(ball.x, ball.y)
        
        for ally in team:
            if ally.id_robot != robot.id_robot:
                ally_dist = ally.distance_to(ball.x, ball.y)
                if ally_dist < my_dist:
                    return Status.FAILURE
                    
        return Status.SUCCESS

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