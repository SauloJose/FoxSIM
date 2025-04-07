import pygame
import numpy as np
from ui.interface_config import ROBOT_SIZE_CM
from simulator.objects.collision import *

class Robot:
    def __init__(self, x, y, speed, team, role, color, ball, initial_direction=np.array([1.0,0.0]), rotation_speed=180):
        """
        Inicializa um robô.
        :param x: Posição X do robô.
        :param y: Posição Y do robô.
        :param speed: Velocidade linear do robô.
        :param team: Time do robô (ex: 'blue' ou 'red').
        :param role: Função do robô ('attacker' ou 'goalkeeper').
        :param color: Cor do robô (RGB).
        :param initial_direction: Ângulo inicial do robô (em graus).
        """
        #Posição do robô
        self.x = x
        self.y = y

        #O objeto PAI pode ser de dois tipos: MOVING e STRUCTURE
        self.type_object = ROBOT_OBJECT 

        #Dados cinéticos
        self.speed = speed
        self.first_direction = initial_direction
        self.direction = np.array(initial_direction)  # Ângulo em graus
        if np.linalg.norm(self.direction) == 0:
            self.direction = np.array([1.0, 0.0])  # Define uma direção padrão se o vetor for nulo
        self.direction = self.direction / np.linalg.norm(self.direction)  # Normaliza o vetor
       
        self.velocity = np.array([0.0,0.0]) # Velocidade do robô (vx, vy)
        
        self.rotation_speed= rotation_speed
        
        # Identificador dos robôs 
        self.team = team
        self.role = role
        self.color = color

        #Ponteiros à objetos do jogo 
        self.ball = ball #referência à bola

        #Dados físicos do robô
        self.width = ROBOT_SIZE_CM  # Largura do robô em pixels
        self.height = ROBOT_SIZE_CM  # Altura do robô em pixels
        self.mass = ROBOT_MASS  # Massa do robô em kg
        self.wheels_radius = ROBOT_WHEELS_RADIUS_CM  # Raio das rodas do robô em cm
        self.distance_wheels = ROBOT_DISTANCE_WHEELS_CM  # Distância entre as rodas em cm
        self.distance_wheels_to_center = ROBOT_DISTANCE_WHEELS_TO_CENTER_CM  # Distância do centro do robô até o meio das rodas em cm

        
        #Adicionando objeto de colisão
        self.collision_object = CollisionRectangle(self.x,self.y,self.width,self.height,type_object=MOVING_OBJECTS,reference=self)
        
        # Superfície para desenhar o robô com rotação
        width_px = int(self.width / SCALE_PX_TO_CM)
        height_px = int(self.height / SCALE_PX_TO_CM)

        self.image = pygame.Surface((width_px, height_px), pygame.SRCALPHA)
        
        
        pygame.draw.rect(self.image, self.color, (0, 0, width_px, height_px))

    def move(self, dt):
        """
        Move o robô com base na direção e velocidade.
        :param dt: Delta time (tempo desde a última atualização).
        """
        self.velocity = self.direction * self.speed 
        
        self.x += self.velocity[0] * dt
        self.y +=  self.velocity[1]* dt

        #Movendo objeto de colisão
        self.collision_object.x = self.x
        self.collision_object.y = self.y 
        self.sync_collision_object()

    def rotate(self, angle):
        """
        Rotaciona o robô em torno de seu centro.
        :param angle: Ângulo em graus para rotacionar.
        """

        radians = np.radians(angle)
        rotation_matrix = np.array([
            [np.cos(radians), -np.sin(radians)],
            [np.sin(radians), np.cos(radians)]
        ])
        self.direction = np.dot(rotation_matrix, self.direction)
        self.direction = self.direction / np.linalg.norm(self.direction)  # Normaliza o vetor
        
        self.velocity = self.direction * self.speed  #atualiza o vetor velocidade

        self.sync_collision_object()

    def turns_towards(self, target_x, target_y):
        """
        Gira o robô para apontar em direção a um ponto específico.
        :param target_x: Posição X do ponto alvo.
        :param target_y: Posição Y do ponto alvo.
        """
        dx = target_x - self.x
        dy = target_y - self.y
        direction = np.array([dx, dy], dtype=float)

        if np.linalg.norm(direction)>0:
            self.direction = direction / np.linalg.norm(direction)  # Normaliza o vetor
        
        self.velocity = self.direction * self.speed
        self.sync_collision_object()

    def turn_towards_ball(self, dt):
        """
        Ajusta gradualmente a direção do robô para apontar para a bola.
        :param dt: Delta time (tempo desde a última atualização).
        """
        # Calcula o vetor direção para a bola
        dx = self.ball.x - self.x
        dy = self.ball.y - self.y
        target_direction = np.array([dx, dy], dtype=float)

        # Verifica se o vetor direção é válido (evita divisão por zero)
        if np.linalg.norm(target_direction) > 0:
            target_direction = target_direction / np.linalg.norm(target_direction)  # Normaliza o vetor

            # Calcula o ângulo atual e o ângulo alvo
            current_angle = np.degrees(np.arctan2(self.direction[1], self.direction[0]))
            target_angle = np.degrees(np.arctan2(target_direction[1], target_direction[0]))

            # Calcula a diferença de ângulo
            angle_diff = (target_angle - current_angle + 360) % 360
            if angle_diff > 180:
                angle_diff -= 360

            # Ajusta a direção gradualmente, limitando a rotação por frame
            max_rotation = self.rotation_speed * dt
            rotation_angle = max_rotation if angle_diff > 0 else -max_rotation
            if abs(angle_diff) < max_rotation:
                rotation_angle = angle_diff  # Alinha diretamente se a diferença for pequena

            # Aplica a rotação
            self.rotate(rotation_angle)

    def distance_to(self, x, y):
        """
        Calcula a distância até um ponto (x, y).
        :param x: Posição X do ponto.
        :param y: Posição Y do ponto.
        :return: Distância até o ponto.
        """
        return np.linalg.norm(np.array([self.x - x, self.y - y]))
    
    def reset_position(self, x, y):
        """
        Reseta a posição do robô para as coordenadas fornecidas.
        :param x: Nova posição X.
        :param y: Nova posição Y.
        """
        self.x = x
        self.y = y
        self.direction = self.first_direction
        self.speed = 0
        self.velocity = self.direction*self.speed

        #Atualiza para o local do objeto
        self.collision_object.x = self.x 
        self.collision_object.y = self.y
        self.sync_collision_object()

    def set_speed(self, speed):
        """
        Define a velocidade do robô.
        :param speed: Velocidade em pixels por segundo.
        """
        self.speed = speed
        self.velocity = self.direction * self.speed
        self.sync_collision_object()

    def set_velocity(self, vx, vy):
        """
        Define a velocidade do robô.
        :param vx: Velocidade no eixo X.
        :param vy: Velocidade no eixo Y.
        """
        self.velocity = np.array([vx, vy])
        self.speed = np.linalg.norm(self.velocity)
        self.direction = self.velocity/np.linalg.norm(self.velocity)
        self.sync_collision_object()


    def set_position(self, x, y):
        """
        Define a posição do robô.
        :param x: Nova posição X.
        :param y: Nova posição Y.
        """
        self.x = x
        self.y = y
        self.direction = np.array([0.0,0.0])
        self.speed = 0
        self.velocity = np.array([0.0, 0.0])
        self.sync_collision_object()

    def set_color(self, color):
        """
        Define a cor do robô.
        :param color: Cor do robô (RGB).
        """
        self.color = color
        self.image.fill((0, 0, 0, 0))

    def stop(self):
        """
        Para o robô (define a velocidade como zero).
        """
        self.set_speed(0)
        self.set_velocity(0, 0)
        self.sync_collision_object()

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
        # Rotaciona a imagem do robô
        angle = np.degrees(np.arctan2(self.direction[1], self.direction[0]))
        rotated_image = pygame.transform.rotate(self.image, -angle)
        center = virtual_to_screen([self.x,self.y])
        rect = rotated_image.get_rect(center=center)

        #Atualiza o ângulo do objeot de colisão
        self.collision_object.angle = angle

        # Desenha o robô na tela
        screen.blit(rotated_image, rect.topleft)
