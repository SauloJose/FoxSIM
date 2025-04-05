import numpy as np  # Substitui math por numpy
from simulator.objects.robot import Robot
from ui.interface_config import *

class Team:
    def __init__(self, color, positions, team_name,ball):
        self.color = color
        self.robots = [
            Robot(x, y, speed=50,team=team_name, role="attacker" if i == 0 else "defender", color=color, ball=ball, initial_direction=np.array([1.0,0.0]))
            for i, (x, y) in enumerate(positions)
        ]

    def reset_positions(self, positions):
        for robot, (x, y) in zip(self.robots, positions):
            robot.reset_position(x,y)

    def set_speed(self, speed):
        for robot in self.robots:
            robot.set_speed(speed)

# Configurações dos times
# Converte as coordenadas relativas para pixels
blue_team_positions = [(x * SCALE, y * SCALE) for x, y in RELATIVE_POSITIONS[:3]]
red_team_positions = [(x * SCALE, y * SCALE) for x, y in RELATIVE_POSITIONS[3:]]
