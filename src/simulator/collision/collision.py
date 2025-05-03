from __future__ import annotations  # Permite usar strings para tipagem tardia
import numpy as np
from typing import TYPE_CHECKING
from ui.interface_config import *
from collections import defaultdict
from utils.helpers import normalize
from shapely.geometry import Polygon, LineString, Point
import math
import pygame 


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
    def __init__(self, x, y, type_object, reference=None):
        super().__init__(type_object)
        self.x = x
        self.y = y
        self.position = np.array([x, y])  # Posição do ponto
        self.velocity = np.array([0.0, 0.0])  # Velocidade do ponto (vx, vy)

        #pai desse objeto de colisão
        self.reference = reference

    def check_collision(self, other):
        """
        Verifica colisão com outro objeto.

        return:
            - [True, mtv]: Se teve colisão
            - [False, None]: Se não teve colisão
        """
        if isinstance(other, CollisionPoint):
            if self.x == other.x and self.y == other.y:
                return [True, np.array([0.0,0.0])]
            return [False, None]
        
        elif isinstance(other, CollisionCircle):
            to_center = np.array([self.x - other.x, self.y - other.y])
            distance = np.linalg.norm(to_center)
            if distance <= other.radius:
                #MTV aponta para fora do círculo
                if distance == 0:
                    mtv_direction = np.array([1.0,0.0])
                else:
                    mtv_direction = to_center / distance 
                mtv = mtv_direction *(other.radius - distance)
                return [True, mtv]
            return [False, None]
        
        elif isinstance(other, CollisionRectangle):
            return other.check_point_inside(self)
        
        elif isinstance(other, CollisionGroup):
            return other.check_collision(self)
        
        return [False, None]

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
    def __init__(self, x, y, radius, type_object, reference=None):
        super().__init__(type_object)
        self.x = x
        self.y = y

        self.radius = radius
        self.center = np.array([self.x, self.y])

        print(f"[DEBUG]Círculo criado com x = {self.x}, y={self.y} e raio radius={self.radius}")
        #pai desse objeto de colisão
        self.reference = reference

    def check_collision(self, other):
        """
        Verifica colisão com outro objeto.
        """
        if isinstance(other, CollisionCircle):
            #retorna um vetor que vai do other -> self
            return self.check_collision_with_circle(other)
        elif isinstance(other, CollisionPoint):
            # Retorna um vetor que vai do other -> self
            collided, mtv = other.check_collision(self)
            if collided:
                return [True, -mtv]
            else:
                return [False, None]
        elif isinstance(other, CollisionLine):
            # Retorna um vetor que vai do other -> self
            collided, mtv = other.check_collision_with_circle(self)
            if collided:
                return [True, -mtv]
            else:
                return [False, None]
        elif isinstance(other, CollisionRectangle):
            collided, mtv = other.check_collision_with_circle(self)
            if collided:
                return [True, -mtv]
            else:
                return [False, None]
        elif isinstance(other, CollisionGroup):
            collided, mtv = other.check_collision(self)
            if collided:
                return [True, -mtv]
            else:
                return [False, None]
        return [False, None]
    
    def get_center(self):
        '''
            Retorna o centro da circunferência
        '''
        return self.center 
    
    def check_collision_with_circle(self, other:CollisionCircle):
        '''
        Verifica colisão entre dois círculos pelo SAT e retorna

        retorno:
            - [True, mtv] Se ocorreu uma colisão
            - [False, None] Se não ocorreu uma colisão
        '''
        # O MTV vai de other para self.
        #Puxando os centros dos círculos
        center_a = self.get_center()
        center_b = other.get_center()

        #Eixo variação dos círculos.
        delta = center_b - center_a
        distance = np.linalg.norm(delta)
        radius_sum = self.radius + other.radius 

        if distance <= radius_sum:
            #Se os centros coincidem, define um MTV padrão.
            if distance == 0:
                mtv_direction = np.array([1.0,0.0])
            else:
                mtv_direction = -delta/distance 
            overlap = radius_sum - distance 
            mtv = mtv_direction *overlap 
            return [True, mtv]
        
        return [False, None ]

    def rotate(self, angle, center):
        """
        Rotaciona o círculo em torno de um centro.
        
        :param angle: Ângulo de rotação em graus (sentido anti-horário).
        :param center: Centro de rotação (tupla com coordenadas x, y).
        """

        # Converte o ângulo para radianos, pois as funções trigonométricas do NumPy usam radianos
        radians = np.radians(angle)

        # Translada o círculo para a origem com base no centro de rotação
        translated_x = self.x - center[0]
        translated_y = self.y - center[1]

        # Aplica a rotação usando a matriz de rotação 2D:
        # [ cos(θ) -sin(θ) ]
        # [ sin(θ)  cos(θ) ]
        rotated_x = translated_x * np.cos(radians) - translated_y * np.sin(radians)
        rotated_y = translated_x * np.sin(radians) + translated_y * np.cos(radians)

        # Translada de volta para a posição original em relação ao centro
        self.x = rotated_x + center[0]
        self.y = rotated_y + center[1]


