import pygame
import time
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

#Criação dos times
blue_team = Team(TEAM_BLUE_COLOR, blue_team_positions, "blue",ball=ball)
red_team = Team(TEAM_RED_COLOR, red_team_positions, "red",ball=ball)

# Estado do jogo
game_started = False

#Variável de controle para desenhar os objetos
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
                print("Mostrnado os objetos de colisão")
                draw_collision_objects = not draw_collision_objects

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            # Permite mover a bola apenas quando o jogo está pausado
            if not game_started and 0 <= x <= FIELD_WIDTH and SCOREBOARD_HEIGHT <= y <= SCOREBOARD_HEIGHT + FIELD_HEIGHT:
                ball.x = x
                ball.y = y # Ajusta para compensar o placar acima do campo

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
            field.collision_object.objects # Passa os objetos de colisão do campo
        )

        # Verifica se o tempo acabou
        if timer.is_finished():
            game_started = False
            print("Tempo esgotado! Fim da partida.")

    # Preenche o fundo da tela com cinza claro
    screen.fill((200, 200, 200))

    # Preenche a barra lateral com cinza claro
    pygame.draw.rect(screen, (200, 200, 200), (FIELD_WIDTH, SCOREBOARD_HEIGHT, SIDEBAR_WIDTH, FIELD_HEIGHT))

    # Preenche a área de configuração com cinza claro
    pygame.draw.rect(screen, (200, 200, 200), (0, FIELD_HEIGHT + SCOREBOARD_HEIGHT, FIELD_WIDTH + SIDEBAR_WIDTH, CONFIG_HEIGHT))

    # Desenha a interface com o tempo restante
    time_left = timer.get_time_left()
    interface.draw(time_left)

    # Desenha o campo (imagem de fundo)
    screen.blit(field_image, (0, SCOREBOARD_HEIGHT))

    # Desenha os robôs e a bola
    for robot in blue_team.robots + red_team.robots:
        robot.draw(screen)
    ball.draw(screen)


    if draw_collision_objects:
        # Desenha os objetos de colisão dos robôs
        for robot in blue_team.robots + red_team.robots:
            pygame.draw.rect(
                screen,
                (255, 0, 0),  # Cor vermelha para os objetos de colisão
                pygame.Rect(
                    robot.collision_object.x - robot.collision_object.width / 2,
                    robot.collision_object.y - robot.collision_object.height / 2,
                    robot.collision_object.width,
                    robot.collision_object.height,
                ),
                2,  # Espessura da borda
            )

        # Desenha o objeto de colisão da bola
        pygame.draw.circle(
            screen,
            (0, 255, 0),  # Cor verde para o objeto de colisão
            (int(ball.collision_object.x), int(ball.collision_object.y)),
            ball.collision_object.radius,
            1,  # Espessura da borda
        )

    # Atualiza a tela
    pygame.display.flip()

pygame.quit()