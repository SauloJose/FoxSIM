import pygame

class Scoreboard:
    def __init__(self, screen):
        """
        Inicializa o placar.
        :param screen: Superfície do pygame onde o placar será desenhado.
        """
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.score = [0, 0]  # [Team A, Team B]
        self.font = None  # Placeholder para o objeto de fonte

    def initialize_font(self, font_name='Arial', font_size=30):
        """
        Inicializa a fonte usada no placar.
        :param font_name: Nome da fonte.
        :param font_size: Tamanho da fonte.
        """
        self.font = pygame.font.SysFont(font_name, font_size)

    def update_score(self, team):
        """
        Atualiza o placar para o time especificado.
        :param team: 1 para Team A, 2 para Team B.
        """
        if team == 1:
            self.score[0] += 1
        elif team == 2:
            self.score[1] += 1

    def draw(self):
        """
        Desenha o placar na tela.
        """
        if self.font is None:
            self.initialize_font()
        score_text = f"Team A: {self.score[0]} - Team B: {self.score[1]}"
        text_surface = self.font.render(score_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.width // 2, 30))
        self.screen.blit(text_surface, text_rect)