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
    FINISH = auto()                     # Fim da partida

    ALLY_GOAL = auto()                  # Gol do time aliado
    ENEMY_GOAL = auto()                 # Gol do time adversário

    PENALTY_ALLY = auto()               # Pênalti a favor dos aliados
    PENALTY_ENEMY = auto()              # Pênalti a favor dos inimigos

    FOUL_ALLY = auto()                  # Falta cometida pelos aliados
    FOUL_ENEMY = auto()                 # Falta cometida pelos inimigos
    GK_AREA_VIOLATION_ALLY = auto()     # Invasão da área do goleiro aliado
    GK_AREA_VIOLATION_ENEMY = auto()    # Invasão da área do goleiro adversário

    GOALKICK_ALLY = auto()              # Tiro de meta para os aliados
    GOALKICK_ENEMY = auto()             # Tiro de meta para os inimigos

    DROP_BALL = auto()                  # Bola ao chão (bola presa ou empate de disputa)
    RESTART = auto()                    # Recomeço padrão


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
    def __init__(self, ball: Ball, field: Field, ally_bots: Team, enemy_bots: Team, timer: Stopwatch):
        # Referências para objetos principais da simulação
        self.ball = ball 
        self.field = field 
        self.allies = ally_bots
        self.enemies = enemy_bots
        self.timer = timer

        #Áreas do campo
        self.enemy_goal = self.field.goal_area_enemy
        self.ally_goal  = self.field.goal_area_ally

        # Área do goleiro
        self.ally_gk_area  = self.field.goalkeeper_area_ally
        self.enemy_gk_area = self.field.goalkeeper_area_enemy

        # Posições dos goleiros:
        self.pos_gk_enemy = self.field.MED_GK_ENEMY
        self.pos_gk_ally = self.field.MED_GK_ALLY

        #Posições para cobranças de penaulti
        self.penalty_ally_pos = self.field.virtual_points['PE2v']
        self.penalty_enemy_pos = self.field.virtual_points['PA2v']
        
        #Pontuação
        self.ally_pontuation  = 0 
        self.enemy_pontuation = 0

        #Tempo de cada partida
        self.TIME_OF_A_PARTY = TIMER_PARTY   #Segundos
        self.TIMES_OF_PARTY  = 6  

    def analyzer(self):
        """
        Método principal chamado a cada frame da simulação.
        Ele verifica eventos do jogo (gol, falta, fim de tempo) e define a decisão do árbitro.
        """
        # Limpa a decisão anterior
        self.current_decision = None

        # Verifica gol primeiro
        goal_result = self._is_goal()
        if goal_result is not None:
            self._handle_goal(goal_result)

        # Verifica falta de goleiro (em desenvolvimento)
        if self._check_goalkeeper_foul():
            self._handle_penalty()

        # Verifica se a partida acabou
        if self._is_party_end():
            print("[Arbitro]: Partida acabou")
            self._handle_end_of_match()

        return self.get_and_clear_decision()


    def get_and_clear_decision(self):
        '''
            Consulta segura do árbitro
        '''
        decision = self.current_decision
        self.current_decision = None
        return decision

    def _reset_timer(self):
        '''
            Reseta o temporizador da partida para contar novamente
        '''
        self.timer.reset()
        

    def _is_goal(self):
        """
        Verifica se a bola entrou em um dos gols.
        Retorna 'ALLY' ou 'ENEMY' se houve gol, ou None se não houve.
        """
        if self.ball.is_inside_goal(self.enemy_goal):
            return 'ALLY'
        elif self.ball.is_inside_goal(self.ally_goal):
            return 'ENEMY'
        return None
    
    def _handle_goal(self, side: str):
        '''
            Atribui a pontuação do gol e continua o jogo
        '''
        if side == 'ALLY':
            print("[Arbitro]: Gol do time A!")
            self.ally_pontuation  += 1 
            self.current_decision = Decisions.ALLY_GOAL
        elif side == 'ENEMY':
            print("[Arbitro]: Gol do time B!")
            self.enemy_pontuation += 1
            self.current_decision = Decisions.ENEMY_GOAL

        self._reset_initial_positions()
        


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
        if self.ally_pontuation > self.enemy_pontuation:
            print("Vitória do Time A!")
        elif self.ally_pontuation < self.enemy_pontuation:
            print("Vitória do Time B!")
        else:
            print("Empate!")

    def _check_goalkeeper_foul(self):
        """
        Verifica se algum robô inimigo entrou na área do goleiro aliado.
        Pode ser usado para marcar penalidades.
        """
        return False 


    def _handle_end_of_match(self):
        '''
        Tarefa para final da partida
        '''
        self._who_is_winner()
        self.current_decision = Decisions.FINISH

        # Zera pontuações
        self.ally_pontuation = 0
        self.enemy_pontuation = 0
        self.interface.score = [self.ally_pontuation,self.enemy_pontuation]

        # Reseta posições iniciais
        self._reset_initial_positions()

        # Reseta o timer
        self._reset_timer()

    def _handle_penalty(self):
        '''
        O que ele irá fazer em caso de penalti
        '''
        print("[Arbitro]: Penalidade marcada!")
        self.current_decision = Decisions.PENALTY_ENEMY  # ou PENALTY_ALLY
        # Posiciona bola no ponto de penalidade, trava bots etc.

    def _finish_game(self):
        '''
            Método para finalizar e analisar o time vencedor da partida,
        '''
        pass 