class CollisionLine(CollisionObject):
    """
    Representa uma linha para detecção de colisão.
    """
    def __init__(self, start, end, type_object = LINE_OBJECT,reference= None):
        super().__init__(type_object=type_object)
        self.start = np.array(start)
        self.end = np.array(end)
        self.direction = self.end - self.start 
        self.length = np.linalg.norm(self.direction)
        self.normalized_dir = self.direction / self.length if self.length != 0 else np.array([0, 0])

        #Calculando centro da linha.
        self.center = (self.start + self.end) / 2
        self.x = self.center[0]
        self.y = self.center[1]

        print(f"[DEBUG] Linha criada com inicio {self.start} e fim {self.end}, posição do centro {self.center} e tamanho {self.length}")

        #pai desse objeto de colisão
        self.reference = reference

    def check_collision(self, other):
        """
        Verifica colisão com outro objeto.
        """
        if isinstance(other, CollisionPoint):
            return self.check_collision_with_point(other)
        elif isinstance(other, CollisionCircle):
            return self.check_collision_with_circle(other)
        elif isinstance(other, CollisionLine):
            return self.check_collision_with_line(other)
        elif isinstance(other, CollisionRectangle):
            return self.check_collision_with_rectangles(other)
        elif isinstance(other, CollisionGroup):
            return other.check_collision(self)
        return [False, None]

    def closest_point_to(self, point):
        '''
        Retorna o ponto mais próximo na linha ao ponto fornecdio
        '''
        line_vec = self.direction 
        point_vec = np.array(point) - self.start
        t=np.dot(point_vec,line_vec) / np.dot(line_vec,line_vec)
        t = max(0, min(1,t))

        return self.start +t*line_vec
    

    def check_collision_with_point(self, point):
        """
        Verifica se tem uma colisão com um ponto.
        """
        closest = self.closest_point_to(point)
        distance = np.linalg.norm(np.array(point)-closest)
        if distance == 0:
            return [True, np.array([0.0,0.0])]
        else:
            return [False, None]


    def check_collision_with_circle(self, circle:CollisionCircle):
        """
        Verifica colisão com um círculo.

        retorna:
            - [True, mtv]: se teve colisão
            - [False, [0.0,0.0]]: Se não teve colisão
        """
        center = np.array([circle.x, circle.y])
        closest = self.closest_point_to(center)
        dist_vec = np.array(center-closest)
        distance = np.linalg.norm(dist_vec)

        if distance <= circle.radius:
            if distance==0:
                # Centro do círculo está exatamente sobre a linha
                mtv = np.array([0.0,0.0])
            else:
                mtv = (dist_vec/distance) * (circle.radius-distance)
            
            return [True, mtv]
        return [False, None]

    def check_collision_with_rectangles(self, rectangle: CollisionRectangle):
        """
        Verifica colisão com um retângulo rotacionado.
        Combina interseção direta com SAT.

        retorna:
            - [True, mtv]: se teve colisão
            - [False, [0.0,0.0]]: Se não teve colisão
        """
        rect_corners = rectangle.get_corners()
        line_points = [self.start, self.end]

        # --- 1. Teste de interseção direta com os lados do retângulo ---
        for i in range(4):
            p1 = rect_corners[i]
            p2 = rect_corners[(i + 1) % 4]
            intersect, _ = self.line_segment_intersection(self.start, self.end, p1, p2)
            if intersect:
                # Colidiu — ainda calculamos o MTV usando SAT abaixo
                break
        else:
            # Nenhum lado foi cruzado — pode ser que a linha esteja dentro sem interseção
            # Nesse caso, só SAT pode detectar
            pass  # Continuamos para SAT

        # --- 2. SAT (Separating Axis Theorem) ---
        axes = []

        # Normais dos lados do retângulo
        for i in range(len(rect_corners)):
            edge = rect_corners[(i + 1) % len(rect_corners)] - rect_corners[i]
            normal = np.array([-edge[1], edge[0]])
            normal = normal / np.linalg.norm(normal)
            axes.append(normal)

        # Normal da linha
        line_edge = self.end - self.start
        if np.linalg.norm(line_edge) != 0:
            line_normal = np.array([-line_edge[1], line_edge[0]])
            line_normal = line_normal / np.linalg.norm(line_normal)
            axes.append(line_normal)

        mtv = None
        min_overlap = float('inf')

        for axis in axes:
            projections_rect = [np.dot(corner, axis) for corner in rect_corners]
            min_rect = min(projections_rect)
            max_rect = max(projections_rect)

            projections_line = [np.dot(point, axis) for point in line_points]
            min_line = min(projections_line)
            max_line = max(projections_line)

            if max_rect < min_line or max_line < min_rect:
                return [False, None]  # Separação encontrada

            overlap = min(max_rect, max_line) - max(min_rect, min_line)
            if overlap < min_overlap:
                min_overlap = overlap
                direction = rectangle.get_center() -((self.start+self.end)/2)
                mtv = axis if np.dot(direction, axis) > 0 else -axis

        return [True, mtv * min_overlap]


    def line_segment_intersection(self, p1, p2, q1, q2):
        """
        Verifica se dois segmentos de linha (p1-p2 e q1-q2) se cruzam.
        Retorna (True, ponto_interseção) se colidem.
        """
        def perp(v):
            return np.array([-v[1], v[0]])

        r = p2 - p1
        s = q2 - q1
        denominator = np.cross(r, s)

        if denominator == 0:
            return (False, None)  # Paralelas

        t = np.cross((q1 - p1), s) / denominator
        u = np.cross((q1 - p1), r) / denominator

        if 0 <= t <= 1 and 0 <= u <= 1:
            intersection = p1 + t * r
            return (True, intersection)

        return (False, None)
    
    def check_collision_with_line(self, other_line:CollisionLine):
        """
        Verifica colisão com outra linha.
        """
        intersects, point = self.line_segment_intersection(self.start, self.end, other_line.start, other_line.end)
        if intersects:
            mtv = np.array([0.0, 0.0])  # Sem profundidade definida para linhas finas
            return [True, mtv]
        return [False, None]
        
        
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
    def __init__(self, x, y, width, height, type_object, angle=0, reference = None):
        super().__init__(type_object)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle
        self.corners = []
        self.update_corners()

        
        print(f"[DEBUG] Retângulo criado com x = {self.x}, y={self.y} e width = {self.width} height={self.height}")

        #Pai dessa classe de colisão.
        self.reference = reference 

    def update_corners(self):
        """
        Atualiza os cantos do retângulo com base na posição e rotação.
        """
        self.corners = self.get_corners()
        '''for i, corner in enumerate(self.get_corners()):
            print(f"Canto {i}: {corner}")
        '''

    def get_edges(self):
        corners = self.get_corners()
        return [(corners[i], corners[(i + 1) % 4]) for i in range(4)]


    def get_center(self):
        '''
            Retorna o centro do retângulo na forma [x,y]
        '''
        return [self.x, self.y]
    
    def get_corners(self):
        """
        Calcula os cantos (vértices) do retângulo considerando sua posição, dimensão e rotação.
        
        Retorna:
            Uma lista de vetores (np.array) representando os 4 cantos do retângulo no espaço global.
        """

        # Calcula metade da largura e altura para facilitar o posicionamento em torno do centro (self.x, self.y)
        half_width = self.width / 2
        half_height = self.height / 2

        # Define os 4 cantos do retângulo no sistema local (sem rotação e centralizado na origem)
        corners = [
            np.array([-half_width, -half_height]),  # canto inferior esquerdo
            np.array([half_width, -half_height]),   # canto inferior direito
            np.array([half_width, half_height]),    # canto superior direito
            np.array([-half_width, half_height])    # canto superior esquerdo
        ]

        # Converte o ângulo de rotação de graus para radianos
        radians = np.radians(self.angle)

        # Cria a matriz de rotação 2D (sentido anti-horário)
        rotation_matrix = np.array([
            [np.cos(radians), -np.sin(radians)],
            [np.sin(radians),  np.cos(radians)]
        ])

        # Aplica a rotação e depois a translação (para a posição global [self.x, self.y])
        return [np.dot(rotation_matrix, corner) + np.array([self.x, self.y]) for corner in corners]
    
    #Posso enviar os corners diretamente para o retângulo
    def set_corners(self, corners):
        self.corners = corners 


    def check_collision(self, other):
        """
        Verifica colisão com outro objeto de qualquer tipo conhecido.
        
        Essa função atua como um despachante geral, chamando o método apropriado de verificação
        de colisão dependendo do tipo do objeto passado (other).

        Parâmetros:
            other: Objeto com o qual se deseja verificar colisão. Pode ser ponto, círculo,
                retângulo, linha ou polilinha.

        Retorna:
            True se houver colisão entre os objetos, False caso contrário.
        """

        # Caso o outro objeto seja um ponto, usa o método para verificar se ele está dentro do retângulo
        if isinstance(other, CollisionPoint):
            return self.check_point_inside(other)

        # Caso o outro objeto seja um círculo, chama o método de colisão com círculo
        elif isinstance(other, CollisionCircle):
            return self.check_collision_with_circle(other)

        # Caso o outro objeto seja outro retângulo, usa o Separating Axis Theorem (SAT)
        elif isinstance(other, CollisionRectangle):
            return self.check_collision_with_rectangle(other)

        # Caso o outro objeto seja uma linha, chama o método da linha para verificar colisão com o retângulo
        elif isinstance(other, CollisionLine):
            collided, mtv = other.check_collision_with_rectangles(self)
            if collided:
                return [True, -mtv]  # inverter para manter padrão: other → self
            return [False, None]

        # Caso o outro objeto seja uma polilinha, também delega a verificação para o objeto da polilinha
        elif isinstance(other, CollisionGroup):
            collided, mtv = other.check_collision(self)
            if collided:
                return [True, -mtv]
            else:
                return [False, None]

        # Se o tipo do objeto não for reconhecido, retorna False por padrão
        return [False, None]


    def check_point_inside(self, point):
        """
        Verifica se um ponto está dentro do retângulo, levando em conta rotação.
        Retorna:
            [True, mtv] se estiver dentro, onde mtv é o vetor mínimo de translação para empurrar o ponto para fora.
            [False, None] caso contrário.
        """
        # Vetor do ponto em relação ao centro
        rel = np.array([point.x, point.y]) - np.array([self.x, self.y])

        # Rotaciona o ponto de volta (rotação inversa ao retângulo)
        radians = np.radians(-self.angle)
        rotation_matrix = np.array([
            [np.cos(radians), np.sin(radians)],
            [-np.sin(radians),  np.cos(radians)]
        ])
        local_point = np.dot(rotation_matrix, rel)

        # Agora o retângulo é considerado como AABB no referencial local
        half_width = self.width / 2
        half_height = self.height / 2

        dx = half_width - abs(local_point[0])
        dy = half_height - abs(local_point[1])

        if dx >= 0 and dy >= 0:
            # Está dentro do retângulo
            if dx < dy:
                mtv_local = np.array([np.sign(local_point[0]) * dx, 0])
            else:
                mtv_local = np.array([0, np.sign(local_point[1]) * dy])

            # Rotaciona de volta o MTV para o espaço global
            # Como usamos rotação inversa antes, agora voltamos com a rotação original
            radians_back = np.radians(self.angle)
            rotation_matrix_back = np.array([
                [np.cos(radians_back), np.sin(radians_back)],
                [-np.sin(radians_back),  np.cos(radians_back)]
            ])
            mtv_global = np.dot(rotation_matrix_back, mtv_local)
            return [True, mtv_global]
        
        return [False, None]


    def check_collision_with_circle(self, circle):
        """
        Verifica colisão entre este retângulo (rotacionado) e um círculo.
        Retorna [True, mtv] ou [False, None].
        
        Melhorias implementadas:
        1. Tratamento mais robusto de casos extremos
        2. Cálculo mais preciso do MTV
        3. Melhor estabilidade numérica
        4. Suporte a colisões em alta velocidade
        5. Correção de edge cases
        """
        # 1. Obter dados básicos do círculo
        cx, cy = circle.x, circle.y
        radius = circle.radius
        
        # 2. Transformar o centro do círculo para o espaço local do retângulo
        dx = cx - self.x
        dy = cy - self.y
        angle_rad = -np.radians(self.angle)
        
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)
        local_x = cos_a * dx - sin_a * dy
        local_y = sin_a * dx + cos_a * dy
        
        # 3. Encontrar o ponto mais próximo no retângulo (em espaço local)
        half_w = self.width / 2
        half_h = self.height / 2
        
        # Clamp para dentro do retângulo
        closest_x = max(-half_w, min(local_x, half_w))
        closest_y = max(-half_h, min(local_y, half_h))
        
        # 4. Calcular vetor de distância
        dist_x = local_x - closest_x
        dist_y = local_y - closest_y
        dist_sq = dist_x**2 + dist_y**2
        
        # 5. Verificação inicial de colisão
        if dist_sq > radius**2 + 1e-6:  # Pequena margem para estabilidade numérica
            return [False, None]
        
        # 6. Tratamento especial para colisão exata no canto
        if dist_sq < 1e-12:  # Centro exatamente no canto
            # Encontrar o canto mais próximo (pode ser múltiplo em caso de empate)
            corner_x = half_w if local_x > 0 else -half_w
            corner_y = half_h if local_y > 0 else -half_h
            
            # Criar vetor de empurrão radial
            push_x = local_x - corner_x
            push_y = local_y - corner_y
            push_dist = max(np.sqrt(push_x**2 + push_y**2), 1e-6)
            
            mtv_local = np.array([push_x, push_y]) * (radius / push_dist)
        else:
            # 7. Caso normal: calcular MTV
            dist = np.sqrt(dist_sq)
            penetration = radius - dist
            
            # Evitar divisão por zero e normalizar
            if dist > 1e-6:
                mtv_local = np.array([dist_x, dist_y]) * (penetration / dist)
            else:
                mtv_local = np.array([radius, 0])  # Fallback seguro
                
            # 8. Ajuste para casos de tangência (maior empurrão)
            if dist < radius * 0.1:  # Quando muito próximo
                mtv_local *= 1.5
        
        # 9. Converter MTV de volta para o espaço global
        mtv_global = np.array([
            cos_a * mtv_local[0] - sin_a * mtv_local[1],
            sin_a * mtv_local[0] + cos_a * mtv_local[1]
        ])
        
        # 10. Ajuste final do MTV
        mtv_norm = np.linalg.norm(mtv_global)
        
        # Verificação de validade do MTV
        if mtv_norm < 1e-3 or not np.all(np.isfinite(mtv_global)):
            return [False, None]
        
        # Normalizar e garantir magnitude mínima
        min_mtv = radius * 0.01  # 1% do raio como mínimo
        if mtv_norm < min_mtv:
            mtv_global = mtv_global / mtv_norm * min_mtv
        
        return [True, mtv_global]


    def get_closest_point_on_rectangle(self, point, corners):
        """
        Obtém o ponto mais próximo na borda do retângulo em relação a um ponto externo.
        
        :param point: Ponto externo (numpy array) a ser testado.
        :param corners: Lista com os 4 cantos do retângulo (em ordem, já rotacionados).
        :return: O ponto mais próximo do retângulo ao ponto fornecido.
        """
        closest_point = None                # Vai armazenar o ponto mais próximo encontrado
        min_distance = float('inf')        # Inicializa a menor distância como infinita

        # Percorre cada lado do retângulo
        for i in range(len(corners)):
            start = corners[i]                         # Início do lado
            end = corners[(i + 1) % len(corners)]      # Fim do lado (conecta de forma circular)

            edge_vector = end - start                  # Vetor que representa o lado do retângulo
            point_vector = point - start               # Vetor do início do lado até o ponto externo

            # Projeção escalar do ponto no vetor da borda
            projection = np.dot(point_vector, edge_vector) / np.dot(edge_vector, edge_vector)

            # Limita a projeção entre 0 e 1, para que fique dentro do segmento de linha
            projection = max(0, min(1, projection))

            # Ponto mais próximo no segmento (projetado ao longo da borda)
            closest = start + projection * edge_vector

            # Calcula a distância entre o ponto externo e o ponto projetado
            distance = np.linalg.norm(point - closest)

            # Se a distância for a menor encontrada até agora, armazena o ponto
            if distance < min_distance:
                min_distance = distance
                closest_point = closest

        return closest_point   # Retorna o ponto mais próximo na borda do retângulo


    def check_collision_with_rectangle(self, other:CollisionRectangle):
        """
        Verifica colisão entre dois retângulos rotacionados usando o algoritmo SAT (Separating Axis Theorem).
        
        Retorna:
            [True, mtv] se houver colisão,
            [False, None] caso contrário.
        """
        corners1 = self.get_corners()         # Cantos do primeiro retângulo
        corners2 = other.get_corners()        # Cantos do segundo retângulo
        axes = []

        # Função auxiliar para calcular a normal de um lado do retângulo
        def get_normals(corners):
            normals = []
            for i in range(len(corners)):
                edge = corners[(i + 1) % len(corners)] - corners[i]  # Vetor do lado
                if np.linalg.norm(edge) == 0:
                    continue  # Evita divisões por zero (casos degenerados)
                normal = np.array([-edge[1], edge[0]])               # Normal perpendicular
                normals.append(normal / np.linalg.norm(normal))      # Normaliza
            return normals

        # Adiciona todas as normais (eixos candidatos) dos dois retângulos
        axes.extend(get_normals(corners1))
        axes.extend(get_normals(corners2))

        # MTV tracking
        min_overlap = float('inf')
        mtv_axis = None 

        # SAT: projetar os dois retângulos em cada eixo candidato
        for axis in axes:
            proj1 = [np.dot(corner, axis) for corner in corners1]  # Projeções do 1º retângulo
            proj2 = [np.dot(corner, axis) for corner in corners2]  # Projeções do 2º retângulo

            min1, max1 = min(proj1), max(proj1)
            min2, max2 = min(proj2), max(proj2)

            if max1<min2 or max2 < min1:
                return [False, None] # Sem colisão                
            
            #Calcula sobreposição
            overlap = min(max1,max2) - max(min1,min2)
            if overlap < min_overlap:
                min_overlap = overlap
                mtv_axis = axis.copy()

        # Ajusta a direção do MTV
        center1 = np.array([self.x, self.y])
        center2 = np.array([other.x, other.y])
        direction = center1 - center2
        if np.dot(direction, mtv_axis) <0:
            mtv_axis = -mtv_axis 

        if min_overlap < 1e-2: #1mm em escala virtual
            #use o vetor entre dois pontos mais próximos como MTV alternativo
            min_dist = float("inf")
            closest_pair = None 
            for c1 in corners1:
                for c2 in corners2:
                    d = np.linalg.norm(c1-c2)
                    if d<min_dist:
                        min_dist = d
                        closest_pair = (c1,c2)

            if closest_pair:
                alt_axis = closest_pair[1]-closest_pair[0]
                if np.linalg.norm(alt_axis) != 0:
                    mtv_axis = alt_axis / np.linalg.norm(alt_axis)
                    min_overlap = 1e-2
       
        mtv = mtv_axis *min_overlap 

        return [True, mtv]  # Nenhum eixo separador → colisão confirmada


    def rotate(self, alpha_graus, center = None):
        """
        Rotaciona o retângulo em torno de um centro arbitrário.

        :param alpha_graus: Ângulo em graus (sentido anti-horário).
        :param center: Centro de rotação (tupla ou array [x, y]).
        """
        if center is None:
            center = np.array([self.x, self.y])
        else:
            center = np.array(center)

        # Converte o ângulo para radianos
        alpha = np.radians(alpha_graus)

        # Calcula o vetor do centro do retângulo em relação ao ponto de rotação
        rel_x = self.x - center[0]
        rel_y = self.y - center[1]

        # Aplica a rotação ao centro do retângulo
        rotated_x = rel_x * np.cos(alpha) + rel_y * np.sin(alpha)
        rotated_y = -rel_x * np.sin(alpha) + rel_y * np.cos(alpha)

        # Atualiza as coordenadas do retângulo
        self.x = rotated_x + center[0]
        self.y = rotated_y + center[1]

        # Atualiza o ângulo do retângulo
        self.angle = (self.angle + alpha_graus) % 360

        # Atualiza os cantos se necessário
        if hasattr(self, "update_corners"):
            self.update_corners()



