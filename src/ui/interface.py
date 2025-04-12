import pygame
from ui.interface_config import *
from simulator.objects.ball import Ball 
from simulator.objects.robot import Robot 
from simulator.objects.field import Field 
from simulator.collision.collision import *

# Dicionário de fontes da interface 
class Interface:
    def __init__(self, screen):
        # Nome da interface
        pygame.display.set_caption(f"FoxSIM v{VERSION} - Simulador de futebol de robôs - por: Saulo José")

        self.field_image = pygame.image.load("src/assets/field.png")
        self.field_image = pygame.transform.scale(self.field_image, (WINDOWS_FIELD_WIDTH_PX, WINDOWS_FIELD_HEIGHT_PX))

        #Setando ícone
        icone = pygame.image.load("src/assets/logo_minus.png")  # use o caminho da sua imagem
        pygame.display.set_icon(icone)

        # === Carregamento de Recursos ===
        self.screen = screen
        self.start_button = pygame.Rect(50, WINDOWS_FIELD_HEIGHT_PX + SCOREBOARD_HEIGHT_PX + 20, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.reset_button = pygame.Rect(50, WINDOWS_FIELD_HEIGHT_PX + SCOREBOARD_HEIGHT_PX + 20 + BUTTON_HEIGHT + BUTTON_SPACING, BUTTON_WIDTH, BUTTON_HEIGHT)

        #Variáveis internas 
        self.draw_collision_objects = None
        self.running = None
        self.is_game_paused = None
        self.draw_grid_collision = None

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

    def get_states(self, draw_collision_objects, running, is_game_paused, draw_grid_collision):
        self.draw_collision_objects = draw_collision_objects
        self.running = running
        self.is_game_paused = is_game_paused
        self.draw_grid_collision = draw_grid_collision 

    def draw(self, time_left, screen, ball:Ball, robots:Robot, field:Field):
        screen.fill((200, 200, 200))

        minutes = int(time_left // 60)
        seconds = int(time_left % 60)

        # Área de configuração
        pygame.draw.rect(screen, (200, 200, 200), (0, WINDOWS_FIELD_HEIGHT_PX + SCOREBOARD_HEIGHT_PX, WINDOWS_FIELD_WIDTH_PX + SIDEBAR_WIDTH_PX, CONFIG_HEIGHT_PX))

        # Campo de jogo e robôs/bola primeiro
        screen.blit(self.field_image, (0, SCOREBOARD_HEIGHT_PX))

        #Desenhando objetos do jogo
        for robot in robots:
            robot.draw(screen)
        ball.draw(screen)
        
        # Desenho extra se ativado
        if self.draw_collision_objects:
            #Desenhando a linha da direção da bola
             # === Vetor de velocidade da bola (corrigido com escala e Y invertido) ===
            max_speed = 100.0  # cm/s (ajuste conforme sua física)
            max_arrow_length = 30  # pixels

            ball_speed = np.linalg.norm(ball.velocity)
            if ball_speed > 0:
                # Direção normalizada no sistema virtual
                direction_virtual = ball.velocity / ball_speed

                # Corrigindo direção para Pygame (inverte Y e ajusta escala)
                direction_screen = np.array([direction_virtual[0], -direction_virtual[1]])

                # Tamanho proporcional
                length = min(ball_speed / max_speed * max_arrow_length, max_arrow_length)

                # Posição da bola na tela
                ball_screen_pos = virtual_to_screen(ball.position)
                end_pos = (
                    ball_screen_pos[0] + direction_screen[0] * length,
                    ball_screen_pos[1] + direction_screen[1] * length
                )

                # Interpolação de cor: azul → vermelho
                t = min(ball_speed / max_speed, 1.0)
                r = int(255 * t)
                g = 0
                b = int(255 * (1 - t))
                color = (r, g, b)

                # Linha do vetor velocidade
                pygame.draw.line(screen, color, ball_screen_pos, end_pos, 3)

                # Cabeça da seta
                head_length = 3
                perp = np.array([-direction_screen[1], direction_screen[0]])
                tip = np.array(end_pos)
                left = tip - direction_screen * head_length + perp * 3
                right = tip - direction_screen * head_length - perp * 3
                pygame.draw.polygon(screen, color, [tip, left, right])

            #Para os robôs
            for robot in robots:
                # Desenha o retângulo do objeto de colisão
                corners = np.array([virtual_to_screen(corner) for corner in robot.collision_object.get_corners()])
                pygame.draw.polygon(screen, (0, 255, 0), [(int(c[0]), int(c[1])) for c in corners], 3)

                # Centro do robô na tela
                xbot, ybot = virtual_to_screen([robot.x, robot.y])

                # Direção no sistema virtual → ajusta para Pygame (inverte Y e escala)
                dir_virtual = robot.direction
                dir_screen = np.array([dir_virtual[0], -dir_virtual[1]])  # escala de 3x

                # Comprimento da seta proporcional à velocidade (mínimo 10px, máximo 20px)
                speed = np.linalg.norm(robot.velocity)  # em cm/s
                max_speed = 100  # velocidade que representa o máximo comprimento (ajuste conforme o modelo)

                # Mapeia a velocidade para o intervalo [10, 20]
                length = 25 + (min(speed, max_speed) / max_speed) * 10

                # Vetor direção em coordenadas de tela (já está normalizado)
                end_x = xbot + dir_screen[0] * length
                end_y = ybot + dir_screen[1] * length
                end_pos = (end_x, end_y)

                # Cor da seta (laranja)
                color = (255, 100, 0)

                # Desenha a linha da direção
                pygame.draw.line(screen, color, (xbot, ybot), end_pos, 2)

                # Cabeça da seta    

                head_length = 5
                direction_norm = dir_screen / np.linalg.norm(dir_screen)
                perp = np.array([-direction_norm[1], direction_norm[0]])  # perpendicular para fazer a ponta

                tip = np.array(end_pos)
                left = tip - direction_norm * head_length + perp * 3
                right = tip - direction_norm * head_length - perp * 3

                pygame.draw.polygon(screen, color, [tip, left, right])

            # Desenhando os objetos de colisão para o campo
            # Rect Util
            #rect_util_screen = np.array([virtual_to_screen(corner) for corner in field.RectUtil.get_corners()])

            # goal_area_ally
            goal_area_ally_screen = np.array([virtual_to_screen(corner) for corner in field.goal_area_ally.get_corners()])

            # goal_area_enemy
            goal_area_enemy_screen = np.array([virtual_to_screen(corner) for corner in field.goal_area_enemy.get_corners()])

            #Objeto de colisão da bola
            ball_collision_center  = virtual_to_screen([ball.collision_object.x,ball.collision_object.y])
            ball_collision_radius = ball.collision_object.radius / SCALE_PX_TO_CM
            
            for obj in field.collision_object.objects:
                if isinstance(obj, CollisionRectangle):
                    # Obtenha os vértices do retângulo e converta para coordenadas de tela
                    vertices = [virtual_to_screen(v) for v in obj.get_corners()]
                    pygame.draw.polygon(screen, (0, 255, 255), vertices, width=0)  # Preenchido
                if isinstance(obj, CollisionCircle):
                    obj_c = virtual_to_screen(obj.center)
                    obj_r = obj.radius/SCALE_PX_TO_CM
                    pygame.draw.circle(screen, (0, 255, 0), (int(obj_c[0]),int(obj_c[1])), radius=int(obj_r), width=2)



            # Desenhar o campo 
            #pygame.draw.polygon(screen, (255, 255, 0), [(int(c[0]), int(c[1])) for c in rect_util_screen], 3)
            pygame.draw.polygon(screen, (0, 255, 0), [(int(c[0]), int(c[1])) for c in goal_area_ally_screen], 3)
            pygame.draw.polygon(screen, (0, 255, 0), [(int(c[0]), int(c[1])) for c in goal_area_enemy_screen], 3)

            pygame.draw.circle(screen, (0, 255, 0), (ball_collision_center[0],ball_collision_center[1]), ball_collision_radius, 1)
            
            #Verifica se desenha ou não o grid
            if self.draw_grid_collision:
                # Desenhando os grids do sistema de detecção
                x_start, x_end = BALL_INIT_MIN_X, BALL_INIT_MAX_X
                y_start, y_end = BALL_INIT_MIN_Y, BALL_INIT_MAX_Y 

                for x in range(x_start, x_end + 1, int(CELL_SIZE/SCALE_PX_TO_CM)):
                    pygame.draw.line(screen, GRID_COLOR, (x, y_start), (x, y_end), 1)
                for y in range(y_start, y_end + 1, int(CELL_SIZE/SCALE_PX_TO_CM)):
                    pygame.draw.line(screen, GRID_COLOR, (x_start, y), (x_end, y), 1)

        # Interface (último plano por cima de tudo)

        # Posiciona o placar acima do campo
        blue_label = self.fonts["Timer_small"].render("Time A", True, (0, 0, 255))
        red_label = self.fonts["Timer_small"].render("Time B", True, (255, 0, 0))

        # Placar numérico logo abaixo
        blue_score_surface = self.fonts["Timer"].render(str(self.score[0]), True, (0, 0, 255))
        red_score_surface = self.fonts["Timer"].render(str(self.score[1]), True, (255, 0, 0))

        blue_score_x = 60
        red_score_x = WINDOWS_FIELD_WIDTH_PX - 60


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
        screen.blit(self.fonts["Buttons"].render("Iniciar", True, (0, 0, 0)), self.fonts["Buttons"].render("Iniciar", True, (0, 0, 0)).get_rect(center=self.start_button.center))
        screen.blit(self.fonts["Buttons"].render("Resetar", True, (0, 0, 0)), self.fonts["Buttons"].render("Resetar", True, (0, 0, 0)).get_rect(center=self.reset_button.center))

        # Informações de status (label lateral)
        text = [
            " CONFIG. DA EXIBIÇÃO ",
            f"PAUSADO: {'SIM' if self.is_game_paused else 'NÃO'}",
            f"OBJ. COLISÃO: {'EXIBINDO' if self.draw_collision_objects else 'OCULTO'}",
            f"GRADE : {'EXIBINDO' if (self.draw_grid_collision and self.draw_collision_objects) else 'OCULTO'}",
            f"RODANDO: {'SIM' if self.running else 'NÃO'}",
        ]

        pygame.draw.rect(screen, (0, 0, 0), self.exibition_label, width=1)

        total_height = len(text) * 20
        y = self.exibition_label.centery - total_height // 2

        ok_color = (0, 200, 0)  # Verde
        no_color = (200, 0, 0)  # Vermelho
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
                # Linha sem status (ex: título ou decorativa), renderiza como texto normal
                line_surf = self.fonts["Arial_small"].render(line, True, default_color)
                line_y = self.exibition_label.top + 10 + i * 20
                screen.blit(line_surf, (self.exibition_label.left + 10, line_y))
                continue

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
