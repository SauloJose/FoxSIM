from simulator.objects.collision import *
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
    for robot in robots:
        robot.turn_towards_ball(dt)
        robot.move(dt)

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

    # Aqui garantimos que estamos passando SOMENTE objetos de colisão
    moving_collision_objects = [obj.collision_object for obj in moving_objects]
    static_collision_objects = field.collision_object.objects

    collision_manager.detect_and_resolve(
        [obj.collision_object for obj in moving_objects] + field.collision_object.objects
    )

    # === 7. Verifica se houve gol
    if ball.is_inside_goal(field.goal_area_ally):
        print("Gol do time aliado!")
        return POINT_ALLY

    elif ball.is_inside_goal(field.goal_area_enemy):
        print("Gol do time inimigo!")
        return POINT_ENEMY

    return NO_POINT_YET
