import pygame
import numpy as np

from simulator.objects.team import *
from simulator.objects.ball import Ball
from simulator.objects.field import Field
from simulator.objects.robot import Robot

from simulator.game_logic import update_game_state
from simulator.objects.timer import HighPrecisionTimer

from ui.interface import Interface
from ui.interface_config import *

# === Inicialização ===
pygame.init()
screen = pygame.display.set_mode((WINDOWS_FIELD_WIDTH_PX, WINDOWS_FIELD_HEIGHT_PX + SCOREBOARD_HEIGHT_PX + CONFIG_HEIGHT_PX))
pygame.display.set_caption("Robot Soccer Simulation")

# === Carregamento de Recursos ===
field_image = pygame.image.load("robot-soccer-simulation/src/assets/field.png")
field_image = pygame.transform.scale(field_image, (WINDOWS_FIELD_WIDTH_PX, WINDOWS_FIELD_HEIGHT_PX))

# === Instanciação de Objetos ===
interface = Interface(screen)
field = Field(WINDOWS_FIELD_WIDTH_PX, WINDOWS_FIELD_HEIGHT_PX, FIELD_COLOR)
ball = Ball(WINDOWS_FIELD_WIDTH_PX // 2, SCOREBOARD_HEIGHT_PX + WINDOWS_FIELD_HEIGHT_PX // 2, field=field, radius=BALL_RADIUS_CM, color=BALL_COLOR)

blue_team = Team(TEAM_BLUE_COLOR, blue_team_positions, "blue", ball=ball, first_direction=np.array([1.0, 0.0]))
red_team = Team(TEAM_RED_COLOR, red_team_positions, "red", ball=ball, first_direction=np.array([-1.0, 0.0]))

clock = pygame.time.Clock()
timer = HighPrecisionTimer(TIMER_PARTY)

# === Estados do Jogo ===
game_started = False
draw_collision_objects = False
running = True
is_game_paused = False 

#Método para resetar configurações
def reset_simulation(timer):
    timer.stop()
    timer = HighPrecisionTimer(TIMER_PARTY)
    ball.reset_position(WINDOWS_FIELD_WIDTH_PX // 2, SCOREBOARD_HEIGHT_PX + WINDOWS_FIELD_HEIGHT_PX // 2)
    blue_team.reset_positions(blue_team_positions)
    blue_team.set_speed(50)
    red_team.reset_positions(red_team_positions)
    red_team.set_speed(50)


# === Loop Principal ===
while running:
    dt = clock.tick(FPS) / 1000.0
    
        # --- Eventos ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                print("Alternando exibição dos objetos de colisão")
                draw_collision_objects = not draw_collision_objects
            if event.key == pygame.K_p:
                is_game_paused = not is_game_paused
                if is_game_paused: 
                    timer.pause()
                    print('Simulador pausou')

                else: 
                    timer.resume()
                    print('Simulador retornou da pausa')

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            # Move a bola se o jogo estiver pausado e clique estiver dentro do campo
            if (fieldEx1[0]+PADDING_BALL_OK_PX) <= x <= (fieldEx2[0]-PADDING_BALL_OK_PX) and (fieldEx1[1]+PADDING_BALL_OK_PX) <= y <= (fieldEx3[1]-PADDING_BALL_OK_PX):
                ball.x, ball.y = x, y
                ball.collision_object.x = ball.x
                ball.collision_object.y = ball.y
            # Botões de interface
            if interface.start_button.collidepoint(x, y):
                if not is_game_paused: 
                    game_started = True
                    timer.start()
            elif interface.reset_button.collidepoint(x, y):
                if not is_game_paused: 
                    game_started = False
                    reset_simulation(timer)

    # --- Renderização ---
    #Informa estados à interface

    if not is_game_paused:
        # --- Atualização do Jogo ---
        if game_started:
            situation = update_game_state(
                robots=blue_team.robots + red_team.robots,
                ball=ball,
                dt=dt,
                field=field
            )

            if situation == POINT_ALLY:
                interface.update_score(1)
                game_started = False

            elif situation == POINT_ENEMY:
                interface.update_score(0)
                game_started = False

            elif timer.is_finished():
                print("Tempo esgotado! Fim da partida.")
                game_started = False




    # Renderização na interface
    interface.get_states(draw_collision_objects=draw_collision_objects, running=game_started, is_game_paused=is_game_paused)
    interface.draw(
        time_left=timer.get_time_left(),
        screen=screen,
        field_image=field_image,
        ball=ball,
        field=field,
        robots=blue_team.robots + red_team.robots,
    )

        
    
    pygame.display.flip()
pygame.quit()
