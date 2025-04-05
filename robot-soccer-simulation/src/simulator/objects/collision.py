from __future__ import annotations  # Permite usar strings para tipagem tardia
import numpy as np
from ui.interface_config import *
from typing import TYPE_CHECKING

# Importações para tipagem tardia, evitando problemas de importação circular
if TYPE_CHECKING:
    from simulator.objects.robot import Robot
    from simulator.objects.ball import Ball
    from simulator.objects.field import Field


### Classes dos objetos de colisão
class CollisionObject:
    """
    Classe base para objetos de colisão.
    """
    def __init__(self, type_object):
        '''
        Inicializa a classe de colisão.
        :param type: Tipo de objeto de colisão (ex: "circle", "rectangle", "line").
        '''
        self.type_object = type_object 

    def check_collision(self, other):
        """
        Método abstrato para verificar colisão.
        Deve ser implementado nas subclasses.
        """
        raise NotImplementedError("Este método deve ser implementado nas subclasses.")

class CollisionCircle(CollisionObject):
    """
    Representa um círculo para detecção de colisão.
    """
    def __init__(self, x, y, radius, type_object):
        """
        Inicializa um objeto de colisão circular.
        :param x: Coordenada X do centro do círculo.
        :param y: Coordenada Y do centro do círculo.
        :param radius: Raio do círculo.
        :param type: Tipo do objeto (MOVING ou STRUCTURES).
        """
        super().__init__(type_object)
        self.x = x
        self.y = y
        self.radius = radius

    def check_collision(self, other):
        """
        Verifica colisão com outro objeto.
        """
        if isinstance(other, CollisionCircle):
            # Colisão entre dois círculos
            distance = np.linalg.norm(np.array([self.x - other.x, self.y - other.y]))
            return distance < self.radius + other.radius
        elif isinstance(other, CollisionRectangle):
            # Colisão entre círculo e retângulo
            return other.check_collision(self)
        elif isinstance(other, CollisionLine):
            # Colisão entre círculo e linha
            return other.check_collision(self)
        return False

class CollisionRectangle(CollisionObject):
    """
    Representa um retângulo para detecção de colisão.
    """
    def __init__(self, x, y, width, height, type_object, angle=0):
        """
        Inicializa um objeto de colisão retangular.
        :param x: Coordenada X do centro do retângulo.
        :param y: Coordenada Y do centro do retângulo.
        :param width: Largura do retângulo.
        :param height: Altura do retângulo.
        :param type_object: Tipo do objeto (ex: "BALL", "ROBOT").
        :param angle: Ângulo de rotação do retângulo em graus.
        """
        super().__init__(type_object)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle  # Ângulo de rotação em graus

    def get_corners(self):
        """
        Calcula os quatro cantos do retângulo rotacionado.
        :return: Lista de coordenadas dos cantos [(x1, y1), (x2, y2), (x3, y3), (x4, y4)].
        """
        # Coordenadas dos cantos sem rotação (em relação ao centro)
        half_width = self.width / 2
        half_height = self.height / 2
        corners = [
            np.array([-half_width, -half_height]),
            np.array([half_width, -half_height]),
            np.array([half_width, half_height]),
            np.array([-half_width, half_height])
        ]

        # Matriz de rotação
        radians = np.radians(self.angle)
        rotation_matrix = np.array([
            [np.cos(radians), -np.sin(radians)],
            [np.sin(radians), np.cos(radians)]
        ])

        # Aplica a rotação e desloca para a posição do retângulo
        rotated_corners = [np.dot(rotation_matrix, corner) + np.array([self.x, self.y]) for corner in corners]
        return rotated_corners

    def check_collision(self, other):
        """
        Verifica colisão com outro objeto.
        """
        if isinstance(other, CollisionCircle):
            # Colisão entre retângulo rotacionado e círculo
            return self.check_collision_with_circle(other)
        elif isinstance(other, CollisionRectangle):
            # Colisão entre dois retângulos rotacionados
            return self.check_collision_with_rectangle(other)
        return False

    def check_collision_with_circle(self, circle):
        """
        Verifica colisão entre o retângulo rotacionado e um círculo.
        :param circle: Objeto CollisionCircle.
        :return: True se houver colisão, False caso contrário.
        """
        # Calcula os cantos do retângulo rotacionado
        corners = self.get_corners()

        # Projeta o círculo no retângulo rotacionado
        circle_center = np.array([circle.x, circle.y])
        closest_point = self.get_closest_point_on_rectangle(circle_center, corners)

        # Verifica a distância entre o círculo e o ponto mais próximo
        distance = np.linalg.norm(circle_center - closest_point)
        return distance <= circle.radius

    def get_closest_point_on_rectangle(self, point, corners):
        """
        Encontra o ponto mais próximo no retângulo rotacionado em relação a um ponto externo.
        :param point: Coordenadas do ponto externo (x, y).
        :param corners: Lista de cantos do retângulo rotacionado.
        :return: Coordenadas do ponto mais próximo no retângulo.
        """
        closest_point = None
        min_distance = float('inf')

        # Verifica cada aresta do retângulo
        for i in range(len(corners)):
            start = corners[i]
            end = corners[(i + 1) % len(corners)]
            edge_vector = end - start
            point_vector = point - start
            projection = np.dot(point_vector, edge_vector) / np.dot(edge_vector, edge_vector)
            projection = max(0, min(1, projection))  # Restringe a projeção ao segmento de linha
            closest = start + projection * edge_vector
            distance = np.linalg.norm(point - closest)
            if distance < min_distance:
                min_distance = distance
                closest_point = closest

        return closest_point

    def check_collision_with_rectangle(self, other):
        """
        Verifica colisão entre dois retângulos rotacionados usando o Separating Axis Theorem (SAT).
        :param other: Outro objeto CollisionRectangle.
        :return: True se houver colisão, False caso contrário.
        """
        # Calcula os cantos dos dois retângulos
        corners1 = self.get_corners()
        corners2 = other.get_corners()

        # Eixos de projeção: normais às arestas de ambos os retângulos
        axes = []
        for i in range(len(corners1)):
            edge = corners1[(i + 1) % len(corners1)] - corners1[i]
            axes.append(np.array([-edge[1], edge[0]]) / np.linalg.norm(edge))
        for i in range(len(corners2)):
            edge = corners2[(i + 1) % len(corners2)] - corners2[i]
            axes.append(np.array([-edge[1], edge[0]]) / np.linalg.norm(edge))

        # Projeta os cantos de ambos os retângulos em cada eixo
        for axis in axes:
            projection1 = [np.dot(corner, axis) for corner in corners1]
            projection2 = [np.dot(corner, axis) for corner in corners2]
            if max(projection1) < min(projection2) or max(projection2) < min(projection1):
                return False  # Não há sobreposição em um dos eixos

        return True  # Há sobreposição em todos os eixos

