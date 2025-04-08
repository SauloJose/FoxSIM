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

# === Instanciação de Objetos ===
print("[Sistema]: ======== Criando objetos ======= \n")
interface = Interface(screen)

#Gerando objetos da simulação
field = Field(FIELD_INTERNAL_WIDTH_IN_PX*SCALE_PX_TO_CM, FIELD_INTERNAL_HEIGHT_IN_PX*SCALE_PX_TO_CM, FIELD_COLOR)

print(f"\n[Sistema]: Criando a bola nas posições ({XVBALL_INIT},{YVBALL_INIT} e {BALL_RADIUS_CM})")
ball = Ball(XVBALL_INIT,YVBALL_INIT, field=field, radius=BALL_RADIUS_CM, color=BALL_COLOR)

#Só para debug:
print("\n[Sistema]: Criando robôs do time azul")
blue_team = Team(TEAM_BLUE_COLOR, blue_team_positions, "blue", initial_angle=0)

print("\n[Sistema]: Criando robôs do time vermelho")
red_team = Team(TEAM_RED_COLOR, red_team_positions, "red", initial_angle=180)

clock = pygame.time.Clock()
timer = HighPrecisionTimer(TIMER_PARTY)

# === Estados do Jogo ===
game_started = False
draw_collision_objects = False
draw_grid_collision = False
running = True
is_game_paused = False 

#Método para resetar configurações
def reset_simulation(timer):
    timer.stop()
    timer = HighPrecisionTimer(TIMER_PARTY)
    ball.reset_position(XVBALL_INIT, YVBALL_INIT)
    blue_team.reset_positions(blue_team_positions)
    red_team.reset_positions(red_team_positions)


print("\n[Simulador] ======== simulação PRONTA para iniciar ========")
# === Loop Principal ===
while running:
    dt = clock.tick(FPS) / 1000.0
    
        # --- Eventos ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                print("[Simulador]: Alternando exibição dos objetos de colisão")
                draw_collision_objects = not draw_collision_objects
            if event.key == pygame.K_i: #Exibir grade de colisões
                print("[Simulator] Exibindo grade de colisão")
                draw_grid_collision = not draw_grid_collision
            if event.key == pygame.K_p:
                is_game_paused = not is_game_paused
                if is_game_paused: 
                    timer.pause()
                    print('[Simulador]: Simulador pausou')

                else: 
                    timer.resume()
                    print('[Simulador]: Simulador retornou da pausa')

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            # Move a bola se o jogo estiver pausado e clique estiver dentro do campo
            
            if (BALL_INIT_MIN_X+PADDING_BALL_OK_PX) <= x <= (BALL_INIT_MAX_X-PADDING_BALL_OK_PX) and (BALL_INIT_MIN_Y+PADDING_BALL_OK_PX) <= y <= (BALL_INIT_MAX_Y-PADDING_BALL_OK_PX):
                ball.x, ball.y = screen_to_virtual([x, y]) 
                ball.collision_object.x = ball.x
                ball.collision_object.y = ball.y
                ball.velocity = 0
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
                field=field,
                screen=screen
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
                reset_simulation(timer)





    # Renderização na interface
    interface.get_states(draw_collision_objects=draw_collision_objects, running=game_started, is_game_paused=is_game_paused, draw_grid_collision = draw_grid_collision)
    interface.draw(
        time_left=timer.get_time_left(),
        screen=screen,
        ball=ball,
        field=field,
        robots=blue_team.robots + red_team.robots,
    )

        
    
    pygame.display.flip()
pygame.quit()
