from simulator.objects.collision import *
from simulator.objects.field import Field
import numpy as np

def update_game_state(robots, ball, dt, field_width, field_height, field_objects):
    """
    Atualiza o estado do jogo.
    """
    if isinstance(field_objects, CollisionPolyLine):
        field_objects = field_objects.objects

    # Cria o objeto Collision
    moving_objects = [ball] + robots
    collision = Collision(moving_objects, field_objects)

    # Atualiza a posição da bola
    ball.update_position(dt)

    # Lida com colisões
    collision.handle_collisions()

    # Move os robôs em direção à bola
    for robot in robots:
        robot.turn_towards_ball(dt)
        robot.move(dt)