class CollisionLine(CollisionObject):
    """
    Representa uma linha para detecção de colisão.
    """
    def __init__(self, start, end, type_object):
        """
        Inicializa um objeto de colisão linear.
        :param start: Ponto inicial da linha (x, y).
        :param end: Ponto final da linha (x, y).
        :param type_object: Tipo do objeto (ex: "BALL", "ROBOT").
        """
        super().__init__(type_object)
        self.start = np.array(start)
        self.end = np.array(end)

    def check_collision(self, other):
        """
        Verifica colisão com outro objeto.
        """
        if isinstance(other, CollisionCircle):
            # Colisão entre linha e círculo
            line_vec = self.end - self.start
            point_vec = np.array([other.x, other.y]) - self.start
            line_len = np.linalg.norm(line_vec)
            line_unitvec = line_vec / line_len
            projection = np.dot(point_vec, line_unitvec)
            projection = max(0, min(line_len, projection))
            closest_point = self.start + projection * line_unitvec
            distance_to_circle = np.linalg.norm(closest_point - np.array([other.x, other.y]))
            return distance_to_circle <= other.radius
        return False

class CollisionPolyLine(CollisionObject):
    """
    Representa um conjunto de objetos de colisão (linhas, círculos, retângulos).
    """
    def __init__(self, objects):
        """
        Inicializa a classe com uma lista de objetos de colisão.
        :param objects: Lista de objetos de colisão (CollisionLine, CollisionCircle, CollisionRectangle).
        """
        self.objects = objects

    def check_collision(self, other):
        """
        Verifica colisão com outro objeto.
        :param other: Outro objeto de colisão.
        :return: True se houver colisão com qualquer objeto da lista, False caso contrário.
        """
        for obj in self.objects:
            if obj.check_collision(other):
                return True
        return False

