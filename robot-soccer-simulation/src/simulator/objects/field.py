import pygame
from simulator.objects.collision import *
from ui.interface_config import *

class Field:
    def __init__(self, width=REAL_FIELD_INTERNAL_WIDTH_CM, height=REAL_FIELD_INTERNAL_HEIGHT_CM, color=(0, 0, 0)):
        """
        Inicializa o campo de jogo.
        :param width: Largura do campo em pixels.
        :param height: Altura do campo em pixels.
        :param color: Cor do campo (RGB).
        """
        self.width = width
        self.height = height
        self.color = color
        self.type_object = FIELD_OBJECT

        print(f"[Sistema]: Campo criado com w = {self.width}, h = {self.height} e do tipo {self.type_object}")
        self.collision_objects = []          #Lista utilizada apenas no draw() para fins gráficos 
        
        # Lista de pontos virtuais que limitam o campo
        self.virtual_points = {
            "PA1v": PA1v,
            "PA2v": PA2v,
            "PA3v": PA3v,
            "PE1v": PE1v,
            "PE2v": PE2v,
            "PE3v": PE3v,
            "GA1v": GA1v,
            "GA2v": GA2v,
            "GA3v": GA3v,
            "GA4v": GA4v,
            "GAI1v": GAI1v,
            "GAI2v": GAI2v,
            "GAI3v": GAI3v,
            "GAI4v": GAI4v,
            "GE1v": GE1v,
            "GE2v": GE2v,
            "GE3v": GE3v,
            "GE4v": GE4v,
            "GEI1v": GEI1v,
            "GEI2v": GEI2v,
            "GEI3v": GEI3v,
            "GEI4v": GEI4v,
            "fieldP12v": fieldP12v,
            "fieldP34v": fieldP34v,
            "fieldEx1": fieldEx1,
            "fieldEx2": fieldEx2,
            "fieldEx3": fieldEx3,
            "fieldEx4": fieldEx4,
            "fieldC": fieldC
        }

        vp = self.virtual_points # Apenas para deixar mais simples a escrita.

        # Objetos de colisão (linhas e áreas do campo)
        self.collision_object = CollisionGroup([
            CollisionLine(fieldEx1, fieldEx2,reference=self, type_object=STRUCTURE_OBJECTS), 
            CollisionLine(fieldEx2, GEI1v,reference=self, type_object=STRUCTURE_OBJECTS), 
            CollisionLine(GEI1v, GEI2v,reference=self, type_object=STRUCTURE_OBJECTS), 
            CollisionLine(GEI2v, GEI3v,reference=self, type_object=STRUCTURE_OBJECTS),
            CollisionLine(GEI3v, GEI4v,reference=self, type_object=STRUCTURE_OBJECTS), 
            CollisionLine(GEI4v, fieldEx3,reference=self, type_object=STRUCTURE_OBJECTS),
            CollisionLine(fieldEx3, fieldEx4,reference=self, type_object=STRUCTURE_OBJECTS),
            CollisionLine(fieldEx4, GAI3v,reference=self, type_object=STRUCTURE_OBJECTS),
            CollisionLine(GAI3v, GAI4v,reference=self, type_object=STRUCTURE_OBJECTS),
            CollisionLine(GAI4v, GAI1v,reference=self, type_object=STRUCTURE_OBJECTS),
            CollisionLine(GAI1v, GAI2v,reference=self, type_object=STRUCTURE_OBJECTS),
            CollisionLine(GAI2v, fieldEx1,reference=self, type_object=STRUCTURE_OBJECTS)
            ], type_object=STRUCTURE_OBJECTS,reference=self)

        # --- Objetos especiais para detecção
        print("\n[Sistema]: Criando áreas do campo")
        # Área onde a bola pode ser colocada com o mouse
        print("[Sistema]: - RectUtil")
        self.RectUtil = CollisionRectangle(
            vp["fieldC"][0], vp["fieldC"][1],
            vp["fieldEx2"][0] - vp["fieldEx1"][0],
            vp["fieldEx2"][1] - vp["fieldEx3"][1],
            type_object=POSSIBLE_BOAL_PUT_OBJECT,
            reference=self
        )

        # Áreas de gol (colisão real para lógica de pontuação)
        self.MED_ALLY = (vp["GAI1v"] + vp["GAI3v"]) / 2
        print("\n[Sistema]: - AREA DO GOL ALIADO INTERNA")
        self.goal_area_ally = CollisionRectangle(
            self.MED_ALLY[0], self.MED_ALLY[1],
            (vp["GAI2v"] - vp["GAI1v"])[0],
            (vp["GAI2v"] - vp["GAI3v"])[1],
            type_object=ALLY_GOAL_OBJECT,
            reference=self
        )

        self.MED_ENEMY = (vp["GEI1v"] + vp["GEI3v"]) / 2
        print("\n[Sistema]: - AREA DO GOL INIMIGO INTERNA")
        self.goal_area_enemy = CollisionRectangle(
            self.MED_ENEMY[0], self.MED_ENEMY[1],
            (vp["GEI2v"] - vp["GEI1v"])[0],
            (vp["GEI2v"] - vp["GEI3v"])[1],
            type_object=ENEMY_GOAL_OBJECT,
            reference=self
        )

        # Áreas do goleiro (zona restrita)
        self.MED_GK_ALLY = (vp["GA1v"] + vp["GA3v"]) / 2
        print("\n[Sistema]: - AREA DO GOLEIRO ALIADO")
        self.goalkeeper_area_ally = CollisionRectangle(
            self.MED_GK_ALLY[0], self.MED_GK_ALLY[1],
            (vp["GA2v"] - vp["GA1v"])[0],
            (vp["GA2v"] - vp["GA3v"])[1],
            type_object=GOALKEEPER_AREA_OBJECT_ALLY,
            reference=self
        )

        self.MED_GK_ENEMY = (vp["GE1v"] + vp["GE3v"]) / 2
        print("\n[Sistema]: - AREA DO GOLEIRO INIMIGO")
        self.goalkeeper_area_enemy = CollisionRectangle(
            self.MED_GK_ENEMY[0], self.MED_GK_ENEMY[1],
            (vp["GE2v"] - vp["GE1v"])[0],
            (vp["GE2v"] - vp["GE3v"])[1],
            type_object=GOALKEEPER_AREA_OBJECT_ENEMY,
            reference=self
        )