class CollisionGroup(CollisionObject):
    """
    Representa um objeto de colisão composto por múltiplos objetos de colisão.
    Os objetos internos são tratados como um único grupo coeso.
    """

    def __init__(self, objects, type_object, reference=None):
        """
        Inicializa um CollisionGroup com uma lista de objetos de colisão.
        :param objects: Lista de objetos de colisão (CollisionPoint, CollisionLine, etc.).
        :param type_object: Tipo do objeto (ex: "MOVING", "STRUCTURE").
        """
        super().__init__(type_object)
        self.objects = objects  # Lista de objetos de colisão
        self.reference = reference  # Referência ao objeto pai (ex: Robot, Ball, etc.)

        # Validação de tipos
        for obj in self.objects:
            if not isinstance(obj, CollisionObject):
                raise TypeError(f"Objeto inválido no grupo: {type(obj)}")

        self.points = self._extract_points()  # Extrai os pontos dos objetos internos
        self.aabb_corners = self._generate_aabb()

    def _extract_points(self):
        """
        Extrai os pontos de todos os objetos internos, mantendo o formato (x, y) como tuplas.
        Isso garante consistência para os cálculos posteriores.
        :return: Lista de pontos [(x1, y1), (x2, y2), ...].
        """
        points = []
        for obj in self.objects:
            if isinstance(obj, CollisionPoint):
                points.append((obj.x, obj.y))

            elif isinstance(obj, CollisionCircle):
                points.append((obj.x, obj.y))

            elif isinstance(obj, CollisionRectangle):
                points.extend([tuple(corner) for corner in obj.get_corners()])

            elif isinstance(obj, CollisionLine):
                start = tuple(obj.start) if isinstance(obj.start, np.ndarray) else obj.start
                end = tuple(obj.end) if isinstance(obj.end, np.ndarray) else obj.end
                points.append(start)
                points.append(end)

            elif isinstance(obj, CollisionGroup):
                points.extend(obj._extract_points())

        return points

    def _generate_aabb(self):
        '''
        Gera os 4 cantos da AABB que envolve todos os objetos internos.
        Retorna os cantos no sentido horário.
        '''
        xs = []
        ys = []

        for obj in self.objects:
            if hasattr(obj, 'get_corners'):
                corners = obj.get_corners()
                for corner in corners:
                    xs.append(corner[0])
                    ys.append(corner[1])
            elif isinstance(obj, CollisionLine):
                xs.extend([obj.start[0], obj.end[0]])
                ys.extend([obj.start[1], obj.end[1]])
            elif isinstance(obj, CollisionCircle):
                xs.append(obj.x - obj.radius)
                xs.append(obj.x + obj.radius)
                ys.append(obj.y - obj.radius)
                ys.append(obj.y + obj.radius)

            elif isinstance(obj, CollisionPoint):
                xs.append(obj.x)
                ys.append(obj.y)
            

        if not xs or not ys:
            return [np.array([0, 0])] * 4

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        return [
            np.array([min_x, min_y]),  # canto inferior esquerdo
            np.array([max_x, min_y]),  # canto inferior direito
            np.array([max_x, max_y]),  # canto superior direito
            np.array([min_x, max_y])   # canto superior esquerdo
        ]

    def _aabb_overlap(self, other_group):
        """
        Verifica se a AABB deste grupo colide com a AABB do outro grupo.
        """
        self_min = np.min(self.aabb_corners, axis=0)
        self_max = np.max(self.aabb_corners, axis=0)
        other_min = np.min(other_group.aabb_corners, axis=0)
        other_max = np.max(other_group.aabb_corners, axis=0)

        return not (
            self_max[0] < other_min[0] or self_min[0] > other_max[0] or
            self_max[1] < other_min[1] or self_min[1] > other_max[1]
        )

    def check_collision(self, other):
        """
        Verifica colisão com outro objeto externo.

        retorna:
            - [True, mtv]:  Se ocorreu alguma colisão.
            - [False, None]: Se não teve nenhuma colisão
        """
        self._generate_aabb() #Atualiza AABB antes de verificar

        if isinstance(other, CollisionGroup):
            return self._check_collision_with_group(other)

        return self._check_collision_with_object(other)

    def _check_collision_with_object(self, other):
        """
        Verifica a colisão do grupo coeso com outro objeto.

        retornos:
            [True, mtv] = Se houver colisão
            [False, None] = Se não houver colisão
        """
        menor_mtv = None
        menor_magnitude = float('inf')

        for shape in self.objects:
            collided, mtv = shape.check_collision(other)
            if collided:
                magnitude = np.linalg.norm(mtv)
                if magnitude < menor_magnitude:
                    menor_magnitude = magnitude
                    menor_mtv = mtv

        if menor_mtv is not None:
            return [True, menor_mtv]
        return [False, None]

    def _check_collision_with_group(self, other_group):
        """
        Verifica a colisão do grupo coeso com outro grupo coeso.

        retornos:
            [True, mtv] = Se houver colisão
            [False, None] = Se não houver colisão
        """
        if not self._aabb_overlap(other_group):
            return [False, None]  # Otimização: bounding boxes não colidem

        menor_mtv = None
        menor_magnitude = float('inf')

        for shape_self in self.objects:
            for shape_other in other_group.objects:
                collided, mtv = shape_self.check_collision(shape_other)
                if collided:
                    magnitude = np.linalg.norm(mtv)
                    if magnitude < menor_magnitude:
                        menor_magnitude = magnitude
                        menor_mtv = mtv

        if menor_mtv is not None:
            return [True, menor_mtv]
        return [False, None]

    def rotate(self, angle, center):
        """
        Rotaciona todos os objetos internos em torno de um centro.
        O centro deve ser uma tupla (x, y) e o ângulo em graus.
        """
        for obj in self.objects:
            if hasattr(obj, "rotate"):
                obj.rotate(angle, center)

        # Atualiza pontos e AABB após rotação
        self.points = self._extract_points()
        self.aabb_corners = self._generate_aabb()

    def get_bounding_box(self):
        """
        Retorna a AABB como tupla (min_x, min_y, max_x, max_y)
        """
        xs = [p[0] for p in self.aabb_corners]
        ys = [p[1] for p in self.aabb_corners]
        return min(xs), min(ys), max(xs), max(ys)

    def get_aabb(self):
        """
        Retorna os pontos do AABB para que possa ser desenhado na interface
        caso seja preciso.
        """
        if not hasattr(self, 'aabb_corners'):
            return

        corners = self.aabb_corners
        return [corner.tolist() for corner in corners]

    def add(self, obj):
        '''
        Adiciona novos objetos ao grupo de colisão e atualiza a AABB
        '''
        if not isinstance(obj, CollisionObject):
            raise TypeError(f"Objeto inválido adicionado: {type(obj)}")
        self.objects.append(obj)
        self.points = self._extract_points()
        self.aabb_corners = self._generate_aabb()


