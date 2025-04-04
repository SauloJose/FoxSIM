import pygame
import math

class Ball:
    def __init__(self, x, y, radius=5, color=(255, 165, 0)):
        """
        Inicializa a bola.
        :param x: Posição X da bola.
        :param y: Posição Y da bola.
        :param radius: Raio da bola em cm.
        :param color: Cor da bola (RGB).
        """
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.velocity = [0, 0]  # Velocidade da bola (vx, vy)

    def update_position(self, dt):
        """
        Atualiza a posição da bola com base na velocidade.
        :param dt: Delta time (tempo desde a última atualização).
        """
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt

    def set_velocity(self, vx, vy):
        """
        Define a velocidade da bola.
        :param vx: Velocidade no eixo X.
        :param vy: Velocidade no eixo Y.
        """
        self.velocity = [vx, vy]

    def reset_position(self, x, y):
        """
        Reseta a posição da bola para as coordenadas fornecidas.
        :param x: Nova posição X.
        :param y: Nova posição Y.
        """
        self.x = x
        self.y = y
        self.velocity = [0, 0]

    def draw(self, screen):
        """
        Desenha a bola na tela.
        :param screen: Superfície do pygame onde a bola será desenhada.
        """
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)