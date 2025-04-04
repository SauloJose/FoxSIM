import pygame
from ui.interface_config import BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_SPACING, CONFIG_COLOR, WINDOW_WIDTH, CONFIG_HEIGHT, FIELD_HEIGHT, SCOREBOARD_HEIGHT

class Interface:
    def __init__(self, screen):
        self.screen = screen
        # Define os botões "Iniciar" e "Resetar" um abaixo do outro
        self.start_button = pygame.Rect(50, FIELD_HEIGHT + SCOREBOARD_HEIGHT + 20, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.reset_button = pygame.Rect(50, FIELD_HEIGHT + SCOREBOARD_HEIGHT + 20 + BUTTON_HEIGHT + BUTTON_SPACING, BUTTON_WIDTH, BUTTON_HEIGHT)

    def draw(self):
        # Desenha a área de configurações (fundo da interface)
        pygame.draw.rect(self.screen, CONFIG_COLOR, (0, FIELD_HEIGHT + SCOREBOARD_HEIGHT, WINDOW_WIDTH, CONFIG_HEIGHT))

        # Desenha os botões
        pygame.draw.rect(self.screen, (0, 255, 0), self.start_button)  # Botão "Iniciar" (verde)
        pygame.draw.rect(self.screen, (255, 0, 0), self.reset_button)  # Botão "Resetar" (vermelho)

        # Desenha os textos dos botões
        font = pygame.font.SysFont("Arial", 20)
        start_text = font.render("Iniciar", True, (0, 0, 0))
        reset_text = font.render("Resetar", True, (0, 0, 0))
        self.screen.blit(start_text, start_text.get_rect(center=self.start_button.center))
        self.screen.blit(reset_text, reset_text.get_rect(center=self.reset_button.center))