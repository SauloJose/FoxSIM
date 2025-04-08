import pygame
import numpy as np  # Substitui math por numpy
from simulator.collision.collision import * 
from ui.interface_config import *

class Ball:
    def __init__(self, x, y, field, radius=BALL_RADIUS_CM, color=BALL_COLOR):
        """
        Inicializa a bola.
        :param x: Posição X da bola na imagem principal
        :param y: Posição Y da bola na imagem principal
        :param radius: Raio da bola em cm.
        :param color: Cor da bola (RGB).
        """
        #Variáveis espaciais
        #Transforma as variáveis para o espaço virtual
        # Espaço vetorial
        self._position = np.array([x,y], dtype=float)
        self.velocity = np.zeros(2, dtype=float) #(vx, vy)
        self.direction = np.array([1.0,0.0],dtype=float)

        # Física
        self.radius = radius 
        self.mass = BALL_MASS 
        self.inertia = 0.5 *self.mass*self.radius**2 #Disco sólido
        self.angular_velocity =0.0  #rad/s


        # Outros
        self.color = color  
        self.type_object = BALL_OBJECT
        self.field = field 

        #Objeto de colisão para tratar das colisões 
        self.collision_object = CollisionCircle(
                self.x, self.y, self.radius,
                type_object=MOVING_OBJECTS, reference=self
                )

    #WHATCHDOGS
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, value):
        if not isinstance(value, np.ndarray):
            value = np.array(value, dtype=float)
        self._position = np.array(value, dtype=float)
        self.collision_object.x = self._position[0]
        self.collision_object.y = self._position[1]

    @property
    def x(self):
        return self.position[0]

    @x.setter
    def x(self, value):
        self._position[0] = value
        self.collision_object.x =value
        
    @property
    def y(self):
        return self.position[1]

    @y.setter
    def y(self, value):
        self._position[1] = value
        self.collision_object.y = value
    
    
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


    def update_position(self, dt):
        """
        Atualiza a posição da bola com base na velocidade.
        :param dt: Delta time (tempo desde a última atualização).
        """
        self.position += self.velocity*dt 

    def apply_impulse(self, impulse):
        '''
            Aplica um impulso na bola
        '''
        self.velocity +=impulse/self.mass 

    def apply_torque(self, torque, dt):
        """
        Aplica um torque na bola, alterando sua velocidade angular.
        :param torque: Torque aplicado (em N.m).
        :param dt: Intervalo de tempo (em segundos).
        """
        angular_acceleration = torque / self.inertia
        self.angular_velocity += angular_acceleration * dt


    def reset_position(self, x, y):
        """
        Reseta a posição da bola para as coordenadas fornecidas.
        :param x: Nova posição X.
        :param y: Nova posição Y.
        """
        self.position = np.array([x,y], dtype=float)
        self.velocity = np.zeros(2,dtype=float)
        self.direction =np.array([1.0, 0.0],dtype=float)
        self.speed = 0

        self.collision_object.x = self.x
        self.collision_object.y = self.y

    
    def is_inside_goal(self, goal_area:CollisionRectangle):
        """
        Verifica se a bola está dentro da área do gol.
        :param goal_area: Área do gol (CollisionRectangle).
        :return: True se a bola está dentro do gol, False caso contrário.
        """
        # Verifica se a bola está dentro da área do gol
        is_inside, mtv = goal_area.check_point_inside(self.collision_object)
        return is_inside
    
    def draw(self, screen):
        """
        Desenha a bola na tela.
        :param screen: Superfície do pygame onde a bola será desenhada.
        """
        #retorna posições na imagem antes de desenhar
        pos_img = virtual_to_screen([self.x,self.y])
        pygame.draw.circle(
            screen, self.color, (pos_img[0], pos_img[1]), 
            int(self.radius/SCALE_PX_TO_CM)
        )

    def distance_to(self, x, y):
        """
        Calcula a distância até um ponto (x, y).
        :param x: Posição X do ponto.
        :param y: Posição Y do ponto.
        :return: Distância até o ponto.
        """
        return np.linalg.norm(self.position - np.array([x,y]))