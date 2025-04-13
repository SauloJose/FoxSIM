import numpy as np  # Substitui math por numpy
from simulator.objects.robot import Robot
from ui.interface_config import *
import pygame 

#Classe para encapsular as posições
class Position:
    def __init__(self, GoalKeeperPosition , FirstAtackPosition, SecondAtackPosition):
        self.GoalKeeperP = np.array(GoalKeeperPosition)
        self.Atk1P      = np.array(FirstAtackPosition)
        self.Atk2P      = np.array(SecondAtackPosition)

# Classe para encapsular os times como uma unidade
class Team:
    '''
        Classe criada para organizar os robôs dentro de um time só.
    '''
    def __init__(self, positions:Position, team_name, initial_angle=0):
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

        #Objetos individuais dos robôs que pertencem ao time 
        self.goalkeeaper    = Robot(
                                    x=positions.GoalKeeperP[0],
                                    y=positions.GoalKeeperP[1],
                                    team=self.team_name,
                                    role = GOALKEEPER,
                                    id = 0,
                                    image = imagesRobot[0],
                                    initial_angle= initial_angle 
        )

        self.atacker1       = Robot(
                                    x=positions.Atk1P[0],
                                    y=positions.Atk1P[1],
                                    team=self.team_name,
                                    role = ATACKER1,
                                    id = 1,
                                    image = imagesRobot[1],
                                    initial_angle= initial_angle 
        )

        self.atacker2       = Robot(
                                    x=positions.Atk2P[0],
                                    y=positions.Atk2P[1],
                                    team=self.team_name,
                                    role = ATACKER2,
                                    id = 2,
                                    image = imagesRobot[2],
                                    initial_angle= initial_angle  
        )

        #Lista com os robôs para situações que sejam mais fáceis
        self.robots = [self.goalkeeaper, self.atacker1, self.atacker2]

    def reset_positions(self):
        '''
            Método responsável por colocar novamente os robôs na posição inicial
        '''
        for robot in self.robots:
            robot.reset()

    # Função para setar a nova posição
    def set_positions(self, positions:Position):
        '''
            Passo um objeto de posições com as posições dos robôs do time
        '''
        self.goalkeeaper.set_position(positions.GoalKeeperP[0],positions.GoalKeeperP[1])
        self.atacker1.set_position(positions.Atk1P[0],positions.Atk1P[1])
        self.atacker2.set_position(positions.Atk2P[0],positions.Atk2P[1])

# Configurações dos times

# ======== Valores padrões para as posições dos times para utilizar na classe Team
blue_team_positions = Position(
                                MID_GOALAREA_A,                 #Posição do goleiro 
                                ATK1_POSITION_SITUATION1_ALLY,  #Posição do ATK1
                                ATK2_POSITION_SITUATION2_ALLY   #Posição do ATK2
                                )

#Posição do time inimigo
red_team_positions = Position(
                                MID_GOALAREA_E,                 #Posição do goleiro
                                ATK1_POSITION_SITUATION1_ENEMY, #Posição do ATK1
                                ATK2_POSITION_SITUATION2_ENEMY  #Posição do ATK2
                                )