## Classe principal para controle das colisões
class CollisionManagerSAT:
    def __init__(self, cell_size=CELL_SIZE, screen=None, dt = float(0.0)):
        """
        Gerenciador de colisões usando SAT com otimização por Spatial Hashing.
        :param cell_size: Tamanho de cada célula da grade para particionamento espacial.
        Otimizando o tratamento de colisões

        Em geral, divido o mapa em várias celular com um certo tamanho, e verifico as colisões dentro dessas celulas.
        """
        self.cell_size = cell_size
        self.grid = defaultdict(list)

        #Ter conhecimento do dt do código
        self.dt = float(dt)

        #Apenas para debug virtual
        self.screen = screen

        #Cache para os pontos de contato
        self.contact_points_cache  = {}
        self.collision_pairs_cache = set()

        # Adicionar o detector de colisão contínua
        self.ccd = ContinuousCollisionDetector()
        self.ccd_threshold = 50.0 #Velocidade mínima para usar CDD (em)


    def detect_and_resolve(self, objects):
        """
        Detecta e resolve colisões entre os objetos passados, considerando apenas os tipos relevantes.
        :param objects: Lista de objetos com .collision_object, .velocity, .mass, etc.
        """
        self.clear()
        self.collision_pairs_cache.clear()

        #1. Verifica se são objetos de colisão apenas e passa todos para o grid
        for obj in objects:
            if hasattr(obj, "reference"):
                self.add_object(obj)


        # Fase de detecção
        collisions = []
        #2. Verifica colisões no grid
        for obj in objects:
            if obj.type_object != MOVING_OBJECTS:
                continue 
               
            nearby = self._get_nearby_objects(obj)

            #Verifica colisões com os vizinhos.
            for other in nearby:
                if obj is other or not hasattr(other,"reference"):
                    continue 

                pair_key = self._get_pair_key(obj, other)
                if pair_key in self.collision_pairs_cache:
                    continue
                
                #Adiciona para tratar
                self.collision_pairs_cache.add(pair_key)
                
                # Aplica CCD apenas se a bola estiver envolvida
                is_ball_involved = (
                    (obj.reference.type_object == BALL_OBJECT) or 
                    (other.reference.type_object == BALL_OBJECT)
                )

                if is_ball_involved and (
                    np.linalg.norm(obj.reference.velocity) > self.ccd_threshold or
                    np.linalg.norm(other.reference.velocity) > self.ccd_threshold
                ):
                    ccd_collision, t, normal = self.ccd.check_continuous_collision(obj, other, self.dt)
                    if ccd_collision:
                        mtv = normal * (1.0 - t) * np.linalg.norm(obj.reference.velocity) * self.dt
                        collisions.append((obj, other, mtv))
                else:
                    has_collision, mtv = obj.check_collision(other)
                    if has_collision and np.linalg.norm(mtv) > 1e-6:
                        collisions.append((obj, other, mtv))

        # Fase de resolução com pontos de contato
        for obj1, obj2, mtv in collisions:
            #Apenas calcula, por enquanto, os pontos de contato para objetos que não são do campo
            if obj1.reference.type_object != FIELD_OBJECT and obj2.reference.type_object != FIELD_OBJECT:
                contact_point = self.calculate_contact_point(obj1, obj2)
            else:
                contact_point = None 
                
            # Armazena para possível uso em debug/visualização
            pair_key = self._get_pair_key(obj1, obj2)
            self.contact_points_cache[pair_key] = contact_point
            
            if obj2.type_object == STRUCTURE_OBJECTS:
                self.resolve_collision_with_field(obj1, obj2, mtv)
            else:
                self.resolve_moving_collision(obj1, obj2, mtv, contact_point)

    def _get_pair_key(self, obj1, obj2):
        ''' Retorna uma chave única para o par de objetos'''
        return tuple(sorted((id(obj1),id(obj2))))
    
    def get_cached_contact_points(self,obj1, obj2):
        key = (id(obj1), id(obj2)) if id(obj1) < id(obj2) else (id(obj2), id(obj1))
        return self.contact_points_cache.get(key, None)

    def clear(self):
        """ Limpa o grid de detecção de colisões. """
        self.grid.clear()

    def _hash_position(self, x, y):
        """ Retorna o índice da célula no grid baseada na posição. """
        return int(x // self.cell_size), int(y // self.cell_size)

    def add_object(self, collision_obj):
        """
        Adiciona um objeto ao grid com base na sua posição.
        :param obj: Objeto com propriedades .x e .y
        """
        if isinstance(collision_obj, CollisionGroup):
            for member in collision_obj.objects:
                self.add_object(member)
            return 
        
        #Se for uma linha, calcula bouding box 
        if isinstance(collision_obj, CollisionLine):
            min_x = min(collision_obj.start[0], collision_obj.end[0])
            max_x = max(collision_obj.start[0], collision_obj.end[0])
            min_y = min(collision_obj.start[1], collision_obj.end[1])
            max_y = max(collision_obj.start[1], collision_obj.end[1])

            start_cell = self._hash_position(min_x, min_y)
            end_cell = self._hash_position(max_x, max_y)

            for x in range(start_cell[0], end_cell[0] + 1):
                for y in range(start_cell[1], end_cell[1] + 1):
                    self.grid[(x, y)].append(collision_obj)
            return

        #Se for um retângulo, calcula bounding box com base nos vértices
        elif isinstance(collision_obj, CollisionRectangle):
            # Obtém os vértices do retângulo
            vertices = collision_obj.get_corners()
            xs = [v[0] for v in vertices]
            ys = [v[1] for v in vertices]
            min_x = min(xs)
            max_x = max(xs)
            min_y = min(ys)
            max_y = max(ys)

        # Se for um círculo, usa raio para criar a bounding box
        elif isinstance(collision_obj, CollisionCircle):
            min_x = collision_obj.x - collision_obj.radius
            max_x = collision_obj.x + collision_obj.radius
            min_y = collision_obj.y - collision_obj.radius
            max_y = collision_obj.y + collision_obj.radius

        # Caso contrário, assume que o objeto tem posição .x e .y (como ponto)
        else:
            min_x = max_x = collision_obj.x
            min_y = max_y = collision_obj.y
     
        # Calcula as céclulas que a bouding box cobre
        start_cell  = self._hash_position(min_x, min_y)
        end_cell    = self._hash_position(max_x, max_y)

        for x in range(start_cell[0], end_cell[0]+1):
            for y in range(start_cell[1],end_cell[1]+1):
                self.grid[(x,y)].append(collision_obj)
        

    def _get_nearby_objects(self, obj):
        """
        Retorna objetos nas células vizinhas (incluindo a célula atual).
        Retorna os objetos na célula atual e nas 8 células ao redor.
        """
        cx, cy = self._hash_position(obj.x, obj.y)
        nearby = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                cell = (cx + dx, cy + dy)
                nearby.extend(self.grid.get(cell, []))

        return nearby   
    
    def draw_mtv(self, obj, mtv, color=(255,0,0)):
        if not self.screen: return 
        #Desenhando o vetor mtv para debug
        start_pos = (int(obj.x), int(obj.y))
        end_pos = (int(obj.x + mtv[0]*10), int(obj.y + mtv[1]*10))  # escala para visual
        pygame.draw.line(self.screen, color, start_pos, end_pos, 2)

    def check_segment_intersection(self, p1, p2, q1, q2):
        """
        Verifica se os segmentos [p1, p2] e [q1, q2] se cruzam.
        Retorna (True, ponto) se sim.
        """
        def ccw(a, b, c):
            return (c[1]-a[1])*(b[0]-a[0]) > (b[1]-a[1])*(c[0]-a[0])
        if (ccw(p1, q1, q2) != ccw(p2, q1, q2)) and (ccw(p1, p2, q1) != ccw(p1, p2, q2)):
            return True, None
        return False, None

    def check_segment_circle_intersection(self, p1, p2, center, radius):
        """
        Verifica se o segmento [p1, p2] intersecta o círculo com dado centro e raio.
        """
        d = p2 - p1
        f = p1 - center
        a = np.dot(d, d)
        b = 2 * np.dot(f, d)
        c = np.dot(f, f) - radius * radius
        discriminant = b*b - 4*a*c
        if discriminant < 0:
            return False
        discriminant = np.sqrt(discriminant)
        t1 = (-b - discriminant)/(2*a)
        t2 = (-b + discriminant)/(2*a)
        return (0 <= t1 <= 1) or (0 <= t2 <= 1)
    
                    
    def resolve_moving_collision(self, obj1, obj2, mtv, contact_points = None):
        """
        Resolve colisão entre dois objetos móveis com conservação de momento linear.
        :param obj1, obj2: objetos com massa, velocidade e posição.

        :param mtv: vetor mínimo de translação do SAT (resolve a sobreposição).
         Esse MTV deve ser calculado de Obj2 para Obj1
        """
        #print("Resolvendo colisão de objetos em movimento")
        
        #Pegando os pais que estão controlando os objetos de colisão
        obj1 = obj1.reference
        obj2 = obj2.reference

        # Proteção: MTV nulo ou objetos sem massa válida
        mtv_norm = np.linalg.norm(mtv)
        if mtv_norm < 1e-6 or obj1.mass <= 0 or obj2.mass <= 0:
            return  #silenciosamente ignora colisões inválidas
        
        # Corrige direção da MTV
        pos_diff = obj1.position - obj2.position
        if np.dot(mtv, pos_diff) < 0:
            mtv = -mtv
            mtv_norm = np.linalg.norm(mtv)

        # Limine mínimo para evitar micro-colisões
        if mtv_norm < 0.001:
            return 
        
        # Normalizada do vetor de separação (direção da colisão)
        normal = mtv / mtv_norm

        # Verifica se MTV é suficiente (baseado em velocidade relativa)
        # Separação posicional proporcional à massa
        total_mass = obj1.mass + obj2.mass
        correction = mtv * (1.01 + np.linalg.norm(obj1.velocity - obj2.velocity) * 0.01)
        obj1.position += correction * (obj2.mass / total_mass)
        obj2.position -= correction * (obj1.mass / total_mass)

       # === Ponto de contato ===
        type1 = obj1.type_object
        type2 = obj2.type_object

        if {type1, type2} == {ROBOT_OBJECT, BALL_OBJECT}:
            # Robô-Bola → ponto estimado: centro da bola
            if type1 == BALL_OBJECT:
                collision_point = obj1.position.copy()
            else:
                collision_point = obj2.position.copy()

        elif {type1, type2} == {ROBOT_OBJECT}:
            # Robô-Robô → ponto mais próximo entre as bordas dos retângulos
            poly1 = Polygon(obj1.collision_object.get_corners())
            poly2 = Polygon(obj2.collision_object.get_corners())

            line1 = poly1.exterior
            line2 = poly2.exterior

            # Ponto mais próximo entre os contornos
            p1, p2 = line1.interpolate(line1.project(line2.centroid)).coords[0], \
                    line2.interpolate(line2.project(line1.centroid)).coords[0]

            collision_point = (np.array(p1) + np.array(p2)) / 2
        else:
            collision_point = (obj1.position + obj2.position) / 2


        # Vetores do centro ao ponto de contato
        r1 = collision_point - obj1.position
        r2 = collision_point - obj2.position

        # Velocidade rotacional nos pontos de contato (v = ω × r)
        v_rot1 = np.array([
            -obj1.angular_velocity * r1[1],
            obj1.angular_velocity * r1[0]
        ])
        v_rot2 = np.array([
            -obj2.angular_velocity * r1[1],
            obj2.angular_velocity * r1[0]
        ])
        # Velocidade total nos pontos de contato (linear + rotacional)
        v1_total = obj1.velocity + v_rot1
        v2_total = obj2.velocity + v_rot2

        # Velocidade relativa no ponto de contato
        v_rel = v1_total - v2_total

        # Componente da velocidade relativa na direção normal
        vel_along_normal = np.dot(v_rel, normal)
   
        if vel_along_normal > 0:
            return  # já estão se separando

        # Coeficientes
        if {type1, type2} == {ROBOT_OBJECT, BALL_OBJECT}:
            restitution = COEFFICIENT_RESTITUTION_BALL_ROBOT
            friction = COEFICIENT_FRICTION_BALL_ROBOT
        elif {type1, type2} == {ROBOT_OBJECT}:
            restitution = COEFFICIENT_RESTITUTION_ROBOT_ROBOT
            friction = COEFICIENT_FRICTION_ROBOT_ROBOT
        else:
            restitution = 0.5
            friction = 0.1

        # Calculando impulso escalar
        inv_mass1 = 1 / obj1.mass
        inv_mass2 = 1 / obj2.mass
        inv_inertia1 = 1 / getattr(obj1, 'inertia', 1)
        inv_inertia2 = 1 / getattr(obj2, 'inertia', 1)

        r1_cross_n = np.cross(r1,normal)
        r2_cross_n = np.cross(r2, normal)

        denom = inv_mass1 + inv_mass2 + (r1_cross_n**2) * inv_inertia1 + (r2_cross_n**2) * inv_inertia2
        impulse_mag = -(1 + restitution) * vel_along_normal / denom
        impulse_mag = np.clip(impulse_mag, -MAX_IMPULSE, MAX_IMPULSE)
        
        # Impulso na direção normal
        impulse = impulse_mag * normal 

        obj1.apply_impulse(+impulse, collision_point)
        obj2.apply_impulse(-impulse, collision_point)

        tangent = np.array([-normal[1], normal[0]])
        tangent /= np.linalg.norm(tangent)
        v_rel_tangent = np.dot(v_rel, tangent)

        jt = -v_rel_tangent / denom
        jt = np.clip(jt, -abs(impulse_mag) * friction, abs(impulse_mag) * friction)
        friction_impulse = jt * tangent

        obj1.apply_impulse(+friction_impulse, collision_point)
        obj2.apply_impulse(-friction_impulse, collision_point)

        # Limita velocidades para evitar instabilidades numéricas
        MAX_VELOCITY = 100.0  # Limite de velocidade linear
        MAX_ANGULAR_VELOCITY = 10.0  # Limite de velocidade angular

        # Limita a velocidade linear (magnitude do vetor)
        velocity_magnitude = np.linalg.norm(obj1.velocity)
        if velocity_magnitude > MAX_VELOCITY:
            obj1.velocity = (obj1.velocity / velocity_magnitude) * MAX_VELOCITY

        velocity_magnitude = np.linalg.norm(obj2.velocity)
        if velocity_magnitude > MAX_VELOCITY:
            obj2.velocity = (obj2.velocity / velocity_magnitude) * MAX_VELOCITY

        obj1.angular_velocity = np.clip(obj1.angular_velocity, -MAX_ANGULAR_VELOCITY, MAX_ANGULAR_VELOCITY)
        obj2.angular_velocity = np.clip(obj2.angular_velocity, -MAX_ANGULAR_VELOCITY, MAX_ANGULAR_VELOCITY)

    def line_segment_intersect(self, p1, p2, q1, q2):
        def ccw(a, b, c):
            return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])
        return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)


    def resolve_collision_with_field(self, obj, objfield, mtv, contact_points=None):
        """
        Resolve colisão entre objeto móvel e o campo (estrutura estática de massa infinita).
        Aplica múltiplos impulsos e torques realistas, agrupando pontos próximos.
        """

        obj = obj.reference
  
        norm_mtv = np.linalg.norm(mtv)
        if norm_mtv == 0:
            print("MTV nulo — colisão ignorada.")
            return

        # Direção do MTV — deve ir de objfield → obj
        pos_field = np.array([objfield.x, objfield.y]) if hasattr(objfield, 'x') else np.mean(objfield.get_corners(), axis=0)
        object_pos = np.array([obj.x, obj.y])
        normal = mtv / norm_mtv
        if np.dot(object_pos - pos_field, normal) < 0:
            normal = -normal
            mtv = -mtv

        # Escala MTV com velocidade e dt (para garantir separação em velocidades altas)
        velocity_along_normal = np.dot(obj.velocity, normal)
        velocity_factor = abs(velocity_along_normal) * self.dt
        mtv *= (1.0 + velocity_factor * 0.2)  # fator ajustável

        # Corrige posição
        obj.x += mtv[0]
        obj.y += mtv[1]
        obj.collision_object.x = obj.x
        obj.collision_object.y = obj.y

        # --- Parâmetros de colisão por tipo ---
        type_name = type(obj).__name__
        if 'Ball' in type_name:
            restitution = COEFFICIENT_RESTITUTION_BALL_FIELD
            friction = 0.0
            contact_points = [object_pos.copy()]
        elif 'Robot' in type_name:
            restitution = COEFFICIENT_RESTITUTION_ROBOT_FIELD
            friction = COEFICIENT_FRICTION_ROBOT_FIELD
            if hasattr(obj.collision_object, "get_corners"):
                corners = obj.collision_object.get_corners()
                mid_edges = [(corners[i] + corners[(i + 1) % 4]) / 2 for i in range(4)]
                contact_points = corners + mid_edges
            else:
                contact_points = [object_pos.copy()]
        else:
            restitution = 0.3
            friction = 0.05
            contact_points = [object_pos.copy()]

        # --- Filtra pontos redundantes (agrupa próximos) ---
        filtered_points = []
        eps = 1.0  # Tolerância em cm
        for p in contact_points:
            if all(np.linalg.norm(p - fp) > eps for fp in filtered_points):
                filtered_points.append(p)

        # --- Aplica impulso e torque nos pontos filtrados ---
        obj_inv_mass = 1 / obj.mass
        obj_inv_inertia = 1 / obj.inertia

        for point in filtered_points:
            r = point - object_pos
            vel_at_contact = obj.velocity + obj.angular_velocity * np.array([-r[1], r[0]])
            vel_normal = np.dot(vel_at_contact, normal)
            if vel_normal >= 0:
                continue

            rn = np.cross(r, normal)
            denom = obj_inv_mass + (rn ** 2) * obj_inv_inertia
            j = -(1 + restitution) * vel_normal / denom

            j = np.clip(j, -100, 100)

            impulse = j * normal
            obj.apply_impulse(impulse, point)

            # Atrito
            tangent = np.array([-normal[1], normal[0]])
            vel_tangent = np.dot(vel_at_contact, tangent)
            jt = -vel_tangent / denom
            jt = np.clip(jt, -abs(j) * friction, abs(j) * friction)
            friction_impulse = jt * tangent
            obj.apply_impulse(friction_impulse, point)
            
        # Limita velocidades para evitar instabilidades numéricas
        MAX_VELOCITY = 200.0  # Limite de velocidade linear
        MAX_ANGULAR_VELOCITY = 10.0  # Limite de velocidade angular

        velocity_magnitude = np.linalg.norm(obj.velocity)
        if velocity_magnitude > MAX_VELOCITY:
            obj.velocity = (obj.velocity / velocity_magnitude) * MAX_VELOCITY

        obj.angular_velocity = np.clip(obj.angular_velocity, -MAX_ANGULAR_VELOCITY, MAX_ANGULAR_VELOCITY)

        # Damping
        obj.velocity *= (1 - 0.02 * self.dt * 60)  # Aproximadamente 2% por frame a 60fps
        obj.angular_velocity *= (1 - 0.5 * self.dt * 60)


    # Método interessante para detectar os pontos de colisão
    def calculate_contact_point(self, obj1, obj2):
        """
        Calcula o ponto de contato mais preciso entre dois objetos.
        
        Args:
            obj1: Primeiro objeto de colisão
            obj2: Segundo objeto de colisão
            mtv: Vetor mínimo de translação
            
        Returns:
            np.array: Ponto de contato [x, y] no espaço do jogo
        """
        #Puxo os objetos donos dos objetos de colisão
        obj1 = obj1.reference
        obj2 = obj2.reference 

        # Caso 1: Colisão entre bola e robô
        if {obj1.type_object, obj2.type_object} == {BALL_OBJECT, ROBOT_OBJECT}:
            ball = obj1 if obj1.type_object == BALL_OBJECT else obj2
            robot = obj2 if obj1.type_object == BALL_OBJECT else obj1
            
            # Para bola-robô, o ponto é o mais próximo no robô à bola
            robot_corners = robot.collision_object.get_corners()
            robot_poly = Polygon(robot_corners)
            ball_point = Point(ball.position)
            
            # Projeta o centro da bola no contorno do robô
            nearest_point = robot_poly.exterior.interpolate(
                robot_poly.exterior.project(ball_point))
            
            return np.array(nearest_point.coords[0])

        # Caso 2: Colisão robô-robô
        elif obj1.type_object == ROBOT_OBJECT and obj2.type_object == ROBOT_OBJECT:
            # Usa o ponto médio entre os pontos mais próximos
            poly1 = Polygon(obj1.collision_object.get_corners())
            poly2 = Polygon(obj2.collision_object.get_corners())
            
            p1 = poly1.exterior.interpolate(poly1.exterior.project(poly2.centroid))
            p2 = poly2.exterior.interpolate(poly2.exterior.project(poly1.centroid))
            
            return (np.array(p1.coords[0]) + np.array(p2.coords[0])) / 2

        # Caso 3: Colisão genérica (ponto médio da área de sobreposição)
        else:
            try:
                # Tenta calcular a área de sobreposição
                poly1 = Polygon(obj1.collision_object.get_corners())
                poly2 = Polygon(obj2.collision_object.get_corners())
                overlap = poly1.intersection(poly2)
                
                if not overlap.is_empty:
                    return np.array([overlap.centroid.x, overlap.centroid.y])
            except:
                pass
            
            # Fallback: ponto médio entre os centros
            return (obj1.position + obj2.position) / 2
        
    # Função para desenhar os pontos de colisão
    def draw_contact_points(self, screen):
        """Método para debug: desenha pontos de contato na tela"""
        for point in self.contact_points_cache.values():
            pos = virtual_to_screen(point)
            pygame.draw.circle(screen, (255, 0, 0), pos, 5)



