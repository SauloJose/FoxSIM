import pygame
import numpy as np
from ui.interface_config import ROBOT_SIZE_CM
from simulator.collision.collision import *

class Robot:
    '''
        Implementação dinâmica de um robô controlado por controle diferencial
    '''
    def __init__(self, x, y, team, role, color, initial_angle=0):
        '''
            Inicializando o robô
        '''
        #Coordenadas globais do robô no ambiente
        self.x = x 
        ''' Posição x do robô nas coordenadas globais'''
        self.y = y
        ''' Posição y do robô nas coordenadas globais'''
        self.theta = np.radians(initial_angle)  # Ângulo em radianos do eixo de rotação do robô com o eixo x do sistema cartesiano inicial
        ''' Angulo theta com a horizontal em radianos'''
        self.team = team                        # indicação do time
        self.role = role                        # função do robô
        self.color = color                      # Cor do robô


        # Tipo de objeto para o sistema de colisão
        self.type_object = ROBOT_OBJECT

        # Tamanhos e propriedades físicas
        self.width = ROBOT_SIZE_CM
        self.height = ROBOT_SIZE_CM
        self.mass = ROBOT_MASS
        self.wheels_radius = ROBOT_WHEELS_RADIUS_CM
        self.distance_wheels = ROBOT_DISTANCE_WHEELS_CM
        self.distance_wheels_to_center = ROBOT_DISTANCE_WHEELS_TO_CENTER_CM

        # Velocidades das rodas (em cm/s)
        self.v_l = 0.0  # esquerda
        self.v_r = 0.0  # direita

        # Velocidade linear e angular (no sentido)
        self.v = 0.0
        self.omega = 0.0

        # Vetor velocidade do robô para ser utilizado nos cálculos e resolução de colisões


        # Vetor de direção inicial
        self.direction = np.array([np.cos(self.theta), np.sin(self.theta)])

        #salva os valores iniciais para quando resetar
        self.initial_theta      = self.theta
        self.initial_vl         = self.v_l
        self.initial_vr         = self.v_r 
        self.initial_direction  = self.direction
        self.initial_v          = self.v 
        self.initial_omega      = self.omega
        self.initial_x          = self.x 
        self.initial_y          = self.y

        # Colisão
        self.collision_object = CollisionRectangle(self.x, self.y, self.width, self.height, type_object=MOVING_OBJECTS, reference=self)
        self.sync_collision_object()

        # Imagem para o Pygame
        width_px = int(self.width / SCALE_PX_TO_CM)
        height_px = int(self.height / SCALE_PX_TO_CM)
        self.image = pygame.Surface((width_px, height_px), pygame.SRCALPHA)
        pygame.draw.rect(self.image, self.color, (0, 0, width_px, height_px))

    #setando velocidade das rodas
    def set_wheel_speeds(self, v_l, v_r):
        """Define as velocidades das rodas esquerda e direita (em cm/s)."""
        self.v_l = v_l
        self.v_r = v_r

    #puxa as velocidades lineares das rodas
    def get_vec_velocity(self):
        """
            Retorna o vetor velocidade (vx, vy) do robô no referencial global
        """
        v = (self.v_r + self.v_l) / 2.0
        direction = np.array([np.cos(self.theta), np.sin(self.theta)])
        return v * direction

    # seta o vetor velocidade do robô
    def set_vec_velocity(self, vx,vy):
        """
        Define as velocidades das rodas com base em um vetor velocidade (global).
        Esse vetor é projetado na direção do robô e converte-se em v e ω.
        """
        # Converte o vetor global para velocidade linear desejada
        v_global = np.array([vx, vy])
        
        # Direção do robô
        direction = np.array([np.cos(self.theta), np.sin(self.theta)])

        # Projeta o vetor na direção do robô
        v = np.dot(v_global, direction)  # componente tangente ao robô

        # Considera ω como zero, pois só queremos seguir naquela direção
        omega = 0

        # Calcula velocidades das rodas
        self.v_l = v - (omega * self.distance_wheels / 2)
        self.v_r = v + (omega * self.distance_wheels / 2)


    # função para mover o robô devido um tempo dt
    def move(self, dt):
        """Atualiza posição e orientação usando modelo diferencial."""
        L = self.distance_wheels

        # Calcula velocidades linear e angular
        self.v = (self.v_r + self.v_l) / 2
        self.omega = (self.v_r - self.v_l) / L

        # Atualiza orientação
        self.theta += self.omega * dt

        # Atualiza posição
        self.x += self.v * np.cos(self.theta) * dt
        self.y += self.v * np.sin(self.theta) * dt

        # Atualiza vetor de direção
        self.direction = np.array([np.cos(self.theta), np.sin(self.theta)])

        self.sync_collision_object()

    def rotate(self, angle):
        """
        Rotaciona o robô em torno de seu centro.
        :param angle: Ângulo em graus para rotacionar.
        """
        self.theta += np.radians(angle)
        self.direction = np.array([np.cos(self.theta), np.sin(self.theta)])
        self.sync_collision_object()

    def distance_to(self, x, y):
        """
        Calcula a distância até um ponto (x, y).
        :param x: Posição X do ponto.
        :param y: Posição Y do ponto.
        :return: Distância até o ponto.
        """
        return np.linalg.norm(np.array([self.x - x, self.y - y]))
    
    def reset(self):
        """
        Reseta a posição do robô para as coordenadas fornecidas.
        :param x: Nova posição X.
        :param y: Nova posição Y.
        """
        #Reseta configurações do robô
        self.theta      = self.initial_theta  #Ângulo theta com a horizontal
        self.v_l        = self.initial_vl         
        self.v_r        = self.initial_vr          
        self.direction  = self.initial_direction  
        self.v          = self.initial_v          
        self.omega      = self.initial_omega   
        self.x          = self.initial_x          
        self.y          = self.initial_y       


        # Imagem para o Pygame
        width_px = int(self.width / SCALE_PX_TO_CM)
        height_px = int(self.height / SCALE_PX_TO_CM)
        self.image = pygame.Surface((width_px, height_px), pygame.SRCALPHA)
        pygame.draw.rect(self.image, self.color, (0, 0, width_px, height_px))

        self.sync_collision_object()

    def set_position(self, x, y):
        """
        Define a posição do robô.
        :param x: Nova posição X.
        :param y: Nova posição Y.
        """
        self.x = x
        self.y = y
        self.sync_collision_object()

    def set_color(self, color):
        """
        Define a cor do robô.
        :param color: Cor do robô (RGB).
        """
        self.color = color

    def stop(self):
        """
        Para o robô (define a velocidade como zero).
        """
        self.v_l = 0.0
        self.v_r = 0.0

    def sync_collision_object(self):
        """
        Sincroniza a posição do objeto de colisão com a posição do robô.
        """
        angle= np.degrees(np.arctan2(self.direction[1], self.direction[0]))
        self.collision_object.angle = angle
        self.collision_object.x = self.x
        self.collision_object.y = self.y

    def draw(self, screen):
        """
        Desenha o robô na tela com rotação e um vetor indicando a direção.
        :param screen: Superfície do pygame onde o robô será desenhado.
        """

        width_px = int(self.width / SCALE_PX_TO_CM)
        height_px = int(self.height / SCALE_PX_TO_CM)

        # Cria a imagem com a cor atual
        image = pygame.Surface((width_px, height_px), pygame.SRCALPHA)
        pygame.draw.rect(image, self.color, (0, 0, width_px, height_px))

        # Rotaciona a imagem conforme o ângulo atual
        angle = np.degrees(self.theta)
        rotated_image = pygame.transform.rotate(image, -angle)

        # Calcula posição central
        center = virtual_to_screen([self.x, self.y])
        rect = rotated_image.get_rect(center=center)

        # Desenha na tela
        screen.blit(rotated_image, rect.topleft)

