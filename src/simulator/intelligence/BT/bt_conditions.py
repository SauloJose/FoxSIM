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