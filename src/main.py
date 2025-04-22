import pygame
import pygame_gui 
import numpy as np

from simulator.objects.team import *
from simulator.objects.ball import Ball
from simulator.objects.field import Field
from simulator.objects.robot import Robot

from simulator.game_logic import *
from simulator.objects.timer import Stopwatch

from simulator.rules.rules  import *

from ui.interface import Interface
from ui.interface_config import *

from ui.mainWindow.MainWindows import *

# =======================
#Instalando dependÊncias necessárias
#

# === Inicialização ===
pygame.init()

#Inicializando areas da interface
screen = pygame.display.set_mode((int(WINDOWS_FIELD_WIDTH_PX), int(WINDOWS_FIELD_HEIGHT_PX + SCOREBOARD_HEIGHT_PX + CONFIG_HEIGHT_PX)))
manager = pygame_gui.UIManager((WINDOWS_FIELD_WIDTH_PX + SIDEBAR_WIDTH_PX, WINDOWS_FIELD_HEIGHT_PX + SCOREBOARD_HEIGHT_PX + CONFIG_HEIGHT_PX))

# === Instanciação de Objetos ===
print("[Sistema]: ======== Criando objetos ======= \n")
interface = Interface(screen)

#Gerando objetos da simulação
field = Field(FIELD_INTERNAL_WIDTH_IN_PX, FIELD_INTERNAL_HEIGHT_IN_PX, FIELD_COLOR)

print(f"\n[Sistema]: Criando a bola nas posições ({XVBALL_INIT},{YVBALL_INIT} e {BALL_RADIUS_CM})")
ball = Ball(XVBALL_INIT,YVBALL_INIT, field=field, radius=BALL_RADIUS_CM, color=BALL_COLOR)

#Só para debug:
print("\n[Sistema]: Criando robôs do time azul")
blue_team = Team(blue_team_positions,BLUE_TEAM, initial_angle=0)

print("\n[Sistema]: Criando robôs do time vermelho")
red_team = Team(red_team_positions, RED_TEAM, initial_angle=180)

# Gerando clock do jogo
clock = pygame.time.Clock()
timer = Stopwatch(TIMER_PARTY) #Gerando cronometro 

    
#Gerando motor físico para atualizar a simulação
Physics_Engine = Physics(allies=blue_team,enemies=red_team,ball=ball,dt=1.0/FPS,field=field,screen=screen)

# === Estados do Jogo ===
game_started = False
draw_collision_objects = False
draw_grid_collision = False
running = True
is_game_paused = False 

# Gerando Arbitro para entender o jogo
arbitrator = Arbitrator(ball, field, blue_team,red_team,interface,timer)

#Método para resetar configurações
def reset_simulation(timer:Stopwatch):
    timer.reset()
    timer.duration = TIMER_PARTY

    ball.reset_position()
    blue_team.reset_positions()
    red_team.reset_positions()
    interface.score = [0,0]


#Método para 
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
                ball.velocity = np.array([0,0],dtype=float)
            # Botões de interface
            if interface.start_button.collidepoint(x, y):
                if not is_game_paused: 
                    game_started = True
                    timer.start()
            elif interface.reset_button.collidepoint(x, y):
                if not is_game_paused: 
                    game_started = False
                    reset_simulation(timer)

    # --- Tratamento da simulação ---
    if not is_game_paused:
        # --- Atualização do Jogo ---
        if game_started:
            # Atualizando o dt para contabilizar a modificação dos clocks ou bugs
            Physics_Engine.dt = dt 
            Physics_Engine.collision_manager.dt = dt 

            #Atualizo a física do jogo e as posições dos robôs
            Physics_Engine.update()

            # O arbitro analisa a situação do game
            if arbitrator.analyzer() == Decisions.FINISH:
                game_started = False
                reset_simulation(timer)

    # --- Renderização ---
    interface.get_states(draw_collision_objects=draw_collision_objects, running=game_started, is_game_paused=is_game_paused, draw_grid_collision = draw_grid_collision)
    interface.draw(
        time_left=timer.get_time_left(),
        screen=screen,
        ball=ball,
        field=field,
        robots=blue_team.robots + red_team.robots,
    )

    # -- Atualização do Display ---
    pygame.display.flip()
pygame.quit()




