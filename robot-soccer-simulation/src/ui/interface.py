import pygame
from ui.interface_config import *

class Interface:
    def __init__(self, screen):
        self.screen = screen
        self.start_button = pygame.Rect(50, FIELD_HEIGHT + SCOREBOARD_HEIGHT + 20, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.reset_button = pygame.Rect(50, FIELD_HEIGHT + SCOREBOARD_HEIGHT + 20 + BUTTON_HEIGHT + BUTTON_SPACING, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.font = pygame.font.SysFont("Arial", 30)

        # Placar
        self.score = [0, 0]  # [Team A, Team B]

    def update_score(self, team):
        """
        Atualiza o placar para o time especificado.
        :param team: 1 para Team A, 2 para Team B.
        """
        if team == 1:
            self.score[0] += 1
        elif team == 2:
            self.score[1] += 1

    def draw(self, time_left):
        """
        Desenha a interface na tela.
        :param time_left: Tempo restante da partida (em segundos).
        """
        # Limpa a área do placar e temporizador com um fundo cinza claro
        pygame.draw.rect(self.screen, (200, 200, 200), (0, 0, FIELD_WIDTH, SCOREBOARD_HEIGHT))

        # Desenha o placar
        score_text = f"Team A: {self.score[0]} - Team B: {self.score[1]}"
        score_surface = self.font.render(score_text, True, (0, 0, 0))  # Texto preto
        self.screen.blit(score_surface, (20, 10))  # Posiciona o placar mais à esquerda

        # Desenha o temporizador
        minutes = int(time_left // 60)
        seconds = int(time_left % 60)
        time_text = f"Tempo: {minutes:02}:{seconds:02}"
        time_surface = self.font.render(time_text, True, (0, 0, 0))  # Texto preto
        self.screen.blit(time_surface, (FIELD_WIDTH // 2 + 50, 10))  # Posiciona o temporizador no lado direito

        # Desenha os botões
        pygame.draw.rect(self.screen, (0, 255, 0), self.start_button)  # Botão "Iniciar"
        pygame.draw.rect(self.screen, (255, 0, 0), self.reset_button)  # Botão "Resetar"

        # Desenha os textos dos botões
        start_text = self.font.render("Iniciar", True, (0, 0, 0))
        reset_text = self.font.render("Resetar", True, (0, 0, 0))
        self.screen.blit(start_text, start_text.get_rect(center=self.start_button.center))
        self.screen.blit(reset_text, reset_text.get_rect(center=self.reset_button.center))