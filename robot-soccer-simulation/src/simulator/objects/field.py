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
    
        self.collision_objects = []          #Lista utilizada apenas no draw() para fins gráficos 
        
        # Lista de pontos virtuais que limitam o campo
        self.virtual_points = {
            "PA1v": np.array([210, 137]),
            "PA2v": np.array([210, 257]),
            "PA3v": np.array([210, 377]),
            "PE1v": np.array([435, 137]),
            "PE2v": np.array([435, 257]),
            "PE3v": np.array([435, 377]),
            "GA1v": np.array([97, 152]),
            "GA2v": np.array([142, 152]),
            "GA3v": np.array([142, 362]),
            "GA4v": np.array([97, 362]),
            "GAI1v": np.array([67, 197]),
            "GAI2v": np.array([97, 197]),
            "GAI3v": np.array([97, 317]),
            "GAI4v": np.array([67, 317]),
            "GE1v": np.array([502, 152]),
            "GE2v": np.array([547, 152]),
            "GE3v": np.array([547, 362]),
            "GE4v": np.array([502, 362]),
            "GEI1v": np.array([547, 197]),
            "GEI2v": np.array([577, 197]),
            "GEI3v": np.array([577, 317]),
            "GEI4v": np.array([547, 317]),
            "fieldP12v": np.array([322, 62]),
            "fieldP34v": np.array([322, 452]),
            "fieldEx1": np.array([97,62]),
            "fieldEx2": np.array([547,62]),
            "fieldEx3": np.array([547,452]),
            "fieldEx4": np.array([97,452]),
            "fieldC": np.array([322, 257])  
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
        # Área onde a bola pode ser colocada com o mouse
        self.RectUtil = CollisionRectangle(
            vp["fieldC"][0], vp["fieldC"][1],
            vp["fieldEx2"][0] - vp["fieldEx1"][0],
            vp["fieldEx3"][1] - vp["fieldEx2"][1],
            type_object=POSSIBLE_BOAL_PUT_OBJECT,
            reference=self
        )

        # Áreas de gol (colisão real para lógica de pontuação)
        self.MED_ALLY = (vp["GAI1v"] + vp["GAI3v"]) / 2
        self.goal_area_ally = CollisionRectangle(
            self.MED_ALLY[0], self.MED_ALLY[1],
            (vp["GAI2v"] - vp["GAI1v"])[0],
            (vp["GAI3v"] - vp["GAI2v"])[1],
            type_object=ALLY_GOAL_OBJECT,
            reference=self
        )

        self.MED_ENEMY = (vp["GEI1v"] + vp["GEI3v"]) / 2
        self.goal_area_enemy = CollisionRectangle(
            self.MED_ENEMY[0], self.MED_ENEMY[1],
            (vp["GEI2v"] - vp["GEI1v"])[0],
            (vp["GEI3v"] - vp["GEI2v"])[1],
            type_object=ENEMY_GOAL_OBJECT,
            reference=self
        )

        # Áreas do goleiro (zona restrita)
        self.MED_GK_ALLY = (vp["GA1v"] + vp["GA3v"]) / 2
        self.goalkeeper_area_ally = CollisionRectangle(
            self.MED_GK_ALLY[0], self.MED_GK_ALLY[1],
            (vp["GA2v"] - vp["GA1v"])[0],
            (vp["GA3v"] - vp["GA2v"])[1],
            type_object=GOALKEEPER_AREA_OBJECT_ALLY,
            reference=self
        )

        self.MED_GK_ENEMY = (vp["GE1v"] + vp["GE3v"]) / 2
        self.goalkeeper_area_enemy = CollisionRectangle(
            self.MED_GK_ENEMY[0], self.MED_GK_ENEMY[1],
            (vp["GE2v"] - vp["GE1v"])[0],
            (vp["GE3v"] - vp["GE2v"])[1],
            type_object=GOALKEEPER_AREA_OBJECT_ENEMY,
            reference=self
        )