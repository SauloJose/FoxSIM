from simulator.objects.ball import * 
from simulator.objects.field import *
from simulator.objects.robot import *
from ui.interface import Interface
from simulator.objects.timer import *
from ui.interface_config import *

class Arbitrator:
    '''
        Representa o árbitro do jogo
    '''
    def __init__(self, ball: Ball, field: Field, ally_bots: list[Robot], enemy_bots: list[Robot], interface: Interface, timer: HighPrecisionTimer):
        '''
            Agente responsável por dar sentido ao jogo, verificando se ocorreu gol, falta e mandando os jogadores realizarem ações.
        '''
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
        self.penalty_ally_pos = self.field.virtual_points['PE2v']
        self.penalty_enemy_pos = self.field.virtual_points['PA2v']
        
        #Pontuação
        self.ally_pontuation  = 0 
        self.enemy_pontuation = 0

        # Pontuação 
        self.pontuation = np.array([0,0],dtype=int)
        self.TIME_OF_A_PARTY = 60   #Segundos
        self.TIMES_OF_PARTY  = 6    



    def _is_goal(self):
        ''' Verifica se ocorreu algum gol'''
        # Gol no time inimigo → ponto para aliados
        if self.ball.is_inside_goal(self.enemy_goaL):
            self.score[0] += 1
            self.interface.update_score(1)  # Time A
            return True

        # Gol no time aliado → ponto para inimigos
        if self.ball.is_inside_goal(self.ally_goal):

            self.score[1] += 1
            self.interface.update_score(2)  # Time B
            return True

        return False

    def _reset_positions(self):
        '''
            Reseta as posições dos objetos do jogo
        '''
        self.ball.reset_position(*self.ball_reset_position)

        for bot, pos in zip(self.allies, self.ally_reset_positions):
            bot.set_position(*pos)
            bot.stop()

        for bot, pos in zip(self.enemies, self.enemy_reset_positions):
            bot.set_position(*pos)
            bot.stop()

    def _is_party_end(self):
        '''
            Verifica quem ganhou a partida
        '''
        return self.timer.elapsed() >= self.TIME_OF_A_PARTY


    def _who_is_winner(self):
        ''' Analisa o Score da partida e define um campeão'''
        if self.score[0] > self.score[1]:
            pass
        elif self.score[1] > self.score[0]:
            pass
        else:
            pass

    def analyzer(self):
        '''
            Analisador principal da partida
        '''
        if self._is_goal():
            self._reset_positions()

        if self._is_party_end():
            self._who_is_winner()
            self.timer.reset()
            self.score[:] = 0
            self.interface.score[:] = 0
            self._reset_positions()
