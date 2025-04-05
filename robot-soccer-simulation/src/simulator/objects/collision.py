from __future__ import annotations  # Permite usar strings para tipagem tardia
import numpy as np
from typing import TYPE_CHECKING
from ui.interface_config import *

# Importações para tipagem tardia, evitando problemas de importação circular
if TYPE_CHECKING:
    from simulator.objects.robot import Robot
    from simulator.objects.ball import Ball
    from simulator.objects.field import Field

# Constantes de coeficientes de restituição
COEFFICIENT_RESTITUTION_BALL_ROBOT = 1.0
COEFFICIENT_RESTITUTION_ROBOT_ROBOT = 0.2
COEFFICIENT_RESTITUTION_BALL_FIELD = 0.6
COEFFICIENT_FRICTION_ROBOT_ROBOT = 0.9  # Coeficiente de atrito


### Classes dos objetos de colisão
class CollisionObject:
    """
    Classe base para objetos de colisão.
    """
    def __init__(self, type_object):
        """
        Inicializa a classe de colisão.
        :param type_object: Tipo de objeto de colisão (ex: "circle", "rectangle", "line").
        """
        self.type_object = type_object

    def check_collision(self, other):
        """
        Método abstrato para verificar colisão.
        Deve ser implementado nas subclasses.
        """
        raise NotImplementedError("Este método deve ser implementado nas subclasses.")

    def rotate(self, angle):
        """
        Método abstrato para rotacionar o objeto.
        Deve ser implementado nas subclasses.
        """
        raise NotImplementedError("Este método deve ser implementado nas subclasses.")


class CollisionPoint(CollisionObject):
    """
    Representa um ponto para detecção de colisão.
    """
    def __init__(self, x, y, type_object):
        super().__init__(type_object)
        self.x = x
        self.y = y

    def check_collision(self, other):
        """
        Verifica colisão com outro objeto.
        """
        if isinstance(other, CollisionPoint):
            return self.x == other.x and self.y == other.y
        elif isinstance(other, CollisionCircle):
            distance = np.linalg.norm(np.array([self.x - other.x, self.y - other.y]))
            return distance <= other.radius
        elif isinstance(other, CollisionRectangle):
            return other.check_point_inside(self)
        return False

    def rotate(self, angle, center):
        """
        Rotaciona o ponto em torno de um centro.
        """
        radians = np.radians(angle)
        translated_x = self.x - center[0]
        translated_y = self.y - center[1]
        rotated_x = translated_x * np.cos(radians) - translated_y * np.sin(radians)
        rotated_y = translated_x * np.sin(radians) + translated_y * np.cos(radians)
        self.x = rotated_x + center[0]
        self.y = rotated_y + center[1]


class CollisionCircle(CollisionObject):
    """
    Representa um círculo para detecção de colisão.
    """
    def __init__(self, x, y, radius, type_object):
        super().__init__(type_object)
        self.x = x
        self.y = y
        self.radius = radius

    def check_collision(self, other):
        """
        Verifica colisão com outro objeto.
        """
        if isinstance(other, CollisionCircle):
            distance = np.linalg.norm(np.array([self.x - other.x, self.y - other.y]))
            return distance <= self.radius + other.radius
        elif isinstance(other, CollisionPoint):
            return other.check_collision(self)
        elif isinstance(other, CollisionRectangle):
            return other.check_collision_with_circle(self)
        return False


