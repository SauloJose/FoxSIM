from simulator.collision.collision import *
from simulator.objects.field import Field
from simulator.objects.ball import Ball 
from simulator.objects.robot import Robot 
import numpy as np


def update_game_state(robots: list[Robot], ball: Ball, dt: float, field: Field):
    """
    Atualiza o estado do jogo com base no tempo dt.
    Inclui atualização de posição, movimentação, detecção e resposta de colisões via SAT.
    """
    # === 1. Atualiza a posição da bola
    ball.update_position(dt)

    # === 2. Atualiza os robôs (lógica de movimentação e decisão)
    '''
        Adicionar as inteligências para controlar os robôs e tomar as decisões
    '''
    for robot in robots:
        # Seta velocidades no robô
        robot.set_wheel_speeds(10, 10)

        # Move com controle diferencial
        robot.move(dt)

    # ========================= Detectar e resolver colisões ======================
    # === 3. Junta os objetos móveis (robôs + bola)
    moving_objects = [ball] + robots
    
    # === 6. Detecta e resolve colisões
    collision_manager = CollisionManagerSAT(cell_size=CELL_SIZE)

    collision_manager.detect_and_resolve(
        [obj.collision_object for obj in moving_objects] + field.collision_object.objects
    )

    # ================== Aplicar regras do jogo ====================================
    '''
        Aplicar as Regras da partida.
    '''


    # ==================== Enviar o FLAG que irá informar o que aconteceu no jogo
    return NO_POINT_YET
