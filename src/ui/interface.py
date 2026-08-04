import pygame
import numpy as np
import pymunk
from ui.interface_config import *
from simulator.objects.ball import Ball
from simulator.objects.robot import Robot
from simulator.objects.field import Field

class Interface:
    def __init__(self, screen):
        pygame.display.set_caption(f"FoxSIM v{VERSION} - Simulador de futebol de robôs - por: Saulo José")

        self.field_image = pygame.image.load("src/assets/field.png")
        self.field_image = pygame.transform.scale(self.field_image, (int(WINDOWS_FIELD_WIDTH_PX), int(WINDOWS_FIELD_HEIGHT_PX)))

        icone = pygame.image.load("src/assets/logo_minus.png")
        pygame.display.set_icon(icone)

        self.screen = screen
        self.start_button = pygame.Rect(50, WINDOWS_FIELD_HEIGHT_PX + SCOREBOARD_HEIGHT_PX + 20, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.reset_button = pygame.Rect(50, WINDOWS_FIELD_HEIGHT_PX + SCOREBOARD_HEIGHT_PX + 20 + BUTTON_HEIGHT + BUTTON_SPACING, BUTTON_WIDTH, BUTTON_HEIGHT)

        self.draw_collision_objects = None
        self.running = None
        self.is_game_paused = None
        self.draw_grid_collision = None

        top = self.start_button.top
        bottom = self.reset_button.bottom
        left = self.start_button.right + 10
        width = BUTTON_WIDTH * 1.3
        height = bottom - top
        self.exibition_label = pygame.Rect(left, top, width, height)

        self.fonts = {
            "Arial": pygame.font.SysFont("Arial", 30),
            "Arial_small": pygame.font.SysFont("fixed", 11),
            "Menu": pygame.font.SysFont("Comic Sans MS", 20),
            "Timer": pygame.font.SysFont("OCR A Extended", 36),
            "Timer_small": pygame.font.SysFont("OCR A Extended", 18),
            "Buttons": pygame.font.SysFont("Verdana", 20),
            "Arcade": pygame.font.SysFont("Fixedsys", 40),
            "Arcade_small": pygame.font.SysFont("Fixedsys", 25),
        }

        self.score = [0, 0]

    def update_score(self, team):
        if team == 1:
            self.score[0] += 1
        elif team == 2:
            self.score[1] += 1

    def get_states(self, draw_collision_objects, running, is_game_paused, draw_grid_collision):
        self.draw_collision_objects = draw_collision_objects
        self.running = running
        self.is_game_paused = is_game_paused
        self.draw_grid_collision = draw_grid_collision

    def draw(self, time_left, screen, ball: Ball, robots: list, field: Field):
        screen.fill((200, 200, 200))

        minutes = int(time_left // 60)
        seconds = int(time_left % 60)

        # Área de configuração
        pygame.draw.rect(screen, (200, 200, 200), (0, WINDOWS_FIELD_HEIGHT_PX + SCOREBOARD_HEIGHT_PX,
                                                    WINDOWS_FIELD_WIDTH_PX + SIDEBAR_WIDTH_PX, CONFIG_HEIGHT_PX))

        # Campo de jogo
        screen.blit(self.field_image, (0, SCOREBOARD_HEIGHT_PX))

        # Desenha robôs e bola
        for robot in robots:
            robot.draw(screen)
        ball.draw(screen)

        # Desenho extra se ativado
        if self.draw_collision_objects:
            # --- Vetor de velocidade da bola ---
            max_speed = 100.0
            max_arrow_length = 30
            ball_speed = np.linalg.norm(ball.velocity)
            if ball_speed > 0:
                direction_virtual = ball.velocity / ball_speed
                direction_screen = np.array([direction_virtual[0], -direction_virtual[1]])
                length = min(ball_speed / max_speed * max_arrow_length, max_arrow_length)
                ball_screen_pos = virtual_to_screen(ball.position)
                end_pos = (
                    ball_screen_pos[0] + direction_screen[0] * length,
                    ball_screen_pos[1] + direction_screen[1] * length
                )
                t = min(ball_speed / max_speed, 1.0)
                r = int(255 * t)
                g = 0
                b = int(255 * (1 - t))
                color = (r, g, b)
                pygame.draw.line(screen, color, ball_screen_pos, end_pos, 3)
                head_length = 3
                perp = np.array([-direction_screen[1], direction_screen[0]])
                tip = np.array(end_pos)
                left = tip - direction_screen * head_length + perp * 3
                right = tip - direction_screen * head_length - perp * 3
                pygame.draw.polygon(screen, color, [tip, left, right])

            # --- Vetores de direção dos robôs ---
            for robot in robots:
                xbot, ybot = virtual_to_screen([robot.x, robot.y])
                dir_virtual = robot.direction
                dir_screen = np.array([dir_virtual[0], -dir_virtual[1]])
                speed = np.linalg.norm(robot.velocity)
                max_speed = 100
                length = 25 + (min(speed, max_speed) / max_speed) * 10
                end_x = xbot + dir_screen[0] * length
                end_y = ybot + dir_screen[1] * length
                end_pos = (end_x, end_y)
                color = (255, 100, 0)
                pygame.draw.line(screen, color, (xbot, ybot), end_pos, 2)
                head_length = 5
                direction_norm = dir_screen / np.linalg.norm(dir_screen)
                perp = np.array([-direction_norm[1], direction_norm[0]])
                tip = np.array(end_pos)
                left = tip - direction_norm * head_length + perp * 3
                right = tip - direction_norm * head_length - perp * 3
                pygame.draw.polygon(screen, color, [tip, left, right])

            # --- Desenho dos objetos de colisão (Pymunk) ---
            # Bola: shape circular
            if ball.shape:
                center_screen = virtual_to_screen(ball.body.position)
                radius_screen = ball.shape.radius / SCALE_PX_TO_CM
                pygame.draw.circle(screen, (0, 255, 0), (int(center_screen[0]), int(center_screen[1])),
                                   int(radius_screen), 2)

            # Robôs: polígonos
            for robot in robots:
                if robot.shape:
                    verts = robot.shape.get_vertices()
                    # Aplica rotação e depois translada
                    verts_global = [robot.body.position + v.rotated(robot.body.angle) for v in verts]
                    verts_screen = [virtual_to_screen(v) for v in verts_global]
                    pygame.draw.polygon(screen, (0, 255, 0), verts_screen, 2)

            # Campo: shapes estáticos (segmentos e círculos)
            for shape in field.space.shapes:
                if shape.body and shape.body.body_type == pymunk.Body.STATIC:
                    if isinstance(shape, pymunk.Segment):
                        p1 = virtual_to_screen(shape.a)
                        p2 = virtual_to_screen(shape.b)
                        pygame.draw.line(screen, (0, 255, 255), p1, p2, 2)
                    elif isinstance(shape, pymunk.Circle):
                        center_screen = virtual_to_screen(shape.body.position + shape.offset)
                        radius_screen = shape.radius / SCALE_PX_TO_CM
                        pygame.draw.circle(screen, (0, 255, 255), (int(center_screen[0]), int(center_screen[1])),
                                           int(radius_screen), 2)

            # Áreas de gol (RectHelper)
            if hasattr(field, 'goal_area_ally'):
                rect = field.goal_area_ally
                corners = [(rect.x - rect.width/2, rect.y - rect.height/2),
                           (rect.x + rect.width/2, rect.y - rect.height/2),
                           (rect.x + rect.width/2, rect.y + rect.height/2),
                           (rect.x - rect.width/2, rect.y + rect.height/2)]
                corners_screen = [virtual_to_screen(c) for c in corners]
                pygame.draw.polygon(screen, (0, 255, 0), corners_screen, 2)

            if hasattr(field, 'goal_area_enemy'):
                rect = field.goal_area_enemy
                corners = [(rect.x - rect.width/2, rect.y - rect.height/2),
                           (rect.x + rect.width/2, rect.y - rect.height/2),
                           (rect.x + rect.width/2, rect.y + rect.height/2),
                           (rect.x - rect.width/2, rect.y + rect.height/2)]
                corners_screen = [virtual_to_screen(c) for c in corners]
                pygame.draw.polygon(screen, (0, 255, 0), corners_screen, 2)

            # Grade de colisão
            if self.draw_grid_collision:
                x_start, x_end = BALL_INIT_MIN_X, BALL_INIT_MAX_X
                y_start, y_end = BALL_INIT_MIN_Y, BALL_INIT_MAX_Y
                for x in range(x_start, x_end + 1, int(CELL_SIZE / SCALE_PX_TO_CM)):
                    pygame.draw.line(screen, GRID_COLOR, (x, y_start), (x, y_end), 1)
                for y in range(y_start, y_end + 1, int(CELL_SIZE / SCALE_PX_TO_CM)):
                    pygame.draw.line(screen, GRID_COLOR, (x_start, y), (x_end, y), 1)

        # --- Interface (placar, temporizador, botões, label) ---
        blue_label = self.fonts["Timer_small"].render("Time A", True, (0, 0, 255))
        red_label = self.fonts["Timer_small"].render("Time B", True, (255, 0, 0))
        blue_score_surface = self.fonts["Timer"].render(str(self.score[0]), True, (0, 0, 255))
        red_score_surface = self.fonts["Timer"].render(str(self.score[1]), True, (255, 0, 0))

        blue_score_x = 60
        red_score_x = WINDOWS_FIELD_WIDTH_PX - 60

        screen.blit(blue_label, (blue_score_x - blue_label.get_width() // 2, 0))
        screen.blit(blue_score_surface, (blue_score_x - blue_score_surface.get_width() // 2, 15))
        screen.blit(red_label, (red_score_x - red_label.get_width() // 2, 0))
        screen.blit(red_score_surface, (red_score_x - red_score_surface.get_width() // 2, 15))

        # Temporizador
        time_surface = self.fonts["Timer"].render(f"{minutes:02}:{seconds:02}", True, (255, 255, 255))
        time_padding_x = 20
        time_padding_y = 2
        time_rect = time_surface.get_rect()
        time_bg_width = time_rect.width + time_padding_x * 2
        time_bg_height = time_rect.height + time_padding_y * 2
        time_bg_rect = pygame.Rect(
            WINDOWS_FIELD_WIDTH_PX // 2 - time_bg_width // 2,
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
        screen.blit(self.fonts["Buttons"].render("Iniciar", True, (0, 0, 0)),
                    self.fonts["Buttons"].render("Iniciar", True, (0, 0, 0)).get_rect(center=self.start_button.center))
        screen.blit(self.fonts["Buttons"].render("Resetar", True, (0, 0, 0)),
                    self.fonts["Buttons"].render("Resetar", True, (0, 0, 0)).get_rect(center=self.reset_button.center))

        # Label de status
        text = [
            " CONFIG. DA EXIBIÇÃO ",
            f"PAUSADO: {'SIM' if self.is_game_paused else 'NÃO'}",
            f"OBJ. COLISÃO: {'EXIBINDO' if self.draw_collision_objects else 'OCULTO'}",
            f"GRADE : {'EXIBINDO' if (self.draw_grid_collision and self.draw_collision_objects) else 'OCULTO'}",
            f"RODANDO: {'SIM' if self.running else 'NÃO'}",
        ]
        max_width = max(self.fonts["Arial_small"].size(line)[0] for line in text) + 20
        total_height = len(text) * 20 + 20
        self.exibition_label.width = max_width
        self.exibition_label.height = total_height
        y = self.exibition_label.top + 10

        pygame.draw.rect(screen, (0, 0, 0), self.exibition_label, width=1)

        ok_color = (0, 200, 0)
        no_color = (200, 0, 0)
        default_color = (0, 0, 0)
        keywords = {
            "EXIBINDO": ok_color,
            "SIM": ok_color,
            "OCULTO": no_color,
            "NÃO": no_color
        }

        for i, line in enumerate(text):
            parts = line.split(": ")
            if len(parts) < 2:
                line_surf = self.fonts["Arial_small"].render(line, True, default_color)
                line_y = y + i * 20
                screen.blit(line_surf, (self.exibition_label.left + 10, line_y))
                continue

            label_text = parts[0] + ":"
            status_text = parts[1]
            label_surf = self.fonts["Arial_small"].render(label_text, True, default_color)
            status_color = keywords.get(status_text.upper(), default_color)
            status_surf = self.fonts["Arial_small"].render(status_text, True, status_color)

            label_x = self.exibition_label.left + 10
            status_x = label_x + label_surf.get_width() + 5
            line_y = y + i * 20

            screen.blit(label_surf, (label_x, line_y))
            screen.blit(status_surf, (status_x, line_y))