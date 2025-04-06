import pygame
import numpy as np  # Substitui math por numpy
from simulator.objects.collision import * 
from ui.interface_config import *

class Ball:
    def __init__(self, x, y, field, radius=BALL_RADIUS_CM, color=BALL_COLOR):
        """
        Inicializa a bola.
        :param x: Posição X da bola.
        :param y: Posição Y da bola.
        :param radius: Raio da bola em cm.
        :param color: Cor da bola (RGB).
        """
        #Variáveis espaciais
        self.x = x
        self.y = y
        self.type_object = BALL_OBJECT

        # Variáveis vetoriais 
        self.direction = np.array([1.0, 0.0])
        self.speed = 0  # Velocidade em pixels por segundo
        self.velocity = self.direction*self.speed  # Velocidade da bola (vx, vy)
        
        #Dados físicos para o simulador tratar das colisões
        self.radius = radius
        self.color = color  
        self.mass = BALL_MASS # Massa da bola em kg


        #ponteiro para o campo para verificar se ela está no gol ou não
        self.field = field 

        #Objeto de colisão para tratar das colisões 
        self.collision_object = CollisionCircle(self.x, self.y, self.radius, type_object=MOVING_OBJECTS, reference=self)

    def update_position(self, dt):
        """
        Atualiza a posição da bola com base na velocidade.
        :param dt: Delta time (tempo desde a última atualização).
        """
        position = np.array([self.x, self.y]) + self.velocity * dt
        self.x, self.y = position.tolist()

        self.collision_object.x = self.x
        self.collision_object.y = self.y 


    def is_inside_goal(self, goal_area:CollisionRectangle):
        """
        Verifica se a bola está dentro da área do gol.
        :param goal_area: Área do gol (CollisionRectangle).
        :return: True se a bola está dentro do gol, False caso contrário.
        """
        # Verifica se a bola está dentro da área do gol
        return goal_area.check_point_inside(self.collision_object)
    

    def set_velocity(self, vx, vy):
        """
        Define a velocidade da bola.
        :param vx: Velocidade no eixo X.
        :param vy: Velocidade no eixo Y.
        """
        self.velocity = np.array([vx, vy])
        self.speed = np.linalg.norm(self.velocity)  # Atualiza a velocidade linear
        
        if np.linalg.norm(self.velocity) > 0:
            self.direction = self.velocity /np.linalg.norm(self.velocity)  # Atualiza a direção


    def reset_position(self, x, y):
        """
        Reseta a posição da bola para as coordenadas fornecidas.
        :param x: Nova posição X.
        :param y: Nova posição Y.
        """
        self.x = x
        self.y = y
        self.velocity = np.array([0.0, 0.0])
        self.speed = 0
        self.direction = np.array([1.0, 0.0])

        self.collision_object.x = self.x
        self.collision_object.y = self.y

    def draw(self, screen):
        """
        Desenha a bola na tela.
        :param screen: Superfície do pygame onde a bola será desenhada.
        """
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def distance_to(self, x, y):
        """
        Calcula a distância até um ponto (x, y).
        :param x: Posição X do ponto.
        :param y: Posição Y do ponto.
        :return: Distância até o ponto.
        """
        return np.linalg.norm(np.array([self.x - x, self.y - y]))