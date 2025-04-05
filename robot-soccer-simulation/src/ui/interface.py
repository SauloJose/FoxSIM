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

    def draw(self, time_left, screen, field_image, ball, robots, draw_collision_objects):
        """
        Desenha a interface na tela.
        :param time_left: Tempo restante da partida (em segundos).
        :param screen: Superfície do pygame onde a interface será desenhada.
        :param field_image: Imagem do campo.
        :param ball: Objeto da bola.
        :param robots: Lista de robôs.
        :param draw_collision_objects: Booleano para desenhar objetos de colisão.
        """
        # Preenche o fundo da tela com cinza claro
        screen.fill((200, 200, 200))

        # Preenche a barra lateral com cinza claro
        pygame.draw.rect(screen, (200, 200, 200), (FIELD_WIDTH, SCOREBOARD_HEIGHT, SIDEBAR_WIDTH, FIELD_HEIGHT))

        # Preenche a área de configuração com cinza claro
        pygame.draw.rect(screen, (200, 200, 200), (0, FIELD_HEIGHT + SCOREBOARD_HEIGHT, FIELD_WIDTH + SIDEBAR_WIDTH, CONFIG_HEIGHT))

        # Desenha o placar do time azul (extremo esquerdo)
        blue_score_text = f"{self.score[0]}"
        blue_score_surface = self.font.render(blue_score_text, True, (0, 0, 255))  # Texto azul
        screen.blit(blue_score_surface, (20, 10))  # Posiciona no extremo esquerdo

        # Desenha o placar do time vermelho (extremo direito)
        red_score_text = f"{self.score[1]}"
        red_score_surface = self.font.render(red_score_text, True, (255, 0, 0))  # Texto vermelho
        screen.blit(red_score_surface, (FIELD_WIDTH - red_score_surface.get_width() - 20, SCOREBOARD_HEIGHT - red_score_surface.get_height() - 10)) 
       
        # Desenha o temporizador (centro do scoreboard)
        minutes = int(time_left // 60)
        seconds = int(time_left % 60)
        time_text = f"{minutes:02}:{seconds:02}"  # Formato MM:SS
        time_surface = self.font.render(time_text, True, (0, 0, 0))  # Texto preto
        screen.blit(time_surface, (FIELD_WIDTH // 2 - time_surface.get_width() // 2, 10))  # Centraliza no topo

        # Desenha os botões
        pygame.draw.rect(screen, (0, 255, 0), self.start_button)  # Botão "Iniciar"
        pygame.draw.rect(screen, (255, 0, 0), self.reset_button)  # Botão "Resetar"

        # Desenha os textos dos botões
        start_text = self.font.render("Iniciar", True, (0, 0, 0))
        reset_text = self.font.render("Resetar", True, (0, 0, 0))
        screen.blit(start_text, start_text.get_rect(center=self.start_button.center))
        screen.blit(reset_text, reset_text.get_rect(center=self.reset_button.center))

        # Desenha o campo (imagem de fundo)
        screen.blit(field_image, (0, SCOREBOARD_HEIGHT))

        # Desenha os robôs e a bola
        for robot in robots:
            robot.draw(screen)
        ball.draw(screen)

        # Desenha os objetos de colisão, vetores e linhas se ativado
        if draw_collision_objects:
            for robot in robots:
                # Obtém os cantos do retângulo de colisão
                corners = robot.collision_object.get_corners()

                # Desenha o retângulo rotacionado usando os cantos
                pygame.draw.polygon(
                    screen,
                    (255, 255, 0),  # Cor amarela para o retângulo
                    [(int(corner[0]), int(corner[1])) for corner in corners],  # Converte os pontos para inteiros
                    3  # Espessura da borda
                )

                # Desenha o vetor de direção do robô
                direction_vector_end = (
                    robot.x + robot.direction[0] * 30,  # Escala o vetor para visualização
                    robot.y + robot.direction[1] * 30
                )
                pygame.draw.line(
                    screen,
                    (0, 255, 255),  # Cor azul para o vetor de direção
                    (robot.x, robot.y),  # Ponto inicial (centro do robô)
                    direction_vector_end,  # Ponto final (direção escalada)
                    2  # Espessura da linha
                )

                # Desenha uma linha do robô até a bola
                pygame.draw.line(
                    screen,
                    (255, 255, 255),  # Cor vermelha para a linha até a bola
                    (robot.x, robot.y),  # Ponto inicial (centro do robô)
                    (ball.x, ball.y),  # Ponto final (centro da bola)
                    1  # Espessura da linha
                )

            # Desenha o objeto de colisão da bola
            pygame.draw.circle(
                screen,
                (0, 255, 0),  # Cor verde para o objeto de colisão
                (int(ball.collision_object.x), int(ball.collision_object.y)),
                ball.collision_object.radius,
                1,  # Espessura da borda
            )
  
