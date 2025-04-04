from simulator.collision import resolve_robot_ball_collision, resolve_robot_robot_collision

def update_game_state(robots, ball, dt):
    for robot in robots:
        # Garante que o robô não saia dos limites do campo
        robot.x = max(0, min(robot.x, 500 - robot.width))
        robot.y = max(50, min(robot.y, 400 - robot.height))

    # Atualiza a posição da bola
    ball.x += ball.velocity[0] * dt  # Substituído ball.vx por ball.velocity[0]
    ball.y += ball.velocity[1] * dt  # Substituído ball.vy por ball.velocity[1]

    # Garante que a bola não saia dos limites do campo
    ball.x = max(0, min(ball.x, 500))
    ball.y = max(50, min(ball.y, 400))