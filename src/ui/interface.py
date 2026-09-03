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
        self.target_debug = False
        self.running = None
        self.is_game_paused = None
        self.target_debug_ids = set()
        self.fps = 0.0
        self.arbitrator_decision = None

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
                "Timer": pygame.font.SysFont("OCR A Extended", 36),  # Fonte gamificada
                "Timer_small": pygame.font.SysFont("OCR A Extended", 18),  # Fonte gamificada
                "Buttons": pygame.font.SysFont("Verdana", 20),
                "Arcade": pygame.font.SysFont("Fixedsys", 40),  # Outra opção gamificada
                "Arcade_small": pygame.font.SysFont("Fixedsys", 25),
            }

        self.score = [0, 0]

    def update_score(self, team):
        if team == 1:
            self.score[0] += 1
        elif team == 2:
            self.score[1] += 1

    def get_states(self, draw_collision_objects, target_debug, running,
                   is_game_paused, target_debug_ids=None, fps=0.0,
                   arbitrator_decision=None):
        self.draw_collision_objects = draw_collision_objects
        self.target_debug = target_debug
        self.running = running
        self.is_game_paused = is_game_paused
        self.target_debug_ids = target_debug_ids or set()
        self.fps = fps
        self.arbitrator_decision = arbitrator_decision

    def _arbitrator_status(self):
        """Retorna uma mensagem curta e sua cor para o estado da partida."""
        decision_name = getattr(self.arbitrator_decision, "name", None)
        messages = {
            "ALLY_GOAL": "GOL A",
            "ENEMY_GOAL": "GOL B",
            "FINISH": "FIM DE JOGO",
            "RESTART": "REINICIO",
            "FOUL_ALLY": "FALTA A",
            "FOUL_ENEMY": "FALTA B",
            "PENALTY_ALLY": "PENALTI A",
            "PENALTY_ENEMY": "PENALTI B",
            "GK_AREA_VIOLATION_ALLY": "INVASAO A",
            "GK_AREA_VIOLATION_ENEMY": "INVASAO B",
            "THROW_IN_ALLY": "LATERAL A",
            "THROW_IN_ENEMY": "LATERAL B",
            "CORNER_ALLY": "ESCANTEIO A",
            "CORNER_ENEMY": "ESCANTEIO B",
            "GOALKICK_ALLY": "TIRO META A",
            "GOALKICK_ENEMY": "TIRO META B",
            "DROP_BALL": "BOLA AO CHAO",
        }
        infractions = {
            "RESTART",
            "FOUL_ALLY",
            "FOUL_ENEMY",
            "PENALTY_ALLY",
            "PENALTY_ENEMY",
            "GK_AREA_VIOLATION_ALLY",
            "GK_AREA_VIOLATION_ENEMY",
        }
        message = messages.get(decision_name, "JOGO NORMAL")
        color = (200, 0, 0) if decision_name in infractions else (0, 180, 0)
        return message, color

    def draw_robot_logs(self, screen, blue_team, red_team):
        # A caixa de logs ficará à direita da caixa de exibição
        left = self.exibition_label.right + 15
        top = self.exibition_label.top

        # Espaçamentos reduzidos para maior compactação
        padding = 10
        row_height = 30    # Altura de cada robô bem mais enxuta
        img_offset_x = 30  # Distância da imagem ao texto
        column_gap = 30    # Espaço horizontal entre as duas colunas
        font_size = 11
        max_robots = max(len(blue_team.robots), len(red_team.robots))
        if max_robots == 0:
            return

        # Fonte dedicada e menor (tamanho 9) para esta área
        font_log = pygame.font.SysFont("Arial",font_size)

        # Função auxiliar para extrair o theta (ângulo)
        def get_theta(robot):
            if hasattr(robot, 'angle'):
                return np.degrees(robot.angle)
            elif hasattr(robot, 'direction'):
                return np.degrees(np.arctan2(robot.direction[1], robot.direction[0]))
            return 0.0

        # --- 1. CÁLCULO DE LARGURAS DAS COLUNAS ---
        max_blue_width = 0
        for robot in blue_team.robots:
            theta = get_theta(robot)
            p_str = f"p: [{robot.x:.1f}, {robot.y:.1f}]"
            d_str = f"d: [{theta:.1f}°]"
            
            w_p = font_log.size(p_str)[0]
            w_d = font_log.size(d_str)[0]
            max_w = max(w_p, w_d) + img_offset_x

            if max_w > max_blue_width:
                max_blue_width = max_w

        max_red_width = 0
        for robot in red_team.robots:
            theta = get_theta(robot)
            p_str = f"p: [{robot.x:.1f}, {robot.y:.1f}]"
            d_str = f"d: [{theta:.1f}°]"
            
            w_p = font_log.size(p_str)[0]
            w_d = font_log.size(d_str)[0]
            max_w = max(w_p, w_d) + img_offset_x

            if max_w > max_red_width:
                max_red_width = max_w

        # --- 2. DIMENSIONAMENTO DA CAIXA ---
        total_width = padding + max_blue_width + column_gap + max_red_width + padding
        total_height = padding + (max_robots * row_height) + padding

        info_rect = pygame.Rect(left, top, total_width, total_height)
        pygame.draw.rect(screen, (0, 0, 0), info_rect, width=1)

        # --- 3. RENDERIZAÇÃO ---
        col1_x = info_rect.left + padding
        col2_x = col1_x + max_blue_width + column_gap
        start_y = info_rect.top + padding

        for i in range(max_robots):
            y_pos = start_y + (i * row_height)

            # --- Coluna Azul ---
            if i < len(blue_team.robots):
                robot = blue_team.robots[i]
                theta = get_theta(robot)

                if hasattr(robot, 'image') and robot.image:
                    img_y = y_pos + (row_height // 2) - (robot.image.get_height() // 2)
                    screen.blit(robot.image, (col1_x, img_y))

                surf_d = font_log.render(f"d: [{theta:.1f}°]", True, (0, 0, 255))

                # Linha 1 colada na linha 2 com apenas 10px de offset vertical
                surf_p = font_log.render(f"p: [{robot.x:.1f}, {robot.y:.1f}]", True, (0, 0, 255))
                screen.blit(surf_p, (col1_x + img_offset_x, y_pos + 1))
                screen.blit(surf_d, (col1_x + img_offset_x, y_pos + 11))

            # --- Coluna Vermelha ---
            if i < len(red_team.robots):
                robot = red_team.robots[i]
                theta = get_theta(robot)

                if hasattr(robot, 'image') and robot.image:
                    img_y = y_pos + (row_height // 2) - (robot.image.get_height() // 2)
                    screen.blit(robot.image, (col2_x, img_y))

                surf_d = font_log.render(f"d: [{theta:.1f}°]", True, (255, 0, 0))

                surf_p = font_log.render(f"p: [{robot.x:.1f}, {robot.y:.1f}]", True, (255, 0, 0))
                screen.blit(surf_p, (col2_x + img_offset_x, y_pos + 1))
                screen.blit(surf_d, (col2_x + img_offset_x, y_pos + 11))

    def _draw_target_debug(self, screen, robots, target_debug_ids):
        """Desenha target, velocidades e curva desejada dos robôs selecionados."""
        for robot in robots:
            if robot.id_robot not in (target_debug_ids or set()):
                continue

            robot_screen = virtual_to_screen(robot.position)
            target_screen = virtual_to_screen(robot.target_position)
            color = (0, 120, 255) if robot.team == BLUE_TEAM else (255, 80, 80)
            pygame.draw.line(screen, color, robot_screen, target_screen, 2)
            pygame.draw.circle(screen, color, target_screen, 7, 2)
            pygame.draw.line(screen, color,
                             (target_screen[0] - 5, target_screen[1]),
                             (target_screen[0] + 5, target_screen[1]), 2)
            pygame.draw.line(screen, color,
                             (target_screen[0], target_screen[1] - 5),
                             (target_screen[0], target_screen[1] + 5), 2)

            # Orientação atual do robô.
            self._draw_arrow(screen, (255, 0, 0), robot_screen,
                             (robot.direction[0], -robot.direction[1]), 25.0)

            # A velocidade desejada é uma linha simples, sem ponta de seta.
            self._draw_velocity_line(screen, (255, 165, 0), robot_screen,
                                      robot.desired_velocity)

    def _draw_ball_velocity(self, screen, ball):
        """Desenha a velocidade real da bola como uma reta laranja."""
        ball_screen = virtual_to_screen(ball.position)
        velocity = np.asarray(ball.velocity, dtype=float)
        speed = np.linalg.norm(velocity)
        if speed == 0:
            return
        self._draw_velocity_line(screen, (255, 165, 0), ball_screen, velocity)


    @staticmethod
    def _draw_arrow(screen, color, origin, direction, length):
        direction = np.asarray(direction, dtype=float)
        norm = np.linalg.norm(direction)
        if norm == 0:
            return
        direction = direction / norm
        end = np.asarray(origin, dtype=float) + direction * length
        perpendicular = np.array([-direction[1], direction[0]])
        pygame.draw.line(screen, color, origin, end, 2)
        pygame.draw.polygon(screen, color, [
            end,
            end - direction * 7 + perpendicular * 4,
            end - direction * 7 - perpendicular * 4,
        ])

    def _draw_velocity_line(self, screen, color, origin, vector):
        vector = np.asarray(vector, dtype=float)
        speed = np.linalg.norm(vector)
        if speed == 0:
            return
        screen_vector = np.array([vector[0], -vector[1]])
        direction = screen_vector / speed
        length = min(50.0, speed)
        end = np.asarray(origin, dtype=float) + direction * length
        pygame.draw.line(screen, color, origin, end, 3)

    def draw(self, time_left, screen, ball: Ball, robots: list, field: Field,
             target_debug_ids=None):
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

        if self.target_debug:
            self._draw_target_debug(screen, robots, target_debug_ids)

        if self.target_debug or self.draw_collision_objects:
            self._draw_ball_velocity(screen, ball)

        # Desenho extra se ativado
        if self.draw_collision_objects:
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
            f" INFORMAÇÕES (FPS: {int(round(self.fps))}) ",
            "DEBUG:",
            "ARBITRO:",
            f"PAUSADO: {'SIM' if self.is_game_paused else 'NÃO'}",
            f"OBJ. COLISÃO: {'EXIBINDO' if self.draw_collision_objects else 'OCULTO'}",
            f"RODANDO: {'SIM' if self.running else 'NÃO'}",
        ]
        max_width = max(self.fonts["Arial_small"].size(line)[0] for line in text) + 20
        total_height = len(text) * 20 + 20
        self.exibition_label.width = max_width
        self.exibition_label.height = total_height
        y = self.exibition_label.top + 10

        # Calcula dinamicamente a largura e altura do label
        max_width = max(self.fonts["Arial_small"].size(line)[0] for line in text) + 20  # 10px de padding em cada lado
        total_height = len(text) * 20 + 20  # 20px por linha + 10px de padding em cima e embaixo

        # Ajusta o tamanho do retângulo
        self.exibition_label.width = max_width
        self.exibition_label.height = total_height

        # Centraliza verticalmente o texto no label
        y = self.exibition_label.top + 10

        # Desenha o retângulo do label
        pygame.draw.rect(screen, (0, 0, 0), self.exibition_label, width=1)

        # Cores para os status
        ok_color = (0, 200, 0)  # Verde
        no_color = (200, 0, 0)  # Vermelho
        default_color = (0, 0, 0)
        keywords = {
            "EXIBINDO": ok_color,
            "SIM": ok_color,
            "OCULTO": no_color,
            "NÃO": no_color
        }

        # Renderiza o texto no label
        for i, line in enumerate(text):
            if line == "ARBITRO:":
                line_y = y + i * 20
                label_surf = self.fonts["Arial_small"].render(line, True, default_color)
                screen.blit(label_surf, (self.exibition_label.left + 10, line_y))
                message, message_color = self._arbitrator_status()
                status_x = self.exibition_label.left + 10 + label_surf.get_width() + 5
                status_surf = self.fonts["Arial_small"].render(message, True, message_color)
                screen.blit(status_surf, (status_x, line_y))
                continue

            if line == "DEBUG:":
                line_y = y + i * 20
                label_surf = self.fonts["Arial_small"].render(line, True, default_color)
                screen.blit(label_surf, (self.exibition_label.left + 10, line_y))
                status_x = self.exibition_label.left + 10 + label_surf.get_width() + 5
                for robot_id, label in ((0, "G"), (1, "A1"), (2, "A2")):
                    status_color = ok_color if self.target_debug and robot_id in self.target_debug_ids else no_color
                    status_surf = self.fonts["Arial_small"].render(label, True, status_color)
                    screen.blit(status_surf, (status_x, line_y))
                    status_x += status_surf.get_width() + 8
                continue

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