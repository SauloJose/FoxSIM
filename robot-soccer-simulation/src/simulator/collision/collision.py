from __future__ import annotations  # Permite usar strings para tipagem tardia
import numpy as np
from typing import TYPE_CHECKING
from ui.interface_config import *
from collections import defaultdict
import pygame 

# Importações para tipagem tardia, evitando problemas de importação circular
if TYPE_CHECKING:
    from simulator.objects.robot import Robot
    from simulator.objects.ball import Ball
    from simulator.objects.field import Field

# Constantes de coeficientes de restituição
COEFFICIENT_RESTITUTION_BALL_ROBOT = 1.0
COEFFICIENT_RESTITUTION_ROBOT_ROBOT = 0.2
COEFFICIENT_RESTITUTION_BALL_FIELD = 0.6
COEFFICIENT_FRICTION_ROBOT_FIELD = 0.5 
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
            return self.check_collision_with_circle(other)
        elif isinstance(other, CollisionPoint):
            return other.check_collision(self)
        elif isinstance(other, CollisionLine):
            return other.check_collision_with_circle(self)
        elif isinstance(other, CollisionRectangle):
            return other.check_collision_with_circle(self)
        elif isinstance(other, CollisionGroup):
            return other.check_collision(self)
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
            return other.check_collision_with_rectangles(self)

        # Caso o outro objeto seja uma polilinha, também delega a verificação para o objeto da polilinha
        elif isinstance(other, CollisionGroup):
            return other.check_collision(self)

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
        """
        cx, cy = circle.x, circle.y
        radius = circle.radius

        # Transforma o centro do círculo para o espaço local do retângulo
        dx = cx - self.x
        dy = cy - self.y
        angle_rad = -np.radians(self.angle)

        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)
        local_x = cos_a * dx - sin_a * dy
        local_y = sin_a * dx + cos_a * dy

        # Limita o ponto ao retângulo (em seu espaço local)
        half_w = self.width / 2
        half_h = self.height / 2

        closest_x = max(-half_w, min(local_x, half_w))
        closest_y = max(-half_h, min(local_y, half_h))

        # Distância do centro da bola ao ponto mais próximo do retângulo
        dist_x = local_x - closest_x
        dist_y = local_y - closest_y
        dist_sq = dist_x**2 + dist_y**2

        if dist_sq > radius**2:
            return [False, None]

        # Colisão detectada — calcula MTV
        dist = np.sqrt(dist_sq)
        if dist != 0:
            # MTV no espaço local
            penetration = radius - dist
            mtv_local = np.array([dist_x, dist_y]) / dist * penetration
            if dist < 1e-2:
                mtv_local *=1.5 #Empurrão extra em tangenciamentos quase exatos
        else:
            # Caso especial: centro da bola está exatamente no canto — empurra radialmente
            # Exemplo: empurra para a direita
            direction_local = np.array([local_x, local_y])
            if np.linalg.norm(direction_local) != 0:
                mtv_local = (direction_local / np.linalg.norm(direction_local))*radius
            else:
                mtv_local = np.array([1.0, 0.0]) * radius

        # Converte MTV de volta ao espaço global
        mtv_global = np.array([
            cos_a * mtv_local[0] + -sin_a * mtv_local[1],
            sin_a * mtv_local[0] +  cos_a * mtv_local[1],
        ])

        #Cortanto o MTV caso seja numericamente estável
        if np.linalg.norm(mtv_global) <1e-3:
            return [False, None]
        
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
        self.points = self._extract_points()  # Extrai os pontos dos objetos internos
        self.reference = reference  # Referência ao objeto pai (ex: Robot, Ball, etc.)

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
                # Adiciona o centro do círculo como ponto
                points.append((obj.x, obj.y))

            elif isinstance(obj, CollisionRectangle):
                # Adiciona os cantos do retângulo como tuplas
                points.extend([tuple(corner) for corner in obj.get_corners()])

            elif isinstance(obj, CollisionLine):
                # Converte para tupla se for np.array
                start = tuple(obj.start) if isinstance(obj.start, np.ndarray) else obj.start
                end = tuple(obj.end) if isinstance(obj.end, np.ndarray) else obj.end
                
                #Adiciono os pontos que configuram essa linha
                points = [start, end]
                points.append(points)

            elif isinstance(obj, CollisionGroup):
                # Reutiliza o método recursivamente para subgrupos
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
        if isinstance(other, CollisionGroup):
            return self._check_collision_with_group(other)
        
        #se for um objeto individual
        return self._check_collision_with_object(other)


    def _check_collision_with_object(self, other):
        '''
            Verifica a colisão do grupo coeso com outro um objeto.

            retornos
                [True, mtv] = Se haver colisão
                [False, None] = Não teve colisão
        '''
        menor_mtv = None
        menor_magnitude = float('inf')

        for shape in self.shapes:
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
        '''
            Verifica a colisão do grupo coeso com outro grupo coeso.

            retornos
                [True, mtv] = Se haver colisão
                [False, None] = Não teve colisão
        '''
        if not self._aabb_overlap(other_group):
            return [False, None]    #Otimização: bounding boxes não colidem
        
        menor_mtv = None 
        menor_magnitude = float('inf')

        for shape_self in self.shapes:
            for shape_other in other_group.shapes:
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
        :param angle: Ângulo de rotação.
        :param center: Centro de rotação.
        """
        for obj in self.objects:
            if hasattr(obj, "rotate"):
                obj.rotate(angle, center)

        # Após a rotação, atualiza os pontos internos
        self.points = self._extract_points()

    def get_bounding_box(self):
        """
        Retorna a AABB como tupla (min_x, min_y, max_x, max_y)
        """
        xs = [p[0] for p in self.aabb_corners]
        ys = [p[1] for p in self.aabb_corners]
        return min(xs), min(ys), max(xs), max(ys)

    #Para exibir
    def get_aabb(self):
        """
            Retorna os pontos do AABB para que possa ser desenhado na interface
            caso seja preciso.
        """
        if not hasattr(self, 'aabb_corners'):
            return

        corners = self.aabb_corners
        points = [corner.tolist() for corner in corners]
        
        return points

