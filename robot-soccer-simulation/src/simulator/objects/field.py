import pygame
from simulator.objects.collision import *

class Field:
    def __init__(self, width=600, height=600, color=(0, 0, 0)):
        """
        Inicializa o campo de jogo.
        :param width: Largura do campo em pixels.
        :param height: Altura do campo em pixels.
        :param color: Cor do campo (RGB).
        """
        self.width = width
        self.height = height
        self.color = color

        # Objetos de colisão (linhas e áreas do campo)
        self.collision_object = CollisionPolyLine([])

    def draw(self, screen):
        """
        Desenha o campo na tela e cria os objetos de colisão.
        :param screen: Superfície do pygame onde o campo será desenhado.
        """
        # Fundo do campo (preto)
        pygame.draw.rect(screen, self.color, (0, 0, self.width, self.height))

        # Linhas do campo
        line_color = (255, 255, 255)  # Branco
        line_thickness = 2

        # Linha central
        center_line_start = (self.width // 2, 0)
        center_line_end = (self.width // 2, self.height)
        pygame.draw.line(screen, line_color, center_line_start, center_line_end, line_thickness)
        self.collision_objects.append(("line", center_line_start, center_line_end))

        # Círculo central
        circle_radius = self.width // 10
        circle_center = (self.width // 2, self.height // 2)
        pygame.draw.circle(screen, line_color, circle_center, circle_radius, line_thickness)

        # Ponto central
        pygame.draw.circle(screen, line_color, circle_center, 3)

        # Gols
        goal_width = self.width // 15
        goal_height = self.height // 3
        left_goal = (0, (self.height - goal_height) // 2, goal_width, goal_height)
        right_goal = (self.width - goal_width, (self.height - goal_height) // 2, goal_width, goal_height)
        pygame.draw.rect(screen, line_color, left_goal, line_thickness)
        pygame.draw.rect(screen, line_color, right_goal, line_thickness)
        self.collision_objects.append(("rect", left_goal))
        self.collision_objects.append(("rect", right_goal))

        # Linhas dos gols
        left_goal_line_start = (goal_width, (self.height - goal_height) // 2)
        left_goal_line_end = (goal_width, (self.height + goal_height) // 2)
        pygame.draw.line(screen, line_color, left_goal_line_start, left_goal_line_end, line_thickness)
        self.collision_objects.append(("line", left_goal_line_start, left_goal_line_end))

        right_goal_line_start = (self.width - goal_width, (self.height - goal_height) // 2)
        right_goal_line_end = (self.width - goal_width, (self.height + goal_height) // 2)
        pygame.draw.line(screen, line_color, right_goal_line_start, right_goal_line_end, line_thickness)
        self.collision_objects.append(("line", right_goal_line_start, right_goal_line_end))

        # Marcas de posicionamento (cruzes)
        cross_size = self.width // 30
        cross_positions = [
            (self.width // 4, self.height // 4),
            (self.width // 4, 3 * self.height // 4),
            (3 * self.width // 4, self.height // 4),
            (3 * self.width // 4, 3 * self.height // 4),
        ]
        for x, y in cross_positions:
            pygame.draw.line(screen, line_color, (x - cross_size, y), (x + cross_size, y), line_thickness)
            pygame.draw.line(screen, line_color, (x, y - cross_size), (x, y + cross_size), line_thickness)

        # Adiciona os objetos de colisão para as bordas do campo
        self.collision_objects.append(("line", (0, 0), (self.width, 0)))  # Linha superior
        self.collision_objects.append(("line", (0, self.height), (self.width, self.height)))  # Linha inferior
        self.collision_objects.append(("line", (0, 0), (0, self.height)))  # Linha esquerda
        self.collision_objects.append(("line", (self.width, 0), (self.width, self.height)))  # Linha direita