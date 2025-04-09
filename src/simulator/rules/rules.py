from simulator.objects.ball import * 
from simulator.objects.field import *
from simulator.objects.robot import *
from ui.interface  import Interface
from simulator.objects.timer import *

#Classe do juíz que irá ditar às regras do jogo
class Judger:
    '''
        Representa o arbitro do jogo
    '''
    def __init__(self, ball:Ball, field:Field, ally_bots:list[Robot], enemy_bots:list[Robot], interface:Interface, timer:HighPrecisionTimer):
        #Objetos que serão analisados
        self.ball = ball 
        self.field = field 
        self.allies = ally_bots
        self.enemies = enemy_bots
        self.timer = timer
        self.interface = interface

        #Áreas do campo
        self.enemy_goaL = self.field.goal_area_enemy
        self.ally_goal  = self.field.goal_area_ally

        # Área do goleiro
        self.ally_gk_area  = self.field.goalkeeper_area_ally
        self.enemy_gk_area = self.field.goalkeeper_area_enemy

        # Posições dos goleiros:
        self.pos_gk_enemy = self.field.MED_GK_ENEMY
        self.por_gk_ally = self.field.MED_GK_ALLY

        #Posições para cobranças de penaulti
        self.penalty_ally_pos = self.field_virtual_points['PE2v']
        self.penalty_enemy_pos = self.field_virtual_points['PA2v']
        
        #Pontuação
        self.ally_pontuation  = 0 
        self.enemy_pontuation = 0

        # Pontuação 
        self.pontuation = np.array([0,0],dtype=int)
        self.TIME_OF_A_PARTY = 60   #Segundos
        self.TIMES_OF_PARTY  = 6    



    def _is_Goal(self):
        pass 

    def _penalty(self):
        pass

    def _foult(self):
        pass

    def _is_party_end(self):
        pass 

    def _who_is_winner(self):
        pass
