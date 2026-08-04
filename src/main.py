import pygame
import pygame_gui
import numpy as np
import pymunk 

from simulator.objects.team import Team
from simulator.objects.ball import Ball
from simulator.objects.field import Field
from simulator.objects.robot import Robot

#from simulator.game_logic import *          # (pode conter Physics, mas não será usado)
from simulator.objects.timer import Stopwatch
from simulator.rules.rules import *
from ui.interface import Interface
from ui.interface_config import *
from simulator.intelligence.strategies import *

import random

# Inicializa o temporizador com 5.0 para que os robôs já escolham
# uma velocidade aleatória logo no primeiro frame do jogo
tempo_mudanca = 2.0

# === Inicialização ===
pygame.init()

# Inicializando áreas da interface
screen = pygame.display.set_mode(
    (int(WINDOWS_FIELD_WIDTH_PX),
     int(WINDOWS_FIELD_HEIGHT_PX + SCOREBOARD_HEIGHT_PX + CONFIG_HEIGHT_PX))
)
manager = pygame_gui.UIManager(
    (WINDOWS_FIELD_WIDTH_PX + SIDEBAR_WIDTH_PX,
     WINDOWS_FIELD_HEIGHT_PX + SCOREBOARD_HEIGHT_PX + CONFIG_HEIGHT_PX)
)

# === Criação do espaço Pymunk ===
space = pymunk.Space()
space.gravity = (0, 0)                # sem gravidade (campo horizontal)
space.damping = 0.9995                # amortecimento global (opcional)

# === Instanciação de Objetos ===
print("[Sistema]: ======== Criando objetos ======= \n")
interface = Interface(screen)

# Gerando objetos da simulação (agora passamos o space)
field = Field(space, width=FIELD_INTERNAL_WIDTH_IN_PX, height=FIELD_INTERNAL_HEIGHT_IN_PX, color=FIELD_COLOR)

print(f"\n[Sistema]: Criando a bola nas posições ({XVBALL_INIT},{YVBALL_INIT})")
ball = Ball(XVBALL_INIT, YVBALL_INIT, field=field, space=space,
            radius=BALL_RADIUS_CM, color=BALL_COLOR)

print("\n[Sistema]: Criando robôs do time azul")
blue_team = Team(blue_team_positions, BLUE_TEAM, initial_angle=0, space=space)

print("\n[Sistema]: Criando robôs do time vermelho")
red_team = Team(red_team_positions, RED_TEAM, initial_angle=180, space=space)

# Ponteiro para todos os robôs
bots = blue_team.robots + red_team.robots

# Clock e temporizador
clock = pygame.time.Clock()
timer = Stopwatch(TIMER_PARTY)

# === Estados do Jogo ===
game_started = False
draw_collision_objects = False
draw_grid_collision = False
running = True
is_game_paused = False

selected_robot = None

# Gerando Árbitro (ainda usa as áreas do campo, agora RectHelper)
arbitrator = Arbitrator(ball, field, blue_team, red_team, interface, timer)

# Behavior trees
blue_bt = build_aggressive_strategy(
    own_goal=MID_GOALAREA_A,
    enemy_goal=MID_GOALAREA_E,
    forward_angle=0.0
)

red_bt = build_aggressive_strategy(
    own_goal=MID_GOALAREA_E,
    enemy_goal=MID_GOALAREA_A,
    forward_angle=np.pi
)

# Método para resetar configurações
def reset_simulation(timer: Stopwatch):
    timer.reset()
    timer.duration = TIMER_PARTY

    ball.reset_position()          # reseta posição e velocidades
    blue_team.reset_positions()    # reseta posições dos robôs
    red_team.reset_positions()
    interface.score = [0, 0]

print("\n[Simulador] ======== simulação PRONTA para iniciar ========")

# === Loop Principal ===
while running:
    dt = clock.tick(FPS) / 1000.0

    # --- Eventos ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Teclado
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                print("[Simulador]: Alternando exibição dos objetos de colisão")
                draw_collision_objects = not draw_collision_objects

            if event.key == pygame.K_i:
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

        # Mouse Down
        # Mouse Down
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            sx, sy = screen_to_virtual([x, y])
            point = (sx, sy)

            if is_game_paused:
                selected_robot = None
                for bot in bots:
                    bot._is_selected = False
                    # point_query retorna um objeto PointQueryInfo
                    info = bot.shape.point_query(point)
                    if info.distance <= 0:   # ponto está dentro ou na borda do polígono
                        bot._is_selected = True
                        selected_robot = bot
                        break

                if selected_robot is None:
                    if field.RectUtil.contains(point):
                        ball.position = (sx, sy)
                        ball.body.velocity = (0.0, 0.0)

                if event.button == 3 and selected_robot is not None:
                    selected_robot.rotate(15)

            # Botões da interface
            if interface.start_button.collidepoint(x, y):
                if not is_game_paused:
                    game_started = True
                    timer.start()
            elif interface.reset_button.collidepoint(x, y):
                if not is_game_paused:
                    game_started = False
                    reset_simulation(timer)

        # Mouse Motion (arrastar robô selecionado)
        elif event.type == pygame.MOUSEMOTION:
            if selected_robot and is_game_paused:
                x, y = pygame.mouse.get_pos()
                sx, sy = screen_to_virtual([x, y])
                buttons = pygame.mouse.get_pressed()
                if buttons[0]:  # botão esquerdo pressionado
                    selected_robot.new_position(sx, sy)

        # Mouse Up (desseleciona)
        elif event.type == pygame.MOUSEBUTTONUP:
            if selected_robot:
                selected_robot._is_selected = False
                selected_robot = None

    # --- Atualização da Física e Lógica (apenas se não pausado) ---
    if not is_game_paused:
        # Atualiza as árvores de comportamento (definem velocidades das rodas)
        if game_started:
            for bot in blue_team.robots:
                blue_bt.tick(robot=bot, ball=ball, team=blue_team,
                             enemy_team=red_team, dt=dt)
            for bot in red_team.robots:
                red_bt.tick(robot=bot, ball=ball, team=red_team,
                            enemy_team=blue_team, dt=dt)

        # --- Atualização Física com Pymunk ---
        # Aplica as velocidades desejadas nos robôs (cinemáticos) e na bola (dinâmica)
        # As classes Robot e Ball já atualizam seus corpos quando set_wheel_speeds
        # ou set_velocity são chamados.
        # Basta executar o step do espaço.
        space.step(dt)

        # Controles adicionais (opcionais): clamping da velocidade da bola
        ball.clamp_velocity()
        ball.apply_damping(dt)   # atrito linear suave

        # --- Arbitragem (verifica gol) ---
        if game_started and arbitrator.analyzer() == Decisions.FINISH:
            game_started = False
            reset_simulation(timer)

    # --- Renderização ---
    interface.get_states(
        draw_collision_objects=draw_collision_objects,
        running=game_started,
        is_game_paused=is_game_paused,
        draw_grid_collision=draw_grid_collision
    )
    interface.draw(
        time_left=timer.get_time_left(),
        screen=screen,
        ball=ball,
        field=field,
        robots=blue_team.robots + red_team.robots,
    )

    pygame.display.flip()

pygame.quit()