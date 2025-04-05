import pygame
import numpy as np
from ui.interface_config import ROBOT_SIZE
from simulator.objects.collision import *

class Robot:
    def __init__(self, x, y, speed, team, role, color, ball, initial_direction=np.array([1.0,0.0]), rotation_speed=360):
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
        self.x = x
        self.y = y
        self.speed = speed

        self.direction = np.array(initial_direction)  # Ângulo em graus
        if np.linalg.norm(self.direction) == 0:
            self.direction = np.array([1.0, 0.0])  # Define uma direção padrão se o vetor for nulo
        self.direction = self.direction / np.linalg.norm(self.direction)  # Normaliza o vetor
       
        self.velocity = np.array([0.0,0.0]) # Velocidade do robô (vx, vy)
        
        self.rotation_speed= rotation_speed
        self.team = team
        self.role = role
        self.color = color

        self.ball = ball #referência à bola

        self.width = ROBOT_SIZE  # Largura do robô em pixels
        self.height = ROBOT_SIZE  # Altura do robô em pixels

        #Adicionando objeto de colisão
        self.collision_object = CollisionRectangle(self.x,self.y,self.width,self.height, ROBOT_OBJECT)
        
        # Superfície para desenhar o robô com rotação
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, self.color, (0, 0, self.width, self.height))

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

        self.collision_object.angle +=angle

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
        self.direction = np.array([1.0,0.0])
        self.speed = 0
        self.velocity = self.direction*self.speed

        #Atualiza para o local do objeto
        self.collision_object.x = self.x 
        self.collision_object.y = self.y

    def set_speed(self, speed):
        """
        Define a velocidade do robô.
        :param speed: Velocidade em pixels por segundo.
        """
        self.speed = speed
        self.velocity = self.direction * self.speed 

    def set_velocity(self, vx, vy):
        """
        Define a velocidade do robô.
        :param vx: Velocidade no eixo X.
        :param vy: Velocidade no eixo Y.
        """
        self.velocity = np.array([vx, vy])
        self.speed = np.linalg.norm(self.velocity)
        self.direction = self.velocity/np.linalg.norm(self.velocity)


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

    def draw(self, screen):
        """
        Desenha o robô na tela com rotação e um vetor indicando a direção.
        :param screen: Superfície do pygame onde o robô será desenhado.
        """
        # Rotaciona a imagem do robô
        angle = np.degrees(np.arctan2(self.direction[1], self.direction[0]))
        rotated_image = pygame.transform.rotate(self.image, -angle)
        rect = rotated_image.get_rect(center=(self.x, self.y))

        # Desenha o robô na tela
        screen.blit(rotated_image, rect.topleft)

        # Desenha o vetor de direção (verde)
        vector_length = 30  # Comprimento do vetor
        end_x = self.x + vector_length * self.direction[0]
        end_y = self.y + vector_length * self.direction[1]
        pygame.draw.line(screen, (0, 255, 0), (self.x, self.y), (end_x, end_y), 2)  # Linha verde