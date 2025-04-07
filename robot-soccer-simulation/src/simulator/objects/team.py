import numpy as np  # Substitui math por numpy
from simulator.objects.robot import Robot
from ui.interface_config import *

class Team:
    '''
        Classe criada para organizar os robôs dentro de um time só.
    '''
    def __init__(self, color, positions, team_name, initial_angle=0):
        self.color = color
        print("[DEBUG]: Criando robôs")
        self.robots = [
            Robot(x, y,team=team_name, role=GOALKEEPER if i == 1 else ATACKER, color=color, initial_angle=initial_angle)
            for i, (x, y) in enumerate(positions)
        ]
    
    def reset_positions(self, positions):
        print("[DEBUG]: Resetando posição dos robôs")
        for robot, (x, y) in zip(self.robots, positions):
            robot.reset()


# Configurações dos times
# Converte as coordenadas relativas para pixels
blue_team_positions = [(x, y) for x, y in RELATIVE_POSITIONS[:3]]
red_team_positions = [(x, y) for x, y in RELATIVE_POSITIONS[3:]]
