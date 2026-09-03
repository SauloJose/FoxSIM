import pygame
import numpy as np
import pymunk
from ui.interface_config import *

class RectHelper:
    """Auxiliar para áreas retangulares não físicas (gol, goleiro, etc.)."""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains(self, point):
        """Verifica se um ponto (x, y) está dentro do retângulo."""
        px, py = point
        return (self.x - self.width/2 <= px <= self.x + self.width/2 and
                self.y - self.height/2 <= py <= self.y + self.height/2)

class Field:
    def __init__(self, space, width=REAL_FIELD_INTERNAL_WIDTH_CM, height=REAL_FIELD_INTERNAL_HEIGHT_CM, color=(0, 0, 0)):
        """
        Inicializa o campo com Pymunk.
        :param space: espaço Pymunk compartilhado
        :param width, height: dimensões (cm)
        :param color: cor (apenas para referência)
        """
        self.space = space
        self.width = width
        self.height = height
        self.color = color
        self.type_object = FIELD_OBJECT
        self.velocity = np.array([0,0])

        # Dicionário de pontos virtuais (constantes do config)
        self.virtual_points = {
            "PA1v": PA1v, "PA2v": PA2v, "PA3v": PA3v,
            "PE1v": PE1v, "PE2v": PE2v, "PE3v": PE3v,
            "GA1v": GA1v, "GA2v": GA2v, "GA3v": GA3v, "GA4v": GA4v,
            "GAI1v": GAI1v, "GAI2v": GAI2v, "GAI3v": GAI3v, "GAI4v": GAI4v,
            "GE1v": GE1v, "GE2v": GE2v, "GE3v": GE3v, "GE4v": GE4v,
            "GEI1v": GEI1v, "GEI2v": GEI2v, "GEI3v": GEI3v, "GEI4v": GEI4v,
            "fieldP12v": fieldP12v, "fieldP34v": fieldP34v,
            "fieldEx1": fieldEx1, "fieldEx2": fieldEx2,
            "fieldEx3": fieldEx3, "fieldEx4": fieldEx4,
            "fieldC": fieldC,
            "Q1A1v": Q1A1v, "Q1A2v": Q1A2v,
            "Q2A1v": Q2A1v, "Q2A2v": Q2A2v,
            "Q3A1v": Q3A1v, "Q3A2v": Q3A2v,
            "Q4A1v": Q4A1v, "Q4A2v": Q4A2v,
        }

        vp = self.virtual_points
        thickness = THICKNESS
        dim_vertice = DIM_VERTICES

        # --- Criação dos objetos estáticos (paredes e vértices) com Pymunk ---
        self._create_static_walls(vp, thickness, dim_vertice)

        # --- Áreas especiais (não físicas, para lógica de jogo) ---
        self._create_special_areas(vp)

        self.MED_GK_ALLY = (vp["GA1v"] + vp["GA3v"]) / 2
        self.MED_GK_ENEMY = (vp["GE1v"] + vp["GE3v"]) / 2

    def _create_static_walls(self, vp, thickness, dim_vertice):
        """Cria corpos estáticos para as paredes e vértices."""
        line_pairs = [
            (vp["Q1A1v"], vp["Q1A2v"]),
            (vp["Q1A2v"], vp["Q2A1v"]),
            (vp["Q2A1v"], vp["Q2A2v"]),
            (vp["Q2A2v"], vp["GEI1v"]),
            (vp["GEI1v"], vp["GEI2v"]),
            (vp["GEI2v"], vp["GEI3v"]),
            (vp["GEI3v"], vp["GEI4v"]),
            (vp["GEI4v"], vp["Q3A1v"]),
            (vp["Q3A1v"], vp["Q3A2v"]),
            (vp["Q3A2v"], vp["Q4A1v"]),
            (vp["Q4A1v"], vp["Q4A2v"]),
            (vp["Q4A2v"], vp["GAI3v"]),
            (vp["GAI3v"], vp["GAI4v"]),
            (vp["GAI4v"], vp["GAI1v"]),
            (vp["GAI1v"], vp["GAI2v"]),
            (vp["GAI2v"], vp["Q1A1v"]),
        ]

        static_body = pymunk.Body(body_type=pymunk.Body.STATIC)

        # === ADICIONE O CORPO AO ESPAÇO PRIMEIRO ===
        self.space.add(static_body)

        # Agora adicione as shapes que usam esse corpo
        for p1, p2 in line_pairs:
            seg = pymunk.Segment(static_body, tuple(p1), tuple(p2), thickness)
            seg.friction = 0.5
            seg.elasticity = 0.1
            seg.collision_type = 2
            self.space.add(seg)

        # Círculos nos vértices
        vertex_points = [
            vp["Q1A1v"], vp["Q1A2v"], vp["Q2A1v"], vp["Q2A2v"],
            vp["Q3A1v"], vp["Q3A2v"], vp["Q4A1v"], vp["Q4A2v"],
            vp["GEI1v"], vp["GEI2v"], vp["GEI3v"], vp["GEI4v"],
            vp["GAI1v"], vp["GAI2v"], vp["GAI3v"], vp["GAI4v"],
        ]
        for pt in vertex_points:
            circle = pymunk.Circle(static_body, dim_vertice, offset=tuple(pt))
            circle.friction = 0.5
            circle.elasticity = 0.1
            self.space.add(circle)

    def _create_special_areas(self, vp):
        """Cria áreas auxiliares (gol, goleiro, retângulo de colocação)."""
        # Retângulo de colocação da bola (RectUtil)
        field_c = vp["fieldC"]
        w = (vp["fieldEx2"][0] - vp["fieldEx1"][0]) - 7
        h = (vp["fieldEx2"][1] - vp["fieldEx3"][1]) - 7
        self.RectUtil = RectHelper(field_c[0], field_c[1], w, h)

        # Área de gol aliado
        med_ally = (vp["GAI1v"] + vp["GAI3v"]) / 2
        w_ally = (vp["GAI2v"] - vp["GAI1v"])[0]
        h_ally = (vp["GAI2v"] - vp["GAI3v"])[1]
        self.goal_area_ally = RectHelper(med_ally[0], med_ally[1], w_ally, h_ally)

        # Área de gol inimigo
        med_enemy = (vp["GEI1v"] + vp["GEI3v"]) / 2
        w_enemy = (vp["GEI2v"] - vp["GEI1v"])[0]
        h_enemy = (vp["GEI2v"] - vp["GEI3v"])[1]
        self.goal_area_enemy = RectHelper(med_enemy[0], med_enemy[1], w_enemy, h_enemy)

        # Área do goleiro aliado
        med_gk_ally = (vp["GA1v"] + vp["GA3v"]) / 2
        w_gk_ally = (vp["GA2v"] - vp["GA1v"])[0]
        h_gk_ally = (vp["GA2v"] - vp["GA3v"])[1]
        self.goalkeeper_area_ally = RectHelper(med_gk_ally[0], med_gk_ally[1], w_gk_ally, h_gk_ally)

        # Área do goleiro inimigo
        med_gk_enemy = (vp["GE1v"] + vp["GE3v"]) / 2
        w_gk_enemy = (vp["GE2v"] - vp["GE1v"])[0]
        h_gk_enemy = (vp["GE2v"] - vp["GE3v"])[1]
        self.goalkeeper_area_enemy = RectHelper(med_gk_enemy[0], med_gk_enemy[1], w_gk_enemy, h_gk_enemy)

    # Método auxiliar (não mais usado, mantido para compatibilidade)
    def line_to_thin_rectangle(self, p1, p2, thickness=1, reference=None, type_object=STRUCTURE_OBJECTS):
        """Não utilizado com Pymunk; mantido para evitar quebra de código."""
        pass