class ContinuousCollisionDetector:
    def __init__(self):
        self.normal_cache = {}  # Cache para normais
    
    def get_edge_normal(self, p1, p2):
        cache_key = (tuple(p1), tuple(p2))
        if cache_key in self.normal_cache:
            return self.normal_cache[cache_key]
        
        edge_vector = p2 - p1
        normal = np.array([-edge_vector[1], edge_vector[0]])
        norm = np.linalg.norm(normal)
        
        if norm > 1e-6:
            normal = normal / norm
        
        self.normal_cache[cache_key] = normal
        return normal
    
    def ray_segment_intersect(self, ro, rd, p1, p2):
        """Testa interseção entre raio e segmento com tratamento de raio"""
        v1 = ro - p1
        v2 = p2 - p1
        v3 = np.array([-rd[1], rd[0]])
        
        dot = np.dot(v2, v3)
        if abs(dot) < 1e-6:
            return False, None
        
        t1 = np.cross(v2, v1) / dot
        t2 = np.dot(v1, v3) / dot
        
        if t1 >= 0 and 0 <= t2 <= 1:
            return True, t1
        
        return False, None
    
    def check_robot_ball_ccd(self, robot, ball, dt):
        """CCD específico para retângulo (robô) e bola"""
        # Acessa os objetos de referência corretamente
        robot_ref = robot.reference
        ball_ref = ball.reference
        
        # Calcula movimento previsto
        start_pos = ball_ref.position
        end_pos = ball_ref.position + ball_ref.velocity * dt
        movement = end_pos - start_pos
        
        # Testa contra todas as arestas do robô
        rect_corners = robot.get_corners()
        t_first = float('inf')
        collision_normal = None
        
        for i in range(4):
            edge_p1 = rect_corners[i]
            edge_p2 = rect_corners[(i+1)%4]
            
            # Testa interseção considerando o raio da bola
            hit, t = self._swept_circle_edge_test(
                start_pos, ball.radius,
                movement, edge_p1, edge_p2
            )
            
            if hit and t < t_first:
                t_first = t
                collision_normal = self.get_edge_normal(edge_p1, edge_p2)
        
        if t_first <= 1.0:
            return True, t_first, collision_normal
        
        return False, None, None
    
    def _swept_circle_edge_test(self, circle_pos, radius, movement, edge_p1, edge_p2):
        """Testa interseção entre círculo em movimento e aresta"""
        # Implementação mais precisa considerando o raio
        edge_vec = edge_p2 - edge_p1
        edge_len = np.linalg.norm(edge_vec)
        edge_dir = edge_vec / edge_len if edge_len > 0 else np.zeros(2)
        
        # Calcula ponto mais próximo na aresta
        to_circle = circle_pos - edge_p1
        projection = np.dot(to_circle, edge_dir)
        projection = max(0, min(edge_len, projection))
        closest = edge_p1 + projection * edge_dir
        
        # Vetor do ponto mais próximo ao círculo
        to_center = circle_pos - closest
        dist_sq = np.dot(to_center, to_center)
        
        # Se já está colidindo no frame atual
        if dist_sq <= radius**2:
            return True, 0.0
        
        # Se está se movendo para longe
        if np.dot(movement, to_center) >= 0:
            return False, None
        
        # Testa interseção com cápsula (aresta + raio)
        return self.ray_segment_intersect(
            circle_pos, movement,
            closest + to_center/np.sqrt(dist_sq)*radius,
            closest + to_center/np.sqrt(dist_sq)*radius
        )
    
    def check_continuous_collision(self, objA, objB, dt):
        """Verificação genérica de CCD"""
        # Caso robô-bola
        if isinstance(objA, CollisionRectangle) and isinstance(objB, CollisionCircle):
            return self.check_robot_ball_ccd(objA, objB, dt)
        # Caso bola-robô (inverte a ordem)
        elif isinstance(objA, CollisionCircle) and isinstance(objB, CollisionRectangle):
            collided, t, normal = self.check_robot_ball_ccd(objB, objA, dt)
            return collided, t, -normal if normal is not None else None
        
        # Adicione outros casos aqui (bola-bola, robô-robô)
        return False, None, None