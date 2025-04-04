import pygame

class Menu:
    def __init__(self, screen):
        """
        Inicializa o menu principal.
        :param screen: Superfície do pygame onde o menu será desenhado.
        """
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font = pygame.font.SysFont("Arial", 40)

        # Define os botões como retângulos
        self.start_button = pygame.Rect(self.width // 2 - 100, self.height // 2 - 100, 200, 50)
        self.settings_button = pygame.Rect(self.width // 2 - 100, self.height // 2, 200, 50)
        self.exit_button = pygame.Rect(self.width // 2 - 100, self.height // 2 + 100, 200, 50)

    def draw(self):
        """
        Desenha o menu na tela.
        """
        # Desenha o texto dos botões
        pygame.draw.rect(self.screen, (0, 0, 0), self.start_button)
        pygame.draw.rect(self.screen, (0, 0, 0), self.settings_button)
        pygame.draw.rect(self.screen, (0, 0, 0), self.exit_button)

        start_text = self.font.render("Start Game", True, (255, 255, 255))
        settings_text = self.font.render("Settings", True, (255, 255, 255))
        exit_text = self.font.render("Exit", True, (255, 255, 255))

        self.screen.blit(start_text, start_text.get_rect(center=self.start_button.center))
        self.screen.blit(settings_text, settings_text.get_rect(center=self.settings_button.center))
        self.screen.blit(exit_text, exit_text.get_rect(center=self.exit_button.center))