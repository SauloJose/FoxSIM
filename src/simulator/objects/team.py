import numpy as np  # Substitui math por numpy
from simulator.objects.robot import Robot
from ui.interface_config import *
import pygame 

class Team:
    '''
        Classe criada para organizar os robôs dentro de um time só.
    '''
    def __init__(self, positions, team_name, initial_angle=0):
        self.team_name = team_name
        self.initial_angle = initial_angle
        self.positions = positions 

        print(f"[DEBUG]: Criando robôs do time {self.team_name}")

        # Escala para o tamanho do robô
        scale = (ROBOT_SIZE_CM / SCALE_PX_TO_CM, ROBOT_SIZE_CM / SCALE_PX_TO_CM)

        # Imagens dos aliados com máxima qualidade
        self.ATA1_image = pygame.transform.smoothscale(pygame.image.load("src/assets/ATA1.png").convert_alpha(), scale)
        self.ATA2_image = pygame.transform.smoothscale(pygame.image.load("src/assets/ATA2.png").convert_alpha(), scale)
        self.ATGK_image = pygame.transform.smoothscale(pygame.image.load("src/assets/ATGK.png").convert_alpha(), scale)
        self.ally_images = [self.ATGK_image, self.ATA1_image, self.ATA2_image]

        # Imagens dos inimigos com máxima qualidade
        self.ETA1_image = pygame.transform.smoothscale(pygame.image.load("src/assets/ETA1.png").convert_alpha(), scale)
        self.ETA2_image = pygame.transform.smoothscale(pygame.image.load("src/assets/ETA2.png").convert_alpha(), scale)
        self.ETGK_image = pygame.transform.smoothscale(pygame.image.load("src/assets/ETGK.png").convert_alpha(), scale)
        self.enemies_images = [self.ETGK_image, self.ETA1_image, self.ETA2_image]


        imagesRobot = self.ally_images if team_name == BLUE_TEAM else self.enemies_images

        # Criação dos robôs
        ids = [0, 1, 2]  # GOALKEEPER, ATACKER1, ATACKER2
        self.robots = []
        for i in range(3):
            x, y = self.positions[i][1]
            role = self.positions[i][0]
            image = imagesRobot[i]
            robot = Robot(x, y, self.team_name, role, ids[i], image, initial_angle=self.initial_angle)
            self.robots.append(robot)

        # Acesso direto para organização
        self.goalkeeaper, self.atacker1, self.atacker2 = self.robots

    def reset_positions(self, positions):
        print("[DEBUG]: Resetando posição dos robôs")
        for robot, (_, pos) in zip(self.robots, positions):
            robot.reset()
            robot.set_position(pos[0], pos[1])


# Configurações dos times
# Converte as coordenadas relativas para pixels
blue_team_positions = [[role, pos] for role, pos in RELATIVE_POSITIONS[:3]]
red_team_positions = [[role, pos] for role, pos in RELATIVE_POSITIONS[3:]]