class CollisionLine(CollisionObject):
    """
    Representa uma linha para detecção de colisão.
    """
    def __init__(self, start, end):
        super().__init__("LINE")
        self.start = np.array(start)
        self.end = np.array(end)

    def check_collision(self, other):
        """
        Verifica colisão com outro objeto.
        """
        if isinstance(other, CollisionPoint):
            return self.check_point_collision(other)
        elif isinstance(other, CollisionCircle):
            return self.check_collision_with_circle(other)
        return False

    def check_point_collision(self, point):
        """
        Verifica colisão com um ponto.
        """
        line_vec = self.end - self.start
        point_vec = np.array([point.x, point.y]) - self.start
        projection = np.dot(point_vec, line_vec) / np.dot(line_vec, line_vec)
        projection = max(0, min(1, projection))
        closest_point = self.start + projection * line_vec
        return np.allclose(closest_point, [point.x, point.y])

    def check_collision_with_circle(self, circle):
        """
        Verifica colisão com um círculo.
        """
        line_vec = self.end - self.start
        point_vec = np.array([circle.x, circle.y]) - self.start
        projection = np.dot(point_vec, line_vec) / np.dot(line_vec, line_vec)
        projection = max(0, min(1, projection))
        closest_point = self.start + projection * line_vec
        distance = np.linalg.norm(np.array([circle.x, circle.y]) - closest_point)
        return distance <= circle.radius

    def rotate(self, angle, center):
        """
        Rotaciona a linha em torno de um centro.
        """
        start_point = CollisionPoint(self.start[0], self.start[1], "POINT")
        end_point = CollisionPoint(self.end[0], self.end[1], "POINT")
        start_point.rotate(angle, center)
        end_point.rotate(angle, center)
        self.start = np.array([start_point.x, start_point.y])
        self.end = np.array([end_point.x, end_point.y])


class CollisionRectangle(CollisionObject):
    """
    Representa um retângulo para detecção de colisão.
    """
    def __init__(self, x, y, width, height, type_object, angle=0):
        super().__init__(type_object)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle
        self.update_corners()

    def update_corners(self):
        """
        Atualiza os cantos do retângulo com base na posição e rotação.
        """
        self.corners = self.get_corners()

    def get_corners(self):
        """
        Calcula os cantos do retângulo.
        """
        half_width = self.width / 2
        half_height = self.height / 2
        corners = [
            np.array([-half_width, -half_height]),
            np.array([half_width, -half_height]),
            np.array([half_width, half_height]),
            np.array([-half_width, half_height])
        ]
        radians = np.radians(self.angle)
        rotation_matrix = np.array([
            [np.cos(radians), -np.sin(radians)],
            [np.sin(radians), np.cos(radians)]
        ])
        return [np.dot(rotation_matrix, corner) + np.array([self.x, self.y]) for corner in corners]

    def check_collision(self, other):
        """
        Verifica colisão com outro objeto.
        """
        if isinstance(other, CollisionPoint):
            return self.check_point_inside(other)
        elif isinstance(other, CollisionCircle):
            return self.check_collision_with_circle(other)
        elif isinstance(other, CollisionRectangle):
            return self.check_collision_with_rectangle(other)
        return False

    def check_point_inside(self, point):
        """
        Verifica se um ponto está dentro do retângulo.
        """
        local_point = np.array([point.x, point.y]) - np.array([self.x, self.y])
        for i in range(len(self.corners)):
            edge = self.corners[(i + 1) % len(self.corners)] - self.corners[i]
            normal = np.array([-edge[1], edge[0]])
            projection = np.dot(local_point, normal)
            if projection > 0:
                return False
        return True

    def check_collision_with_circle(self, circle):
        """
        Verifica colisão entre o retângulo (rotacionado) e um círculo.
        :param circle: Objeto CollisionCircle.
        :return: True se houver colisão, False caso contrário.
        """
        circle_center = np.array([circle.x, circle.y])
        corners = self.get_corners()

        # Verifica se o centro do círculo está dentro do retângulo
        if self.check_point_inside(circle):
            return True

        # Verifica colisão com as arestas do retângulo
        for i in range(len(corners)):
            start = corners[i]
            end = corners[(i + 1) % len(corners)]  # Próximo canto (fechando o retângulo)
            edge_vector = end - start
            point_vector = circle_center - start

            # Projeção do ponto no segmento de linha
            projection = np.dot(point_vector, edge_vector) / np.dot(edge_vector, edge_vector)
            projection = max(0, min(1, projection))  # Restringe a projeção ao segmento de linha

            # Calcula o ponto mais próximo na aresta
            closest = start + projection * edge_vector

            # Calcula a distância entre o centro do círculo e o ponto mais próximo
            distance = np.linalg.norm(circle_center - closest)

            # Verifica se a distância é menor ou igual ao raio do círculo
            if distance <= circle.radius:
                return True

        return False

    def get_closest_point_on_rectangle(self, point, corners):
        """
        Obtém o ponto mais próximo no retângulo em relação a um ponto externo.
        """
        closest_point = None
        min_distance = float('inf')
        for i in range(len(corners)):
            start = corners[i]
            end = corners[(i + 1) % len(corners)]
            edge_vector = end - start
            point_vector = point - start
            projection = np.dot(point_vector, edge_vector) / np.dot(edge_vector, edge_vector)
            projection = max(0, min(1, projection))
            closest = start + projection * edge_vector
            distance = np.linalg.norm(point - closest)
            if distance < min_distance:
                min_distance = distance
                closest_point = closest
        return closest_point

    def check_collision_with_rectangle(self, other):
        """
        Verifica colisão com outro retângulo.
        """
        corners1 = self.get_corners()
        corners2 = other.get_corners()
        axes = []
        for i in range(len(corners1)):
            edge = corners1[(i + 1) % len(corners1)] - corners1[i]
            axes.append(np.array([-edge[1], edge[0]]) / np.linalg.norm(edge))
        for i in range(len(corners2)):
            edge = corners2[(i + 1) % len(corners2)] - corners2[i]
            axes.append(np.array([-edge[1], edge[0]]) / np.linalg.norm(edge))
        for axis in axes:
            projection1 = [np.dot(corner, axis) for corner in corners1]
            projection2 = [np.dot(corner, axis) for corner in corners2]
            if max(projection1) < min(projection2) or max(projection2) < min(projection1):
                return False
        return True

    def rotate(self, angle):
        """
        Rotaciona o retângulo.
        """
        self.angle += angle
        self.update_corners()


