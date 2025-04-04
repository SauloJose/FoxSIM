from simulator.objects.robot import Robot
from ui.interface_config import *

class Team:
    def __init__(self, color, positions, team_name):
        self.color = color
        self.robots = [
            Robot(x, y, speed=50, color=color, team=team_name, role="attacker" if i == 0 else "defender")
            for i, (x, y) in enumerate(positions)
        ]

    def reset_positions(self, positions):
        for robot, (x, y) in zip(self.robots, positions):
            robot.x = x
            robot.y = y

# Configurações dos times
# Converte as coordenadas relativas para pixels
blue_team_positions = [(x * SCALE, y * SCALE) for x, y in RELATIVE_POSITIONS[:3]]
red_team_positions = [(x * SCALE, y * SCALE) for x, y in RELATIVE_POSITIONS[3:]]

blue_team = Team(TEAM_BLUE_COLOR, blue_team_positions, "blue")
red_team = Team(TEAM_RED_COLOR, red_team_positions, "red")