class Collision:
    """
    Classe que gerencia as colisões no jogo.
    """
    def __init__(self, moving_objects, structures):
        """
        Inicializa a classe de colisão.
        :param moving_objects: Lista de objetos do tipo MOVING.
        :param structures: Lista de objetos do tipo STRUCTURES.
        """
        self.moving_objects = moving_objects
        self.structures = structures

    def handle_collisions(self):
        """
        Lida com todas as colisões no jogo.
        """
        # Colisões entre objetos MOVING
        for i, obj1 in enumerate(self.moving_objects):
            for obj2 in self.moving_objects[i + 1:]:
                if obj1.collision_object.check_collision(obj2.collision_object):
                    print(f"Colisão detectada entre {obj1.collision_object.type_object} e {obj2.collision_object.type_object}")
                    self.resolve_moving_collision(obj1, obj2)

        # Colisões entre MOVING e STRUCTURES
        for moving in self.moving_objects:
            for structure in self.structures:
                if moving.collision_object.check_collision(structure):
                    print(f"Colisão detectada entre {obj1.collision_object.type_object} e {obj2.collision_object.type_object}")
                    self.resolve_structure_collision(moving, structure)

    def resolve_moving_collision(self, obj1, obj2):
        """
        Resolve colisões entre objetos MOVING.
        """
        print(f"Colisão detectada entre {obj1.collision_object.type_object} e {obj2.collision_object.type_object}")

        if obj1.collision_object.type_object ==  BALL_OBJECT and obj2.collision_object.type_object == ROBOT_OBJECT:
            self.resolve_ball_robot_collision(obj1, obj2)
        elif obj1.collision_object.type_object == ROBOT_OBJECT and obj2.collision_object.type_object == BALL_OBJECT:
            self.resolve_ball_robot_collision(obj2, obj1)
        elif obj1.collision_object.type_object == ROBOT_OBJECT and obj2.collision_object.type_object == ROBOT_OBJECT:
            self.resolve_robot_robot_collision(obj1, obj2)

    # No método resolve_ball_robot_collision
    def resolve_ball_robot_collision(self, ball, robot):
        """
        Resolve a colisão entre a bola e um robô.
        """
        collision_vector = np.array([ball.x - robot.x, ball.y - robot.y])
        collision_vector = collision_vector / np.linalg.norm(collision_vector)
        
        # Ajusta a posição da bola e do robô
        relative_velocity = ball.velocity - robot.velocity
        
        # Calcula a sobreposição
        velocity_projection = np.dot(relative_velocity, collision_vector) * collision_vector
        
        # Ajusta a posição da bola
        ball.velocity -= 2 * COEFFICIENT_RESTITUTION_BALL_ROBOT * velocity_projection
        robot.velocity += 2* COEFFICIENT_RESTITUTION_BALL_ROBOT * velocity_projection

        if np.linalg.norm(ball.velocity) > 0:
            ball.direction = ball.velocity / np.linalg.norm(ball.velocity)

    def resolve_robot_robot_collision(self, robot1, robot2):
        """
        Resolve a colisão entre dois robôs.
        """
        print(f"Resolvendo colisão robô-robô: robô1 em ({robot1.x}, {robot1.y}), robô2 em ({robot2.x}, {robot2.y})")
        collision_vector = np.array([robot2.x - robot1.x, robot2.y - robot1.y])
        if np.linalg.norm(collision_vector) > 0:
            collision_vector = collision_vector / np.linalg.norm(collision_vector)
        else:
            collision_vector = np.array([1.0, 0.0])  # Define um vetor padrão se o vetor de colisão for nulo

        overlap = robot1.collision_object.width / 2 + robot2.collision_object.width / 2 - np.linalg.norm(collision_vector)
        if overlap > 0:
            robot1.x -= collision_vector[0] * overlap / 2
            robot1.y -= collision_vector[1] * overlap / 2
            robot2.x += collision_vector[0] * overlap / 2
            robot2.y += collision_vector[1] * overlap / 2

            # Atualiza os objetos de colisão
            robot1.collision_object.x = robot1.x
            robot1.collision_object.y = robot1.y
            robot2.collision_object.x = robot2.x
            robot2.collision_object.y = robot2.y

            # Ajustar velocidades com base no coeficiente de restituição
            relative_velocity = np.array([robot2.velocity[0] - robot1.velocity[0], robot2.velocity[1] - robot1.velocity[1]])
            velocity_projection = np.dot(relative_velocity, collision_vector) * collision_vector
            robot1.velocity += COEFFICIENT_RESTITUTION_ROBOT_ROBOT * velocity_projection
            robot2.velocity -= COEFFICIENT_RESTITUTION_ROBOT_ROBOT * velocity_projection

    def resolve_structure_collision(self, moving, structure):
        """
        Resolve colisões entre MOVING e STRUCTURES.
        """
        if moving.collision_object.type_object == BALL_OBJECT and structure.collision_object.type_object == FIELD_OBJECT:
            moving.velocity *= -COEFFICIENT_RESTITUTION_BALL_FIELD
        elif moving.collision_object.type_object == ROBOT_OBJECT and structure.collision_object.type_object == FIELD_OBJECT:
            moving.x -= moving.speed * np.cos(np.radians(moving.direction))
            moving.y -= moving.speed * np.sin(np.radians(moving.direction))
        else:
            structure.in_collision = True