class CollisionPolyLine(CollisionObject):
    """
    Representa um objeto de colisão composto por múltiplos objetos de colisão.
    Os objetos internos são tratados como um único grupo coeso.
    """
    def __init__(self, objects, type_object):
        """
        Inicializa um CollisionPolyLine com uma lista de objetos de colisão.
        :param objects: Lista de objetos de colisão (CollisionPoint, CollisionLine, etc.).
        :param type_object: Tipo do objeto (ex: "MOVING", "STRUCTURE").
        """
        super().__init__(type_object)
        self.objects = objects  # Lista de objetos de colisão
        self.points = self._extract_points()  # Pontos extraídos dos objetos internos

    def _extract_points(self):
        """
        Extrai os pontos de todos os objetos internos, mantendo o formato original.
        :return: Lista de pontos [(x1, y1), (x2, y2), ...].
        """
        points = []
        for obj in self.objects:
            if isinstance(obj, CollisionPoint):
                points.append((obj.x, obj.y))
            elif isinstance(obj, CollisionCircle):
                # Adiciona o centro do círculo como ponto
                points.append((obj.x, obj.y))
            elif isinstance(obj, CollisionRectangle):
                # Adiciona os cantos do retângulo
                points.extend(obj.get_corners())
            elif isinstance(obj, CollisionLine):
                # Adiciona os pontos inicial e final da linha
                points.append(tuple(obj.start))
                points.append(tuple(obj.end))
            elif isinstance(obj, CollisionPolyLine):
                # Adiciona os pontos do PolyLine interno
                points.extend(obj._extract_points())
        return points

    def check_collision(self, other):
        """
        Verifica colisão com outro objeto externo.
        :param other: Outro objeto de colisão.
        :return: True se houver colisão, False caso contrário.
        """
        for obj in self.objects:
            if obj.check_collision(other):
                return True
        return False

    def rotate(self, angle, center):
        """
        Rotaciona todos os objetos internos em torno de um centro.
        :param angle: Ângulo de rotação em graus.
        :param center: Centro de rotação (x, y).
        """
        for obj in self.objects:
            obj.rotate(angle, center)
        self.points = self._extract_points()  # Atualiza os pontos após a rotação

    def get_bounding_box(self):
        """
        Calcula a caixa delimitadora (bounding box) do PolyLine.
        :return: (min_x, min_y, max_x, max_y)
        """
        x_coords = [point[0] for point in self.points]
        y_coords = [point[1] for point in self.points]
        return min(x_coords), min(y_coords), max(x_coords), max(y_coords)


