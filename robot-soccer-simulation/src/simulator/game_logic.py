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
        robot.move(dt)

    # ========================= Detectar e resolver colisões ======================
    # === 3. Junta os objetos móveis (robôs + bola)
    moving_objects = [ball] + robots

    # === 4. Injeta referências e types nos objetos de colisão móveis
    for obj in moving_objects:
        if obj.collision_object:
            obj.collision_object.reference = obj
            obj.collision_object.type_object = MOVING_OBJECTS

    # === 5. Injeta referências e types nos objetos de colisão do campo
    for struct in field.collision_object.objects:
        struct.reference = field
        struct.type_object = STRUCTURE_OBJECTS

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
