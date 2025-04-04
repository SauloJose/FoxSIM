import pygame
import math
from ui.interface_config import ROBOT_SIZE
class Robot:
    def __init__(self, x, y, speed, team, role, color):
        """
        Inicializa um robô.
        :param x: Posição X do robô.
        :param y: Posição Y do robô.
        :param speed: Velocidade linear do robô.
        :param team: Time do robô (ex: 'blue' ou 'red').
        :param role: Função do robô ('attacker' ou 'goalkeeper').
        :param color: Cor do robô (RGB).
        """
        self.x = x
        self.y = y
        self.speed = speed
        self.direction = 0  # Ângulo em graus
        self.team = team
        self.role = role
        self.color = color
        self.width = ROBOT_SIZE  # Largura do robô em cm
        self.height = ROBOT_SIZE  # Altura do robô em cm

    def move(self, dt):
        """
        Move o robô com base na direção e velocidade.
        :param dt: Delta time (tempo desde a última atualização).
        """
        self.x += self.speed * math.cos(math.radians(self.direction)) * dt
        self.y += self.speed * math.sin(math.radians(self.direction)) * dt

    def turn(self, angle):
        """
        Gira o robô em um determinado ângulo.
        :param angle: Ângulo em graus para girar.
        """
        self.direction = (self.direction + angle) % 360

    def get_position(self):
        """
        Retorna a posição atual do robô.
        :return: Tupla (x, y).
        """
        return self.x, self.y

    def reset_position(self, x, y):
        """
        Reseta a posição do robô para as coordenadas fornecidas.
        :param x: Nova posição X.
        :param y: Nova posição Y.
        """
        self.x = x
        self.y = y

    def collide_with_ball(self, ball):
        """
        Verifica se o robô colidiu com a bola.
        :param ball: Objeto da classe Ball.
        :return: True se houve colisão, False caso contrário.
        """
        distance = math.sqrt((self.x - ball.x) ** 2 + (self.y - ball.y) ** 2)
        return distance < ball.radius + (self.width / 2)

    def handle_collision(self, ball):
        """
        Lida com a colisão entre o robô e a bola.
        :param ball: Objeto da classe Ball.
        """
        if self.collide_with_ball(ball):
            # Simples resposta de colisão: inverte a direção da bola
            ball.velocity[0] = -ball.velocity[0]
            ball.velocity[1] = -ball.velocity[1]
            ball.update_position(0.1)  # Move a bola ligeiramente para evitar sobreposição

    def draw(self, screen):
        """
        Desenha o robô na tela.
        :param screen: Superfície do pygame onde o robô será desenhado.
        """
        pygame.draw.rect(
            screen,
            self.color,
            (self.x - self.width / 2, self.y - self.height / 2, self.width, self.height)
        )