class Collision:
    """
    Classe que gerencia as colisões no jogo.
    """
    def __init__(self, moving_objects, structures):
        self.moving_objects = moving_objects
        self.structures = structures

    def handle_collisions(self):
        """
        Gerencia as colisões entre objetos móveis e estruturas.
        Prioriza colisões com maior sobreposição.
        """
        collisions = []

        # Detecta colisões entre objetos móveis
        for i, obj1 in enumerate(self.moving_objects):
            for obj2 in self.moving_objects[i + 1:]:
                if obj1.collision_object.check_collision(obj2.collision_object):
                    overlap = self.calculate_overlap(obj1, obj2)
                    collisions.append((overlap, obj1, obj2))

        # Ordena as colisões por sobreposição (maior primeiro)
        collisions.sort(reverse=True, key=lambda x: x[0])

        # Resolve as colisões na ordem de prioridade
        for _, obj1, obj2 in collisions:
            self.resolve_moving_collision(obj1, obj2)

    def calculate_overlap(self, obj1, obj2):
        """
        Calcula a sobreposição entre dois objetos de colisão.
        """
        collision_vector = np.array([obj2.x - obj1.x, obj2.y - obj1.y])
        distance = np.linalg.norm(collision_vector)

        if distance == 0:
            return float('inf')  # Máxima sobreposição

        # Verifica os tipos de objetos de colisão
        if isinstance(obj1.collision_object, CollisionCircle) and isinstance(obj2.collision_object, CollisionCircle):
            # Ambos são círculos
            return obj1.collision_object.radius + obj2.collision_object.radius - distance
        elif isinstance(obj1.collision_object, CollisionRectangle) and isinstance(obj2.collision_object, CollisionRectangle):
            # Ambos são retângulos (simplificação para tratar como círculos de mesmo diâmetro)
            return obj1.collision_object.width / 2 + obj2.collision_object.width / 2 - distance
        elif isinstance(obj1.collision_object, CollisionCircle) and isinstance(obj2.collision_object, CollisionRectangle):
            # Um é círculo e o outro é retângulo
            return obj1.collision_object.radius + obj2.collision_object.width / 2 - distance
        elif isinstance(obj1.collision_object, CollisionRectangle) and isinstance(obj2.collision_object, CollisionCircle):
            # Um é retângulo e o outro é círculo
            return obj1.collision_object.width / 2 + obj2.collision_object.radius - distance

        return 0  # Caso não seja possível calcular a sobreposição

    def resolve_moving_collision(self, obj1, obj2):
        """
        Resolve colisões entre objetos móveis.
        """
        if obj1.collision_object.type_object == BALL_OBJECT and obj2.collision_object.type_object == ROBOT_OBJECT:
            self.resolve_ball_robot_collision(obj1, obj2)
        elif obj1.collision_object.type_object == ROBOT_OBJECT and obj2.collision_object.type_object == BALL_OBJECT:
            self.resolve_ball_robot_collision(obj2, obj1)
        elif obj1.collision_object.type_object == ROBOT_OBJECT and obj2.collision_object.type_object == ROBOT_OBJECT:
            self.resolve_robot_robot_collision(obj1, obj2)



    def resolve_ball_robot_collision(self, ball, robot):
        """
        Resolve a colisão entre a bola e o robô.
        """
        collision_vector = np.array([ball.x - robot.x, ball.y - robot.y])
        distance = np.linalg.norm(collision_vector)

        if distance == 0:
            # Evita divisão por zero
            collision_vector = np.array([1.0, 0.0])
        else:
            collision_vector /= distance

        # Calcula a velocidade relativa
        relative_velocity = ball.velocity - robot.velocity
        velocity_projection = np.dot(relative_velocity, collision_vector) * collision_vector

        # Atualiza as velocidades da bola e do robô
        ball.velocity -= 2 * COEFFICIENT_RESTITUTION_BALL_ROBOT * velocity_projection
        robot.velocity += 2 * COEFFICIENT_RESTITUTION_BALL_ROBOT * velocity_projection

    def resolve_robot_robot_collision(self, robot1, robot2):
        """
        Resolve colisões entre dois robôs, reposicionando-os apenas o suficiente para evitar sobreposição.
        """
        collision_vector = np.array([robot2.x - robot1.x, robot2.y - robot1.y])
        distance = np.linalg.norm(collision_vector)

        if distance == 0:
            # Evita divisão por zero
            collision_vector = np.array([1.0, 0.0])
            distance = 1.0
        else:
            collision_vector /= distance

        # Calcula a sobreposição entre os robôs
        overlap = robot1.collision_object.width / 2 + robot2.collision_object.width / 2 - distance
        if overlap > 0:
            # Reposiciona os robôs apenas o suficiente para evitar sobreposição
            correction = overlap / 2
            robot1.x -= collision_vector[0] * correction
            robot1.y -= collision_vector[1] * correction
            robot2.x += collision_vector[0] * correction
            robot2.y += collision_vector[1] * correction

            # Atualiza os objetos de colisão dos robôs
            robot1.collision_object.x = robot1.x
            robot1.collision_object.y = robot1.y
            robot2.collision_object.x = robot2.x
            robot2.collision_object.y = robot2.y

        # Calcula a velocidade relativa entre os robôs
        relative_velocity = robot2.velocity - robot1.velocity
        velocity_projection = np.dot(relative_velocity, collision_vector) * collision_vector

        # Troca a quantidade de movimento vetorial (momentum) entre os robôs
        robot1.velocity += COEFFICIENT_RESTITUTION_ROBOT_ROBOT * velocity_projection
        robot2.velocity -= COEFFICIENT_RESTITUTION_ROBOT_ROBOT * velocity_projection

        # Aplica atrito para estabilizar os robôs
        robot1.velocity *= COEFFICIENT_FRICTION_ROBOT_ROBOT
        robot2.velocity *= COEFFICIENT_FRICTION_ROBOT_ROBOT

        # Limita a velocidade dos robôs
        max_speed = 100  # Velocidade máxima permitida
        robot1.velocity = np.clip(robot1.velocity, -max_speed, max_speed)
        robot2.velocity = np.clip(robot2.velocity, -max_speed, max_speed)
            
    def resolve_structure_collision(self, moving, structure):
        """
        Resolve colisões entre objetos MOVING (ex: bola, robô) e STRUCTURES (ex: campo, paredes).
        :param moving: Objeto móvel (ex: bola ou robô).
        :param structure: Objeto estático (ex: campo ou parede).
        """
        if moving.collision_object.type_object == BALL_OBJECT and structure.collision_object.type_object == FIELD_OBJECT:
            # A bola colide com o campo: inverte a velocidade com um coeficiente de restituição
            moving.velocity *= -COEFFICIENT_RESTITUTION_BALL_FIELD

        elif moving.collision_object.type_object == ROBOT_OBJECT and structure.collision_object.type_object == FIELD_OBJECT:
            # O robô colide com o campo: ajusta a posição para evitar sobreposição
            moving.x -= moving.speed * np.cos(np.radians(moving.direction))
            moving.y -= moving.speed * np.sin(np.radians(moving.direction))

            # Atualiza a posição do objeto de colisão do robô
            moving.collision_object.x = moving.x
            moving.collision_object.y = moving.y

        else:
            # Caso genérico: marca a estrutura como em colisão
            structure.in_collision = True