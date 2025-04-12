from simulator.objects.ball import * 
from simulator.objects.field import *
from simulator.objects.robot import *
from simulator.objects.team  import * 

from ui.interface import Interface
from simulator.objects.timer import *
from ui.interface_config import *

from enum import Enum, auto

# Possíveis decisões do Árbitro
class Decisions(Enum):
    '''
    Enum que representa as decisões possíveis tomadas pelo Árbitro no VSSS (IEEE Rules).
    '''
    FINISH = auto()              # Fim da partida

    ALLY_GOAL = auto()           # Gol do time aliado
    ENEMY_GOAL = auto()          # Gol do time adversário

    PENALTY_ALLY = auto()        # Pênalti a favor dos aliados
    PENALTY_ENEMY = auto()       # Pênalti a favor dos inimigos

    FOUL_ALLY = auto()           # Falta cometida pelos aliados
    FOUL_ENEMY = auto()          # Falta cometida pelos inimigos
    GK_AREA_VIOLATION_ALLY = auto()   # Invasão da área do goleiro aliado
    GK_AREA_VIOLATION_ENEMY = auto()  # Invasão da área do goleiro adversário

    THROW_IN_ALLY = auto()       # Lateral a favor dos aliados
    THROW_IN_ENEMY = auto()      # Lateral a favor dos inimigos

    CORNER_ALLY = auto()         # Escanteio a favor dos aliados
    CORNER_ENEMY = auto()        # Escanteio a favor dos inimigos

    GOALKICK_ALLY = auto()       # Tiro de meta para os aliados
    GOALKICK_ENEMY = auto()      # Tiro de meta para os inimigos

    DROP_BALL = auto()           # Bola ao chão (bola presa ou empate de disputa)
    RESTART = auto()             # Recomeço padrão


#Posições 
class BasicPositions:
    '''
        Posições básicas para que o Arbitro posicione os jogadores quando for necessário
    '''
    def __init__(self):
        self.GOALP = None 

#Classe do Arbitro
class Arbitrator:
    '''
        Classe que representa o árbitro da partida, que irá garantir as regras
        da partida
    '''
    def __init__(self, ball: Ball, field: Field, ally_bots: Team, enemy_bots: Team, interface: Interface, timer: HighPrecisionTimer):
        # Referências para objetos principais da simulação
        self.ball = ball 
        self.field = field 
        self.allies = ally_bots
        self.enemies = enemy_bots
        self.interface = interface
        self.timer = timer

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
        self.pontuation = np.array([0,0],dtype=int)

        #Tempo de cada partida
        self.TIME_OF_A_PARTY = TIMER_PARTY   #Segundos
        self.TIMES_OF_PARTY  = 6  

    def analyzer(self):
        """
        Método principal chamado a cada frame da simulação.
        Ele verifica se houve gol, falta, ou se a partida terminou.
        """
        #Verifica se teve gol
        if self._is_goal():
            self._reset_initial_positions()
            self._reset_timer()
            return 0

        if self._is_party_end():
            return 1
        
        '''if self._check_goalkeeper_foul():
            self._handle_penalty()

        if self._is_party_end():
            self._who_is_winner()
            self.pontuation[:] = 0
            self.interface.update_score(0)  # Zera o placar visual
            self._reset_positions()
            self.timer.start()  # Começa nova partida'''

    def _reset_timer(self):
        '''
            Reseta o temporizador da partida para contar novamente
        '''
        self.timer.stop()
        self.timer = HighPrecisionTimer(TIMER_PARTY)

    def _is_goal(self):
        """
        Verifica se a bola entrou em um dos gols.
        Atualiza o placar e a interface se necessário.
        """
        if self.ball.is_inside_goal(self.enemy_goaL):
            "[Arbitro]: Gol do time A"
            self.pontuation[0] += 1
            self.interface.update_score(1)  # Atualiza placar dos aliados
            return True
        elif self.ball.is_inside_goal(self.ally_goal):
            "[Arbitro]: Gol do time B"
            self.pontuation[1] += 1
            self.interface.update_score(2)  # Atualiza placar dos inimigos
            return True
        return False

    def _reset_initial_positions(self):
        """
        Reposiciona a bola no meio do campo e todos os robôs
        nas posições iniciais configuradas.
        """
        # Reseta posição da bola
        self.ball.reset_position()

        #Reseto as posições dos robôs para o começo da partida
        self.enemies.reset_positions()
        self.allies.reset_positions()

    def _is_party_end(self):
        """
        Verifica se o tempo da partida acabou.
        """
        return self.timer.is_finished()

    def _who_is_winner(self):
        """
        Exibe o vencedor com base no placar atual ao final da partida.
        """
        if self.pontuation[0] > self.pontuation[1]:
            print("Vitória dos aliados!")
        elif self.pontuation[1] > self.pontuation[0]:
            print("Vitória dos inimigos!")
        else:
            print("Empate!")

    def _check_goalkeeper_foul(self):
        """
        Verifica se algum robô inimigo entrou na área do goleiro aliado.
        Pode ser usado para marcar penalidades.
        """
        pass 

    def _handle_penalty(self):
        """
        Executa as penalidades aplicáveis, como reset da bola
        em ponto de pênalti e parada de todos os robôs.
        """
        pass

    def _finish_game(self):
        '''
            Método para finalizar e analisar o time vencedor da partida,
        '''
        pass 


