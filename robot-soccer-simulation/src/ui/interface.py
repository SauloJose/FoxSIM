import pygame
from ui.interface_config import *

# Dicionário de fontes da interface 
class Interface:
    def __init__(self, screen):
        self.screen = screen
        self.start_button = pygame.Rect(50, FIELD_HEIGHT + SCOREBOARD_HEIGHT + 20, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.reset_button = pygame.Rect(50, FIELD_HEIGHT + SCOREBOARD_HEIGHT + 20 + BUTTON_HEIGHT + BUTTON_SPACING, BUTTON_WIDTH, BUTTON_HEIGHT)

        # Ajusta a posição e altura da exibition_label com base nos botões
        top = self.start_button.top
        bottom = self.reset_button.bottom
        left = self.start_button.right + 10
        width = BUTTON_WIDTH*1.3
        height = bottom - top

        self.exibition_label = pygame.Rect(left, top, width, height)

        # Fontes utilizadas na interface (incluindo algumas gamificadas)
        self.fonts = {
                "Arial": pygame.font.SysFont("Arial", 30),
                "Arial_small": pygame.font.SysFont("Fixedsys", 15),
                "Menu": pygame.font.SysFont("Comic Sans MS", 20),
                "Timer": pygame.font.SysFont("OCR A Extended", 36),  # Fonte gamificada
                "Timer_small": pygame.font.SysFont("OCR A Extended", 18),  # Fonte gamificada
                "Buttons": pygame.font.SysFont("Verdana", 20),
                "Arcade": pygame.font.SysFont("Fixedsys", 40),  # Outra opção gamificada
                "Arcade_small": pygame.font.SysFont("Fixedsys", 25),
            }


        # Placar do jogo 
        self.score = [0, 0]  # [Team A, Team B]
        self.draw_collision_objects = None
        self.running = None
        self.is_game_paused = None

    def update_score(self, team):
        if team == 1:
            self.score[0] += 1
        elif team == 2:
            self.score[1] += 1

    def get_states(self, draw_collision_objects, running, is_game_paused):
        self.draw_collision_objects = draw_collision_objects
        self.running = running
        self.is_game_paused = is_game_paused

    def draw(self, time_left, screen, field_image, ball, robots, field):
        screen.fill((200, 200, 200))

        minutes = int(time_left // 60)
        seconds = int(time_left % 60)

        # Área de configuração
        pygame.draw.rect(screen, (200, 200, 200), (0, FIELD_HEIGHT + SCOREBOARD_HEIGHT, FIELD_WIDTH + SIDEBAR_WIDTH, CONFIG_HEIGHT))

        # Campo de jogo e robôs/bola primeiro
        screen.blit(field_image, (0, SCOREBOARD_HEIGHT))
        for robot in robots:
            robot.draw(screen)
        ball.draw(screen)

        # Desenho extra se ativado
        if self.draw_collision_objects:
            for robot in robots:
                corners = robot.collision_object.get_corners()
                pygame.draw.polygon(screen, (0, 255, 0), [(int(c[0]), int(c[1])) for c in corners], 3)

                dir_end = (robot.x + robot.direction[0] * 30, robot.y + robot.direction[1] * 30)
                pygame.draw.line(screen, (255, 100, 0), (robot.x, robot.y), dir_end, 2)
                pygame.draw.line(screen, (250, 20, 255), (robot.x, robot.y), (ball.x, ball.y), 1)

            pygame.draw.polygon(screen, (255, 255, 0), [(int(c[0]), int(c[1])) for c in field.RectUtil.get_corners()], 3)
            pygame.draw.polygon(screen, (0, 255, 0), [(int(c[0]), int(c[1])) for c in field.goal_area_ally.get_corners()], 3)
            pygame.draw.polygon(screen, (0, 255, 0), [(int(c[0]), int(c[1])) for c in field.goal_area_enemy.get_corners()], 3)

            pygame.draw.circle(screen, (0, 255, 0), (int(ball.collision_object.x), int(ball.collision_object.y)), ball.collision_object.radius, 1)

            x_start, x_end = fieldEx1[0], fieldEx2[0]
            y_start, y_end = fieldEx1[1], fieldEx4[1]
            for x in range(x_start, x_end + 1, CELL_SIZE):
                pygame.draw.line(screen, GRID_COLOR, (x, y_start), (x, y_end), 1)
            for y in range(y_start, y_end + 1, CELL_SIZE):
                pygame.draw.line(screen, GRID_COLOR, (x_start, y), (x_end, y), 1)

        # Interface (último plano por cima de tudo)

        # Posiciona o placar acima do campo
        blue_label = self.fonts["Timer_small"].render("Team A", True, (0, 0, 255))
        red_label = self.fonts["Timer_small"].render("Team B", True, (255, 0, 0))

        # Placar numérico logo abaixo
        blue_score_surface = self.fonts["Timer"].render(str(self.score[0]), True, (0, 0, 255))
        red_score_surface = self.fonts["Timer"].render(str(self.score[1]), True, (255, 0, 0))

        blue_score_x = 60
        red_score_x = FIELD_WIDTH - 60


        screen.blit(blue_label, (blue_score_x - blue_label.get_width() // 2, 0))
        screen.blit(blue_score_surface, (blue_score_x - blue_score_surface.get_width() // 2, 15))

        screen.blit(red_label, (red_score_x - red_label.get_width() // 2, 0))
        screen.blit(red_score_surface, (red_score_x - red_score_surface.get_width() // 2, 15))

        # Temporizador com fundo preto e fonte branca
        time_surface = self.fonts["Timer"].render(f"{minutes:02}:{seconds:02}", True, (255, 255, 255))
        time_padding_x = 20
        time_padding_y = 2
        time_rect = time_surface.get_rect()
        time_bg_width = time_rect.width + time_padding_x * 2
        time_bg_height = time_rect.height + time_padding_y * 2
        time_bg_rect = pygame.Rect(
            FIELD_WIDTH // 2 - time_bg_width // 2,
            5,
            time_bg_width,
            time_bg_height
        )
        pygame.draw.rect(screen, (0, 0, 0), time_bg_rect)
        screen.blit(time_surface, (time_bg_rect.centerx - time_surface.get_width() // 2,
                                time_bg_rect.centery - time_surface.get_height() // 2))
        
        # Botões
        pygame.draw.rect(screen, (0, 255, 0), self.start_button)
        pygame.draw.rect(screen, (255, 0, 0), self.reset_button)
        screen.blit(self.fonts["Buttons"].render("Iniciar", True, (0, 0, 0)), self.fonts["Buttons"].render("Iniciar", True, (0, 0, 0)).get_rect(center=self.start_button.center))
        screen.blit(self.fonts["Buttons"].render("Resetar", True, (0, 0, 0)), self.fonts["Buttons"].render("Resetar", True, (0, 0, 0)).get_rect(center=self.reset_button.center))

        # Informações de status (label lateral)
        text = [
            f"PAUSED: {'YES' if self.is_game_paused else 'NO'}",
            f"COLLISION OBJECTS: {'ON' if self.draw_collision_objects else 'OFF'}",
            f"RUNNING: {'YES' if self.running else 'NO'}"
        ]

        pygame.draw.rect(screen, (0, 0, 0), self.exibition_label, width=1)

        total_height = len(text) * 20
        y = self.exibition_label.centery - total_height // 2

        ok_color = (0, 200, 0)  # Verde
        no_color = (200, 0, 0)  # Vermelho
        default_color = (0, 0, 0)
        keywords = {
            "ON": ok_color,
            "YES": ok_color,
            "OFF": no_color,
            "NO": no_color
        }

        for i, line in enumerate(text):
            parts = line.split(": ")
            label_text = parts[0] + ":"
            status_text = parts[1]

            label_surf = self.fonts["Arial_small"].render(label_text, True, default_color)
            status_color = keywords.get(status_text.upper(), default_color)
            status_surf = self.fonts["Arial_small"].render(status_text, True, status_color)

            label_x = self.exibition_label.left + 10
            status_x = label_x + label_surf.get_width() + 5
            line_y = self.exibition_label.top + 10 + i * 20

            screen.blit(label_surf, (label_x, line_y))
            screen.blit(status_surf, (status_x, line_y))
