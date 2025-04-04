import pygame
from simulator.objects.team import blue_team, red_team, blue_team_positions, red_team_positions
from simulator.objects.ball import Ball
from simulator.objects.field import Field
from simulator.game_logic import update_game_state
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

# Estado do jogo
game_started = False

# Loop principal
running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    # Processa eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            # Verifica se o clique foi dentro do campo
            if 0 <= x <= FIELD_WIDTH and SCOREBOARD_HEIGHT <= y <= SCOREBOARD_HEIGHT + FIELD_HEIGHT:
                ball.x = x
                ball.y = y # Ajusta para compensar o placar acima do campo

            # Verifica se o clique foi em um botão
            if interface.start_button.collidepoint(x, y):
                game_started = True
            if interface.reset_button.collidepoint(x, y):
                game_started = False
                ball.reset_position(FIELD_WIDTH // 2, SCOREBOARD_HEIGHT + FIELD_HEIGHT // 2)
                blue_team.reset_positions(blue_team_positions)
                red_team.reset_positions(red_team_positions)

    # Atualiza o estado do jogo
    if game_started:
        update_game_state(blue_team.robots + red_team.robots, ball, dt)

    # Desenha o placar
    pygame.draw.rect(screen, SCOREBOARD_COLOR, (0, 0, FIELD_WIDTH, SCOREBOARD_HEIGHT))

    # Desenha o campo (imagem de fundo)
    screen.blit(field_image, (0, SCOREBOARD_HEIGHT))

    # Desenha as janelas laterais
    pygame.draw.rect(screen, SIDEBAR_COLOR_1, (FIELD_WIDTH, SCOREBOARD_HEIGHT, SIDEBAR_WIDTH, FIELD_HEIGHT // 2))
    pygame.draw.rect(screen, SIDEBAR_COLOR_2, (FIELD_WIDTH, SCOREBOARD_HEIGHT + FIELD_HEIGHT // 2, SIDEBAR_WIDTH, FIELD_HEIGHT // 2))

    # Desenha os robôs e a bola
    for robot in blue_team.robots + red_team.robots:
        robot.draw(screen)
    ball.draw(screen)

    # Desenha a interface (área de configurações com botões)
    interface.draw()

    # Atualiza a tela
    pygame.display.flip()

pygame.quit()