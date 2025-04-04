import pygame

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

    def draw(self, screen):
        """
        Desenha o campo na tela.
        :param screen: Superfície do pygame onde o campo será desenhado.
        """
        # Fundo do campo (preto)
        pygame.draw.rect(screen, self.color, (0, 0, self.width, self.height))

        # Linhas do campo
        pygame.draw.line(screen, (255, 255, 255), (self.width // 2, 0), (self.width // 2, self.height), 2)  # Linha central
        pygame.draw.circle(screen, (255, 255, 255), (self.width // 2, self.height // 2), self.width // 10, 2)  # Círculo central

        # Gols
        goal_width = self.width // 15
        goal_height = self.height // 3
        pygame.draw.rect(screen, (255, 255, 255), (0, (self.height - goal_height) // 2, goal_width, goal_height), 2)  # Gol esquerdo
        pygame.draw.rect(screen, (255, 255, 255), (self.width - goal_width, (self.height - goal_height) // 2, goal_width, goal_height), 2)  # Gol direito

        # Linhas dos gols
        pygame.draw.line(screen, (255, 255, 255), (goal_width, (self.height - goal_height) // 2), (goal_width, (self.height + goal_height) // 2), 2)  # Gol esquerdo interno
        pygame.draw.line(screen, (255, 255, 255), (self.width - goal_width, (self.height - goal_height) // 2), (self.width - goal_width, (self.height + goal_height) // 2), 2)  # Gol direito interno

        # Marcas de posicionamento (cruzes)
        cross_size = self.width // 30
        cross_positions = [
            (self.width // 4, self.height // 4),
            (self.width // 4, 3 * self.height // 4),
            (3 * self.width // 4, self.height // 4),
            (3 * self.width // 4, 3 * self.height // 4),
        ]
        for x, y in cross_positions:
            pygame.draw.line(screen, (255, 255, 255), (x - cross_size, y), (x + cross_size, y), 2)  # Linha horizontal
            pygame.draw.line(screen, (255, 255, 255), (x, y - cross_size), (x, y + cross_size), 2)  # Linha vertical

        # Ponto central
        pygame.draw.circle(screen, (255, 255, 255), (self.width // 2, self.height // 2), 3)  # Ponto central