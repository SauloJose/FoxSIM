import pygame
from simulator.collision.collision import *
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
            "fieldC": fieldC, #Atribuindo quinas do campo
            "Q1A1v": Q1A1v,
            "Q1A2v": Q1A2v,
            "Q2A1v": Q2A1v,
            "Q2A2v": Q2A2v,
            "Q3A1v": Q3A1v,
            "Q3A2v": Q3A2v,
            "Q4A1v": Q4A1v,
            "Q4A2v": Q4A2v,
        }

        vp = self.virtual_points # Apenas para deixar mais simples a escrita.
        
        dim_vertice = 1.5

        # Objetos de colisão (linhas e áreas do campo)
        self.collision_object = CollisionGroup([
            self.line_to_thin_rectangle(Q1A1v, Q1A2v, 1, reference=self, type_object=STRUCTURE_OBJECTS),
            self.line_to_thin_rectangle(Q1A2v, Q2A1v, 1, reference=self, type_object=STRUCTURE_OBJECTS), 
            self.line_to_thin_rectangle(Q2A1v, Q2A2v, 1, reference=self, type_object=STRUCTURE_OBJECTS), 
            self.line_to_thin_rectangle(Q2A2v, GEI1v, 1, reference=self, type_object=STRUCTURE_OBJECTS), 
            self.line_to_thin_rectangle(GEI1v, GEI2v, 1, reference=self, type_object=STRUCTURE_OBJECTS), 
            self.line_to_thin_rectangle(GEI2v, GEI3v, 1, reference=self, type_object=STRUCTURE_OBJECTS),
            self.line_to_thin_rectangle(GEI3v, GEI4v, 1, reference=self, type_object=STRUCTURE_OBJECTS), 
            self.line_to_thin_rectangle(GEI4v, Q3A1v, 1, reference=self, type_object=STRUCTURE_OBJECTS),
            self.line_to_thin_rectangle(Q3A1v, Q3A2v, 1, reference=self, type_object=STRUCTURE_OBJECTS),
            self.line_to_thin_rectangle(Q3A2v, Q4A1v, 1, reference=self, type_object=STRUCTURE_OBJECTS),
            self.line_to_thin_rectangle(Q4A1v, Q4A2v, 1, reference=self, type_object=STRUCTURE_OBJECTS),
            self.line_to_thin_rectangle(Q4A2v, GAI3v, 1, reference=self, type_object=STRUCTURE_OBJECTS),
            self.line_to_thin_rectangle(GAI3v, GAI4v, 1, reference=self, type_object=STRUCTURE_OBJECTS),
            self.line_to_thin_rectangle(GAI4v, GAI1v, 1, reference=self, type_object=STRUCTURE_OBJECTS),
            self.line_to_thin_rectangle(GAI1v, GAI2v, 1, reference=self, type_object=STRUCTURE_OBJECTS),
            self.line_to_thin_rectangle(GAI2v, Q1A1v, 1, reference=self, type_object=STRUCTURE_OBJECTS),  #Adicionando os pontos de colisão 
            CollisionCircle(Q1A1v[0],Q1A1v[1],dim_vertice,type_object=STRUCTURE_OBJECTS, reference=self),
            CollisionCircle(Q1A2v[0],Q1A2v[1],dim_vertice,type_object=STRUCTURE_OBJECTS, reference=self),
            CollisionCircle(Q2A1v[0],Q2A1v[1],dim_vertice,type_object=STRUCTURE_OBJECTS, reference=self),
            CollisionCircle(Q2A2v[0],Q2A2v[1],dim_vertice,type_object=STRUCTURE_OBJECTS, reference=self),
            CollisionCircle(Q3A1v[0],Q3A1v[1],dim_vertice,type_object=STRUCTURE_OBJECTS, reference=self),
            CollisionCircle(Q3A2v[0],Q3A2v[1],dim_vertice,type_object=STRUCTURE_OBJECTS, reference=self),
            CollisionCircle(Q4A1v[0],Q4A1v[1],dim_vertice,type_object=STRUCTURE_OBJECTS, reference=self),
            CollisionCircle(Q4A2v[0],Q4A2v[1],dim_vertice,type_object=STRUCTURE_OBJECTS, reference=self),

            CollisionCircle(GEI1v[0],GEI1v[1],dim_vertice,type_object=STRUCTURE_OBJECTS, reference=self),
            CollisionCircle(GEI2v[0],GEI2v[1],dim_vertice,type_object=STRUCTURE_OBJECTS, reference=self),
            CollisionCircle(GEI3v[0],GEI3v[1],dim_vertice,type_object=STRUCTURE_OBJECTS, reference=self),
            CollisionCircle(GEI4v[0],GEI4v[1],dim_vertice,type_object=STRUCTURE_OBJECTS, reference=self),
            
            CollisionCircle(GAI1v[0],GAI1v[1],dim_vertice,type_object=STRUCTURE_OBJECTS, reference=self),
            CollisionCircle(GAI2v[0],GAI2v[1],dim_vertice,type_object=STRUCTURE_OBJECTS, reference=self),
            CollisionCircle(GAI3v[0],GAI3v[1],dim_vertice,type_object=STRUCTURE_OBJECTS, reference=self),
            CollisionCircle(GAI4v[0],GAI4v[1],dim_vertice,type_object=STRUCTURE_OBJECTS, reference=self),

        ], type_object=STRUCTURE_OBJECTS, reference=self)

        # --- Objetos especiais para detecção
        print("\n[Sistema]: Criando áreas do campo")

        # Área onde a bola pode ser colocada com o mouse
        print("[Sistema]: - RectUtil")
        self.RectUtil = CollisionRectangle(
            vp["fieldC"][0], vp["fieldC"][1],
            (vp["fieldEx2"][0] - vp["fieldEx1"][0])-7,
            (vp["fieldEx2"][1] - vp["fieldEx3"][1])-7,
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
        print("[Sistema]: - AREA DO GOLEIRO INIMIGO")
        self.goalkeeper_area_enemy = CollisionRectangle(
            self.MED_GK_ENEMY[0], self.MED_GK_ENEMY[1],
            (vp["GE2v"] - vp["GE1v"])[0],
            (vp["GE2v"] - vp["GE3v"])[1],
            type_object=GOALKEEPER_AREA_OBJECT_ENEMY,
            reference=self
        )

    def line_to_thin_rectangle(self, p1, p2, thickness=1, reference=None, type_object=STRUCTURE_OBJECTS):
        '''
            Método necessário para ajustar o bug que acontece com as paredes do campo.
        '''
        # Centro do retângulo
        center = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        # Comprimento da linha
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = np.sqrt(dx**2 + dy**2)
        # Ângulo em graus
        angle = np.degrees(np.arctan2(dy, dx))
        
        return CollisionRectangle(center[0],center[1], length, thickness, angle=angle, reference=reference, type_object=type_object)