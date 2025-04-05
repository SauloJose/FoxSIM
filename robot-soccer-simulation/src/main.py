import pygame
import numpy as np  # Substitui math por numpy
from simulator.objects.team import *
from simulator.objects.ball import Ball
from simulator.objects.field import Field
from simulator.game_logic import update_game_state
from simulator.objects.timer import HighPrecisionTimer  # Importa o timer
from ui.interface import Interface
from ui.interface_config import *

# Inicializa o Pygame
pygame.init()

# Configurações da janela
screen = pygame.display.set_mode((FIELD_WIDTH + SIDEBAR_WIDTH, FIELD_HEIGHT + SCOREBOARD_HEIGHT + CONFIG_HEIGHT))
pygame.display.set_caption("Robot Soccer Simulation")

# Carrega a imagem do campo
field_image = pygame.image.load("robot-soccer-simulation/src/assets/field.png")
field_image = pygame.transform.scale(field_image, (FIELD_WIDTH, FIELD_HEIGHT))

# Criação da interface
interface = Interface(screen)

# Criação do campo
field = Field(FIELD_WIDTH, FIELD_HEIGHT, FIELD_COLOR)

# Criação da bola
ball = Ball(FIELD_WIDTH // 2, SCOREBOARD_HEIGHT + FIELD_HEIGHT // 2)

# Configurações do relógio
clock = pygame.time.Clock()

# Configuração do timer
timer = HighPrecisionTimer(TIMER_PARTY)

# Criação dos times
blue_team = Team(TEAM_BLUE_COLOR, blue_team_positions, "blue", ball=ball, first_direction=np.array([1.0, 0.0]))
red_team = Team(TEAM_RED_COLOR, red_team_positions, "red", ball=ball, first_direction=np.array([-1.0, 0.0]))

# Estado do jogo
game_started = False

# Variável de controle para desenhar os objetos
draw_collision_objects = False

# Loop principal
running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    # Processa eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                print("Alternando exibição dos objetos de colisão")
                draw_collision_objects = not draw_collision_objects

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            # Permite mover a bola apenas quando o jogo está pausado
            if not game_started and 0 <= x <= FIELD_WIDTH and SCOREBOARD_HEIGHT <= y <= SCOREBOARD_HEIGHT + FIELD_HEIGHT:
                ball.x = x
                ball.y = y  # Ajusta para compensar o placar acima do campo
                ball.collision_object.x = ball.x
                ball.collision_object.y = ball.y 

            # Verifica se o clique foi em um botão
            if interface.start_button.collidepoint(x, y):
                game_started = True
                timer.start()  # Inicia o timer
                
            if interface.reset_button.collidepoint(x, y):
                game_started = False
                timer.stop()  # Para o timer
                timer = HighPrecisionTimer(TIMER_PARTY)  # Reseta o timer
                ball.reset_position(FIELD_WIDTH // 2, SCOREBOARD_HEIGHT + FIELD_HEIGHT // 2)

                blue_team.reset_positions(blue_team_positions)
                blue_team.set_speed(50)

                red_team.reset_positions(red_team_positions)
                red_team.set_speed(50)

    # Atualiza o estado do jogo
    if game_started:
        update_game_state(
            blue_team.robots + red_team.robots,
            ball,
            dt,
            FIELD_WIDTH,
            FIELD_HEIGHT,
            field.collision_object.objects  # Passa os objetos de colisão do campo
        )

        # Verifica se o tempo acabou
        if timer.is_finished():
            game_started = False
            print("Tempo esgotado! Fim da partida.")

    # Atualiza a interface e desenha tudo
    interface.draw(
        time_left=timer.get_time_left(),
        screen=screen,
        field_image=field_image,
        ball=ball,
        robots=blue_team.robots + red_team.robots,
        draw_collision_objects=draw_collision_objects
    )

    # Atualiza a tela
    pygame.display.flip()

pygame.quit()