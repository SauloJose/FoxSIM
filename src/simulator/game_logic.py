from simulator.collision.collision import *
from simulator.objects.field import Field
from simulator.objects.ball import Ball 
from simulator.objects.robot import Robot 
import numpy as np


def update_game_state(allies: list[Robot],enemies: list[Robot], ball: Ball, dt: float, field: Field,screen):
    """
    Atualiza o estado do jogo com base no tempo dt.
    Inclui atualização de posição, movimentação, detecção e resposta de colisões via SAT.
    """
    # ========================= Detectar e resolver colisões ======================
    # === 1. Junta os objetos móveis (robôs + bola)
    moving_objects = [ball] + allies+enemies

    # ==== Juntando objetos de colisão
    all_collision_objects = [obj.collision_object for obj in moving_objects]
    all_collision_objects.append(field.collision_object)

    # === 4. Detecta e resolve colisões
    collision_manager = CollisionManagerSAT(cell_size=CELL_SIZE,screen=screen,dt=dt)
    
    collision_manager.detect_and_resolve(
        all_collision_objects
    )

    # ================== Atualizo as posições =====================================
    ball.update_position(dt)
    # === 2. Atualiza os robôs (lógica de movimentação e decisão)
    '''
        Adicionar as inteligências para controlar os robôs e tomar as decisões
    '''
    #Controlando aliados
    for robot in allies:
        # Seta velocidades no robô
        robot.set_wheel_speeds(20, 15)

        # Move com controle diferencial
        robot.move(dt)

    #Controlando inimigos
    for robot in enemies:
        # Seta velocidades no robô
        robot.set_wheel_speeds(-20, -25)

        # Move com controle diferencial
        robot.move(dt)

    # ================== Aplicar regras do jogo ====================================
    '''
        Aplicar as Regras da partida.
    '''


    # ==================== Enviar o FLAG que irá informar o que aconteceu no jogo
    return NO_POINT_YET
