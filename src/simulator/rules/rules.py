from simulator.objects.ball import * 
from simulator.objects.field import *
from simulator.objects.robot import *
from simulator.objects.team  import * 

from ui.interface import Interface
from simulator.objects.timer import *
from ui.interface_config import *

from enum import Enum, auto


#Posições 
class BasicPositions:
    '''
        Posições básicas para que o Arbitro posicione os jogadores quando for necessário
    '''
    def __init__(self):
        self.GOALP = None 

# Possíveis decisões do Árbitro
class Decisions(Enum):
    '''
    Enum que representa as decisões possíveis tomadas pelo Árbitro no VSSS (IEEE Rules).
    '''
    FINISH = auto()
    ALLY_GOAL = auto()
    ENEMY_GOAL = auto()
    PENALTY_ALLY = auto()
    PENALTY_ENEMY = auto()
    FOUL_ALLY = auto()
    FOUL_ENEMY = auto()
    GK_AREA_VIOLATION_ALLY = auto()
    GK_AREA_VIOLATION_ENEMY = auto()
    THROW_IN_ALLY = auto()
    THROW_IN_ENEMY = auto()
    CORNER_ALLY = auto()
    CORNER_ENEMY = auto()
    GOALKICK_ALLY = auto()
    GOALKICK_ENEMY = auto()
    DROP_BALL = auto()
    RESTART = auto()

class Arbitrator:
    '''
    Classe que representa o árbitro da partida, que irá garantir as regras
    da partida.
    '''
    def __init__(self, ball: Ball, field: Field, ally_bots: Team, enemy_bots: Team,
                 interface: Interface, timer: Stopwatch):
        # Referências para objetos principais da simulação
        self.ball = ball
        self.field = field
        self.allies = ally_bots
        self.enemies = enemy_bots
        self.interface = interface
        self.timer = timer

        # Áreas do campo (agora são RectHelper com método contains)
        self.enemy_goal = self.field.goal_area_enemy
        self.ally_goal = self.field.goal_area_ally

        # Área do goleiro
        self.ally_gk_area = self.field.goalkeeper_area_ally
        self.enemy_gk_area = self.field.goalkeeper_area_enemy

        # Posições dos goleiros (centro das áreas)
        self.pos_gk_enemy = self.field.MED_GK_ENEMY
        self.pos_gk_ally = self.field.MED_GK_ALLY

        # Posições para cobranças de pênalti
        self.penalty_ally_pos = self.field.virtual_points['PE2v']
        self.penalty_enemy_pos = self.field.virtual_points['PA2v']

        # Pontuação
        self.ally_pontuation = 0
        self.enemy_pontuation = 0
        self.pontuation = self.interface.score

        # Tempo de cada partida
        self.TIME_OF_A_PARTY = TIMER_PARTY   # Segundos
        self.TIMES_OF_PARTY = 6

        # Decisão atual (usada internamente)
        self.current_decision = None

    def analyzer(self):
        """
        Método principal chamado a cada frame da simulação.
        Verifica eventos do jogo (gol, falta, fim de tempo) e define a decisão.
        """
        # Limpa a decisão anterior
        self.current_decision = None

        # Verifica gol
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
        Consulta segura do árbitro: retorna a decisão atual e a limpa.
        '''
        decision = self.current_decision
        self.current_decision = None
        return decision

    def _reset_timer(self):
        '''Reseta o temporizador da partida.'''
        self.timer.reset()

    def _is_goal(self):
        """
        Verifica se a bola entrou em um dos gols.
        Retorna 'ALLY' se gol no gol inimigo, 'ENEMY' se gol no gol aliado, ou None.
        """
        # Usa o método is_inside_goal da bola, que recebe um objeto com método contains
        if self.ball.is_inside_goal(self.enemy_goal):
            return 'ALLY'
        elif self.ball.is_inside_goal(self.ally_goal):
            return 'ENEMY'
        return None

    def _handle_goal(self, side: str):
        '''
        Atribui a pontuação do gol e reinicia o jogo.
        '''
        if side == 'ALLY':
            print("[Arbitro]: Gol do time A!")
            self.ally_pontuation += 1
            self.interface.update_score(1)   # assumindo que update_score(1) incrementa aliados
            self.current_decision = Decisions.ALLY_GOAL
        elif side == 'ENEMY':
            print("[Arbitro]: Gol do time B!")
            self.enemy_pontuation += 1
            self.interface.update_score(2)   # time adversário
            self.current_decision = Decisions.ENEMY_GOAL

        self._reset_initial_positions()

    def _reset_initial_positions(self):
        """
        Reposiciona a bola no meio do campo e todos os robôs nas posições iniciais.
        """
        self.ball.reset_position()
        self.enemies.reset_positions()
        self.allies.reset_positions()

    def _is_party_end(self):
        """Verifica se o tempo da partida acabou."""
        return self.timer.is_finished()

    def _who_is_winner(self):
        """Exibe o vencedor com base no placar atual."""
        if self.ally_pontuation > self.enemy_pontuation:
            print("Vitória do Time A!")
        elif self.ally_pontuation < self.enemy_pontuation:
            print("Vitória do Time B!")
        else:
            print("Empate!")

    def _check_goalkeeper_foul(self):
        """
        Verifica se algum robô inimigo entrou na área do goleiro aliado.
        (Implementação futura)
        """
        # Exemplo: usar self.ally_gk_area.contains(posicao_do_robo)
        return False

    def _handle_end_of_match(self):
        '''
        Tarefa para final da partida: anuncia vencedor, zera pontuações, reseta posições e timer.
        '''
        self._who_is_winner()
        self.current_decision = Decisions.FINISH

        # Zera pontuações
        self.ally_pontuation = 0
        self.enemy_pontuation = 0
        self.interface.score = [self.ally_pontuation, self.enemy_pontuation]

        # Reseta posições iniciais
        self._reset_initial_positions()

        # Reseta o timer
        self._reset_timer()

    def _handle_penalty(self):
        '''
        O que fazer em caso de pênalti.
        '''
        print("[Arbitro]: Penalidade marcada!")
        self.current_decision = Decisions.PENALTY_ENEMY  # ou PENALTY_ALLY
        # Posiciona bola no ponto de penalidade, trava bots etc.