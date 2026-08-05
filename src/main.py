import pygame
import pygame_gui
import numpy as np
import pymunk 

from simulator.objects.team import Team
from simulator.objects.ball import Ball
from simulator.objects.field import Field
from simulator.objects.robot import Robot

from simulator.objects.timer import Stopwatch
from simulator.rules.rules import *
from ui.interface import Interface
from ui.interface_config import *
from simulator.intelligence.BT.strategies import *

import random

# Inicializa o temporizador com 2.0s
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
space.gravity = (0, 0)                # Sem gravidade (campo horizontal)
space.damping = 0.9995                # Amortecimento global
space.collision_slop = 0.01
space.collision_bias = (1 - 0.4) ** 60
space.iterations = 30

# === Instanciação de Objetos ===
print("\n" + "="*60)
print("[Sistema]: ======== Criando objetos e verificando coordenadas ========")
print("="*60)

interface = Interface(screen)

# Gerando campo
field = Field(space, width=FIELD_INTERNAL_WIDTH_IN_PX, height=FIELD_INTERNAL_HEIGHT_IN_PX, color=FIELD_COLOR)

# Gerando bola
ball = Ball(XVBALL_INIT, YVBALL_INIT, field=field, space=space,
            radius=BALL_RADIUS_CM, color=BALL_COLOR)
print(f"\n[Bola Criada]: Posição Inicial Interna (x={ball.x:.2f}, y={ball.y:.2f}) cm")

# Gerando time azul
print("\n[Time Azul]: Criando robôs e lendo estados internos...")
blue_team = Team(blue_team_positions, BLUE_TEAM, initial_angle=0, space=space)
for bot in blue_team.robots:
    print(f"  -> ID: {bot.id_robot:<2} | Função: {getattr(bot, 'role', 'N/A'):<12} | "
          f"Posição (x={bot.x:6.2f}, y={bot.y:6.2f}) cm | Ângulo: {np.degrees(bot.angle):6.1f}°")

# Gerando time vermelho
print("\n[Time Vermelho]: Criando robôs e lendo estados internos...")
red_team = Team(red_team_positions, RED_TEAM, initial_angle=180, space=space)
for bot in red_team.robots:
    print(f"  -> ID: {bot.id_robot:<2} | Função: {getattr(bot, 'role', 'N/A'):<12} | "
          f"Posição (x={bot.x:6.2f}, y={bot.y:6.2f}) cm | Ângulo: {np.degrees(bot.angle):6.1f}°")

# Exibindo referências dos Gols
print("\n[Gols]: Referências de Posição Configuradas:")
print(f"  -> Gol Aliado Azul (MID_GOALAREA_A): {MID_GOALAREA_A}")
print(f"  -> Gol Inimigo Vermelho (MID_GOALAREA_E): {MID_GOALAREA_E}")

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

# Gerando Árbitro
arbitrator = Arbitrator(ball, field, blue_team, red_team, interface, timer)

#Carregar as estratégias

# Método para resetar configurações
def reset_simulation(timer: Stopwatch):
    timer.reset()
    timer.duration = TIMER_PARTY

    ball.reset_position()          # Reseta posição e velocidades
    blue_team.reset_positions()    # Reseta posições dos robôs
    red_team.reset_positions()
    interface.score = [0, 0]

print("\n" + "="*60)
print("[Simulador]: ======== Simulação PRONTA para iniciar ========")
print("="*60 + "\n")

# === Loop Principal ===
frame_count = 0

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
                print("[Simulador]: Alternando exibição da grade de colisão")
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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            sx, sy = screen_to_virtual([x, y])
            point = (sx, sy)

            if is_game_paused:
                selected_robot = None
                for bot in bots:
                    bot._is_selected = False
                    info = bot.shape.point_query(point)
                    if info.distance <= 0:
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

        # Mouse Motion
        elif event.type == pygame.MOUSEMOTION:
            if selected_robot and is_game_paused:
                x, y = pygame.mouse.get_pos()
                sx, sy = screen_to_virtual([x, y])
                buttons = pygame.mouse.get_pressed()
                if buttons[0]:
                    can_move = True
                    for other_bot in bots:
                        if other_bot != selected_robot and other_bot.shape.point_query((sx, sy)).distance <= 0:
                            can_move = False
                            break
                    if can_move:
                        selected_robot.new_position(sx, sy)

        # Mouse Up
        elif event.type == pygame.MOUSEBUTTONUP:
            if selected_robot:
                selected_robot._is_selected = False
                selected_robot = None

    # --- Atualização da Física e Lógica ---
    if not is_game_paused:
        if game_started:
            frame_count += 1
            #print(f"--- [Tick {frame_count}] TELEMETRIA DA SIMULAÇÃO ---")
            
            # Telemetria + Tick do Time Azul
            for i, bot in enumerate(blue_team.robots):
                #print(f"  [Time Azul] Bot ID {bot.id_robot:<2} ({getattr(bot, 'role', 'N/A'):<10}) | "Pos: (x={bot.x:6.2f}, y={bot.y:6.2f}) cm")
                if i == 0:
                    target_pos = np.array([ball.x, ball.y], dtype=float)
                    v_l, v_r = bot.go_to_point(target_pos, None, dt)
                    # Limitar velocidades máximas
                    bot.set_wheel_speeds(v_l, v_r)
                else:
                    bot.set_wheel_speeds(0, 0)   # demais robôs azuis parados
                
            # Telemetria + Tick do Time Vermelho
            for bot in red_team.robots:
                #print(f"  [Time Vermelho] Bot ID {bot.id_robot:<2} ({getattr(bot, 'role', 'N/A'):<10}) | f"Pos: (x={bot.x:6.2f}, y={bot.y:6.2f}) cm")
                bot.set_wheel_speeds(0,0)
            # Telemetria da Bola
            #print(f"  [Bola] Pos: (x={ball.x:6.2f}, y={ball.y:6.2f}) cm")

        FIXED_DT = 1 / 60.0
        for bot in bots:
            bot.apply_motor_forces(FIXED_DT)

        # Atualização Física Pymunk
        space.step(FIXED_DT)

        # Ajustes na bola
        ball.clamp_velocity()
        ball.apply_damping(dt)

        # Arbitragem
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

    # --- AJUSTE AQUI ---
    # Passando as variáveis corretas: blue_team e red_team
    interface.draw_robot_logs(screen, blue_team, red_team)
    
    pygame.display.flip()

pygame.quit()