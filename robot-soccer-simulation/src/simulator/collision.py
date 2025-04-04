import math
import pygame

def check_collision(robot, ball):
    """
    Verifica se houve colisão entre um robô e a bola.
    :param robot: Objeto da classe Robot.
    :param ball: Objeto da classe Ball.
    :return: True se houve colisão, False caso contrário.
    """
    distance = math.sqrt((robot.x - ball.x) ** 2 + (robot.y - ball.y) ** 2)
    return distance < (robot.width / 2) + ball.radius

def resolve_robot_ball_collision(robot, ball):
    """
    Resolve a colisão entre um robô e a bola, ajustando a velocidade da bola.
    :param robot: Objeto da classe Robot.
    :param ball: Objeto da classe Ball.
    """
    if check_collision(robot, ball):
        # Calcula o vetor de colisão
        dx = ball.x - robot.x
        dy = ball.y - robot.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Normaliza o vetor de colisão
        nx = dx / distance
        ny = dy / distance

        # Reflete a velocidade da bola no vetor normal
        dot_product = ball.velocity[0] * nx + ball.velocity[1] * ny
        ball.velocity[0] -= 2 * dot_product * nx
        ball.velocity[1] -= 2 * dot_product * ny

        # Move a bola ligeiramente para fora do robô para evitar sobreposição
        overlap = (robot.width / 2 + ball.radius) - distance
        ball.x += nx * overlap
        ball.y += ny * overlap

def check_robot_collision(robot1, robot2):
    """
    Verifica se houve colisão entre dois robôs.
    :param robot1: Objeto da classe Robot.
    :param robot2: Objeto da classe Robot.
    :return: True se houve colisão, False caso contrário.
    """
    rect1 = pygame.Rect(
        robot1.x - robot1.width / 2, robot1.y - robot1.height / 2, robot1.width, robot1.height
    )
    rect2 = pygame.Rect(
        robot2.x - robot2.width / 2, robot2.y - robot2.height / 2, robot2.width, robot2.height
    )
    return rect1.colliderect(rect2)

def resolve_robot_robot_collision(robot1, robot2):
    """
    Resolve a colisão entre dois robôs, ajustando suas posições.
    :param robot1: Objeto da classe Robot.
    :param robot2: Objeto da classe Robot.
    """
    if check_robot_collision(robot1, robot2):
        # Calcula o vetor de colisão
        dx = robot2.x - robot1.x
        dy = robot2.y - robot1.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance == 0:
            # Evita divisão por zero
            return

        # Normaliza o vetor de colisão
        nx = dx / distance
        ny = dy / distance

        # Move os robôs ligeiramente para fora um do outro
        overlap = (robot1.width / 2 + robot2.width / 2) - distance
        robot1.x -= nx * overlap / 2
        robot1.y -= ny * overlap / 2
        robot2.x += nx * overlap / 2
        robot2.y += ny * overlap / 2