## Classe principal para controle das colisões
class CollisionManagerSAT:
    def __init__(self, cell_size=CELL_SIZE, screen=None):
        """
        Gerenciador de colisões usando SAT com otimização por Spatial Hashing.
        :param cell_size: Tamanho de cada célula da grade para particionamento espacial.
        Otimizando o tratamento de colisões

        Em geral, divido o mapa em várias celular com um certo tamanho, e verifico as colisões dentro dessas celulas.
        """
        self.cell_size = cell_size
        self.grid = defaultdict(list)

        #Apenas para debug virtual
        self.screen = screen

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
        #Desenhando o vetor mtv para debug
        start_pos = (int(obj.x), int(obj.y))
        end_pos = (int(obj.x + mtv[0]*10), int(obj.y + mtv[1]*10))  # escala para visual
        pygame.draw.line(self.screen, color, start_pos, end_pos, 2)

    def detect_and_resolve(self, objects):
        """
        Detecta e resolve colisões entre os objetos passados, considerando apenas os tipos relevantes.
        :param objects: Lista de objetos com .collision_object, .velocity, .mass, etc.
        """
        self.clear()
        #print("\n[COLISSION]: Novo detect e resolve acionado =================\n")
        #1. Verifica se são objetos de colisão apenas e passa todos para o grid
        for obj in objects:
            if hasattr(obj, "reference"):
                self.add_object(obj)

        #Verifica se o par já foi checado anteriormente.
        checked_pairs = set()

        #2. Verifica colisões no grid
        for obj in objects:
            if obj.type_object != MOVING_OBJECTS:
                continue 
            
            
            nearby = self._get_nearby_objects(obj)

            #if obj.reference.type_object == BALL_OBJECT:
            #    print(f"\n[DEBUG]: Objeto analisado é a bola")
            #    print("Objetos na vizinhança:", [obj.reference.type_object for obj in nearby])
            #elif obj.reference.type_object == ROBOT_OBJECT:
            #    print(f"\n[DEBUG]: Objeto analisado é o Robô {obj.reference.role} do time {obj.reference.team} com id {obj.reference.id_robot}")
            #    print("Objetos na vizinhança:",[obj.reference.type_object for obj in nearby])


            #Verifica colisões com os vizinhos.
            for other in nearby:
                if obj is other or not hasattr(other,"reference"):
                    continue 

                #cria o par ordenado de IDs para evitar dupla verificação
                pair = (min(id(obj), id(other)),max(id(obj),id(other)))
                
                if pair in checked_pairs:
                    continue
                
                #Adiciona para tratar
                checked_pairs.add(pair)

                other_type = other.type_object 

                # MOVING x STRUCTURE:
                if other_type == STRUCTURE_OBJECTS:
                    hasCollision, mtv = obj.check_collision(other)
                    if hasCollision and np.linalg.norm(mtv) > 1e-6:
                        #print(f"Objeto inicial {obj.reference.type_object} colidiu com {type(other).__name__} que é um {other.type_object} de {type(other.reference).__name__}")
                        dist = np.array([obj.x,obj.y]) - np.array([other.x,other.y])
                        moddist = np.linalg.norm(dist)
                        self.draw_mtv(obj,mtv,color=(255,0,0))
                        #raise RuntimeError("Parou para debug, verificando colisão com o campo")
                        self.resolve_collision_with_field(obj, mtv)
                    #else:
                    #    print(f"Objeto inicial {obj.reference.type_object} não colidiu com {type(other).__name__} que é um {other.type_object} de {type(other.reference).__name__}")
                    continue

                # MOVING x MOVING
                if other_type == MOVING_OBJECTS:
                    hasCollision, mtv = obj.check_collision(other)
                    if hasCollision and np.linalg.norm(mtv) > 1e-6:
                        dist = np.array([obj.x,obj.y]) - np.array([other.x,other.y])
                        moddist = np.linalg.norm(dist)
                        self.draw_mtv(obj,mtv,color=(255,0,0))
                        self.resolve_moving_collision(obj, other, mtv)
                    
    def resolve_moving_collision(self, obj1, obj2, mtv):
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
        if mtv_norm < 1e-6:
            print("MTV nulo — colisão ignorada.")
            return
        if not hasattr(obj1, 'mass') or not hasattr(obj2, 'mass'):
            print("Um dos objetos não possui massa — colisão ignorada.")
            return
        if obj1.mass <= 0 or obj2.mass <= 0:
            print("Massa inválida em um dos objetos — colisão ignorada.")
            return

        # Normalizada do vetor de separação (direção da colisão)
        normal = mtv / np.linalg.norm(mtv)

        # Separação mínima (posicional)
        # Separação posicional proporcional à massa
        total_mass = obj1.mass + obj2.mass
        correction = mtv *1.01  #Levemente maior para garantir a separação
        obj1.position += correction*(obj2.mass/total_mass)
        obj2.position -= correction*(obj1.mass/total_mass)

        # Estimativa do ponto de colisão (centro entre os dois objetos)
        collision_point = (obj1.position+obj2.position)/2

        # Vetores do centro ao ponto de contato
        r1 = collision_point - obj1.position
        r2 = collision_point - obj2.position

        # Velocidade rotacional nos pontos de contato (v = ω × r)
        v_rot1 = getattr(obj1, 'angular_velocity', 0.0) * np.array([-r1[1], r1[0]])
        v_rot2 = getattr(obj2, 'angular_velocity', 0.0) * np.array([-r2[1], r2[0]])

        # Velocidade total nos pontos de contato (linear + rotacional)
        v1_total = obj1.velocity + v_rot1
        v2_total = obj2.velocity + v_rot2

        # Velocidade relativa no ponto de contato
        v_rel = v1_total - v2_total

        # Componente da velocidade relativa na direção normal
        vel_along_normal = np.dot(v_rel, normal)
   
        if vel_along_normal > 0:
            return  # já estão se separando

        type1 = type(obj1).__name__
        type2 = type(obj2).__name__

        # Restituição
        if 'Ball' in (type1, type2) and 'Robot' in (type1, type2):
            restitution = COEFFICIENT_RESTITUTION_BALL_ROBOT
            friction = COEFICIENT_FRICTION_ROBOT_ROBOT  # Pode refinar esse se quiser diferenciar atrito bola-robô
        elif 'Robot' in type1 and 'Robot' in type2:
            restitution = COEFFICIENT_RESTITUTION_ROBOT_ROBOT
            friction = COEFICIENT_FRICTION_ROBOT_ROBOT
        else:
            restitution = 0.5  # fallback
            friction = 0.1     # fallback

        # Calculando impulso escalar
        inv_mass1 = 1 / obj1.mass
        inv_mass2 = 1 / obj2.mass
        inv_inertia1 = 1 / getattr(obj1, 'inertia', 1)
        inv_inertia2 = 1 / getattr(obj2, 'inertia', 1)

        r1_cross_n = r1[0] * normal[1] - r1[1] * normal[0]
        r2_cross_n = r2[0] * normal[1] - r2[1] * normal[0]

        denom = inv_mass1 + inv_mass2 + (r1_cross_n**2) * inv_inertia1 + (r2_cross_n**2) * inv_inertia2

        impulse_mag = -(1 + restitution) * vel_along_normal / denom
        
        MAX_IMPULSE = 100 # (cm/s * kg)
        impulse_mag = np.clip(impulse_mag, -MAX_IMPULSE, MAX_IMPULSE)
        
        # Impulso na direção normal
        impulse = impulse_mag * normal 


        # Aplicação do impulso linear (Torque - Impulso angular)
        obj1.velocity += impulse / obj1.mass
        obj2.velocity -= impulse / obj2.mass

        # --- Impulso Angular (Torque) ---
        # Torque (impulso angular)
        obj1.angular_velocity += r1_cross_n * impulse_mag * inv_inertia1
        obj2.angular_velocity -= r2_cross_n * impulse_mag * inv_inertia2

        # Impulso de atrito (tangencial)
        tangent = np.array([-normal[1], normal[0]])
        v_rel_tangent = np.dot(v_rel, tangent)

        # Cálculo do impulso de atrito limitado
        friction_impulse_mag = -v_rel_tangent * friction
        max_friction = np.abs(impulse_mag)*friction
        friction_impulse_mag = np.clip(friction_impulse_mag, -max_friction, max_friction)
        impulse_friction = friction_impulse_mag * tangent

        # Aplicação do impulso de atrito
        obj1.velocity += impulse_friction * inv_mass1
        obj2.velocity -= impulse_friction * inv_mass2

        # Torque devido ao atrito (gira em sentido contrário ao deslizamento)
        r1_cross_t = r1[0] * tangent[1] - r1[1] * tangent[0]
        r2_cross_t = r2[0] * tangent[1] - r2[1] * tangent[0]
        obj1.angular_velocity += r1_cross_t * friction_impulse_mag * inv_inertia1
        obj2.angular_velocity -= r2_cross_t * friction_impulse_mag * inv_inertia2

        # DAMPING — simula atrito com o campo
        obj1.velocity *= 0.98
        obj2.velocity *= 0.98
        obj1.angular_velocity *= 0.9
        obj2.angular_velocity *= 0.9

    def resolve_collision_with_field(self, obj, mtv, contact_point=None):
        """
        Resolve colisão entre objeto móvel e o campo (estrutura estática de massa infinita).
        :param obj: objeto que colidiu
        :param mtv: vetor mínimo de translação
        """
        obj = obj.reference 
        print(f"(Colisão de um {obj.type_object} com o campo)")

        norm_mtv = np.linalg.norm(mtv)
        if norm_mtv == 0:
            print("MTV nulo — colisão ignorada.")
            return

        normal = mtv / norm_mtv

       # Garante que a MTV está empurrando o objeto para fora do campo
        object_pos = np.array([obj.x, obj.y])
        field_center = np.array([REAL_FIELD_INTERNAL_WIDTH_CM / 2, REAL_FIELD_INTERNAL_HEIGHT_CM / 2])  # ajuste se o campo tiver outro centro
        to_object = object_pos - field_center
        if np.dot(to_object, normal) < 0:
            normal = normal
            mtv = mtv

        # Corrige posição (empurra o objeto para fora do campo)
        obj.x += mtv[0]
        obj.y += mtv[1]
        obj.collision_object.x = obj.x
        obj.collision_object.y = obj.y

        # Verifica componente da velocidade na direção da normal
        if contact_point is None:
            contact_point = object_pos.copy()

        # Velocidade relativa no ponto de contato
        r = contact_point - object_pos 
        vel_at_contact = obj.velocity + obj.angular_velocity * np.array([-r[1],r[0]])

        # Componente na direção normal
        vel_along_normal = np.dot(vel_at_contact, normal)
        if vel_along_normal >= 0 :
            return
        
        type_name = type(obj).__name__
        if 'Ball' in type_name:
            restitution = COEFFICIENT_RESTITUTION_BALL_FIELD
            friction = 0
        elif 'Robot' in type_name:
            restitution = COEFFICIENT_RESTITUTION_ROBOT_FIELD
            friction = COEFICIENT_FRICTION_ROBOT_FIELD
        else:
            restitution = 0.3  # fallback
            friction = 0.05

        # Impulso escalar (restituição + torque)
        rn = np.cross(r, normal)
        obj_inv_mass = 1/obj.mass
        obj_inv_inertia = 1/obj.inertia
        denom = obj_inv_mass + (rn ** 2) * obj_inv_inertia
        j = -(1 + restitution) * vel_along_normal / denom

        impulse = j * normal
        obj.apply_impulse(impulse, contact_point)

        # Atrito (tangente à colisão)
        tangent = np.array([-normal[1], normal[0]])
        vel_tangent = np.dot(vel_at_contact, tangent)

        jt = -vel_tangent / denom
        max_friction = friction * abs(j)
        jt = np.clip(jt, -max_friction, max_friction)

        friction_impulse = jt * tangent
        obj.apply_impulse(friction_impulse, contact_point)
