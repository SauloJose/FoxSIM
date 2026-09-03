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


class GameState(Enum):
    """Estados de controle da partida segundo o protocolo de jogo."""
    HALT = auto()
    STOP = auto()
    GAME_ON = auto()

class Arbitrator:
    '''
    Interface do árbitro da partida.

    O simulador chama ``analyzer`` a cada frame. Este método concentra a
    avaliação das regras e retorna uma decisão para o ciclo da partida.
    Novas regras devem ser adicionadas nos métodos de avaliação/atendimento
    desta classe, sem serem colocadas no loop principal da simulação.
    '''
    def __init__(self, ball: Ball, field: Field, ally_bots: Team, enemy_bots: Team, interface: Interface, timer: Stopwatch):
        # Referências para objetos principais da simulação
        self.ball = ball
        self.field = field
        self.allies = ally_bots
        self.enemies = enemy_bots
        self.interface = interface
        self.timer = timer
        self.enabled = enabled
        self.state = GameState.HALT
        self.last_decision = None
        self.ball_stuck_time = 0.0
        self._last_ball_position = self.ball.position.copy()

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

    def evaluate(self, dt=0.0):
        """Avalia as regras somente quando o árbitro está habilitado."""
        if not self.enabled:
            return None
        return self.analyzer(dt)

    def set_enabled(self, enabled):
        """Liga/desliga a arbitragem para cenários de teste e debug."""
        self.enabled = enabled

    def start_match(self):
        """Autoriza a partida e inicia o cronômetro."""
        if not self.enabled:
            return
        self.state = GameState.GAME_ON
        self.timer.start()

    def reset_match(self):
        """Recoloca o árbitro em HALT e limpa o estado transitório."""
        self.state = GameState.HALT
        self.ball_stuck_time = 0.0
        self._last_ball_position = self.ball.position.copy()
        self.timer.reset()

    def halt(self):
        """Coloca a partida em parada total."""
        self.state = GameState.HALT
        self.timer.pause()
        self._stop_all_robots()

    def stop(self):
        """Interrompe a partida e prepara o afastamento da bola."""
        self.state = GameState.STOP
        self.timer.pause()
        self._stop_all_robots()
        self._separate_robots_from_ball()

    def game_on(self):
        """Retoma o estado de bola em jogo."""
        if self.enabled:
            self.state = GameState.GAME_ON
            self.timer.resume()

    def apply_decision(self, decision):
        """Aplica o posicionamento associado a uma decisão de arbitragem."""
        if decision in (Decisions.FOUL_ALLY, Decisions.FOUL_ENEMY):
            self.prepare_free_kick(decision)
        elif decision in (Decisions.PENALTY_ALLY, Decisions.PENALTY_ENEMY):
            self.prepare_penalty(decision)
        elif decision in (Decisions.GOALKICK_ALLY, Decisions.GOALKICK_ENEMY):
            self.prepare_goal_kick(decision)
        elif decision == Decisions.RESTART:
            self.prepare_kickoff()

    def set_player_pose(self, robot, position, angle):
        """Posiciona um robô usando posição virtual e ângulo em graus."""
        robot.set_position(float(position[0]), float(position[1]))
        robot.angle = np.radians(angle)

    def prepare_kickoff(self, attacking_team=None):
        """Prepara a saída de jogo usando as posições configuradas dos times."""
        self.ball.reset_position()
        self.allies.reset_positions()
        self.enemies.reset_positions()
        if attacking_team is not None:
            team = self.allies if attacking_team == self.allies.team_name else self.enemies
            attacker = team.robots[1]
            direction = 0.0 if team is self.allies else 180.0
            self.set_player_pose(attacker, self.ball.position - np.array([15.0, 0.0]), direction)

    def prepare_free_kick(self, decision):
        """Afasta o time penalizado e orienta os robôs para a cobrança."""
        self.ball.reset_position()
        self.allies.reset_positions()
        self.enemies.reset_positions()
        penalized = self.allies if decision == Decisions.FOUL_ALLY else self.enemies
        self._move_team_away_from_ball(penalized)

    def prepare_goal_kick(self, decision):
        """Reposiciona a bola e os jogadores para um tiro de meta."""
        defending = self.allies if decision == Decisions.GOALKICK_ALLY else self.enemies
        goal_area = self.ally_goal if defending is self.allies else self.enemy_goal
        self.ball.position = (goal_area.x, goal_area.y)
        self.ball.body.velocity = (0.0, 0.0)
        self.allies.reset_positions()
        self.enemies.reset_positions()
        self._move_team_away_from_ball(defending)

    def prepare_penalty(self, decision):
        """Posiciona o cobrador e centraliza o goleiro defensor."""
        attacking = self.allies if decision == Decisions.PENALTY_ALLY else self.enemies
        defending = self.enemies if attacking is self.allies else self.allies
        penalty_position = self.penalty_ally_pos if attacking is self.allies else self.penalty_enemy_pos
        self.ball.position = penalty_position
        self.ball.body.velocity = (0.0, 0.0)
        self.allies.reset_positions()
        self.enemies.reset_positions()
        kicker = attacking.robots[1]
        goal_area = self.ally_goal if defending is self.allies else self.enemy_goal
        goal_position = np.array([goal_area.x, goal_area.y])
        to_goal = np.asarray(goal_position) - self.ball.position
        distance = np.linalg.norm(to_goal)
        direction = to_goal / distance if distance > 1e-6 else np.array([1.0, 0.0])
        self.set_player_pose(kicker, self.ball.position - direction * 12.0,
                             np.degrees(np.arctan2(direction[1], direction[0])))
        goalkeeper = defending.robots[0]
        self.set_player_pose(
            goalkeeper,
            goal_position,
            np.degrees(np.arctan2(-direction[1], -direction[0])),
        )

    def _move_team_away_from_ball(self, team, minimum_distance=20.0):
        """Garante a distância mínima entre a bola e o time penalizado."""
        for robot in team.robots:
            offset = robot.position - self.ball.position
            distance = np.linalg.norm(offset)
            if distance < minimum_distance:
                direction = offset / distance if distance > 1e-6 else np.array([1.0, 0.0])
                self.set_player_pose(robot, self.ball.position + direction * minimum_distance,
                                     np.degrees(np.arctan2(direction[1], direction[0])))

    def _stop_all_robots(self):
        for robot in self.allies.robots + self.enemies.robots:
            robot.stop()

    def _separate_robots_from_ball(self, minimum_distance=20.0):
        """Afasta robôs que estejam dentro da distância mínima da bola."""
        for robot in self.allies.robots + self.enemies.robots:
            offset = robot.position - self.ball.position
            distance = np.linalg.norm(offset)
            if distance >= minimum_distance:
                continue
            direction = offset / distance if distance > 1e-6 else np.array([1.0, 0.0])
            robot.set_position(*(self.ball.position + direction * minimum_distance))

    def analyzer(self, dt=0.0):
        """
        Método principal chamado a cada frame da simulação.
        Verifica eventos do jogo (gol, falta, fim de tempo) e define a decisão.
        """
        if not self.enabled or self.state != GameState.GAME_ON:
            return None

        # Limpa a decisão anterior
        self.current_decision = None

        # Verifica gol
        goal_result = self._is_goal()
        if goal_result is not None:
            self._handle_goal(goal_result)

        # Verifica falta de goleiro (em desenvolvimento)
        if self._check_goalkeeper_foul():
            self._handle_penalty()

        violation = self._check_rule_violations(dt)
        if violation is not None:
            self.current_decision = violation

        # Verifica se a partida acabou
        if self._is_party_end():
            print("[Arbitro]: Partida acabou")
            self._handle_end_of_match()

        return self.get_and_clear_decision()

    def _check_rule_violations(self, dt=0.0):
        """Ponto central para faltas, bola presa e robôs travados."""
        invasion = self._is_line_robot_invasion()
        if invasion is not None and invasion is not False:
            return invasion
        if self._is_ball_stuck(dt):
            return Decisions.RESTART
        decision = self._check_pushing_or_stalled_robot()
        return decision if decision is not False else None

    def _is_line_robot_invasion(self):
        """Detecta dois robôs de linha aliados na própria área de goleiro."""
        for team, area in ((self.allies, self.ally_gk_area), (self.enemies, self.enemy_gk_area)):
            line_robots = [
                robot for robot in team.robots[1:]
                if area.contains(robot.position)
            ]
            if len(line_robots) >= 2:
                return (Decisions.GK_AREA_VIOLATION_ALLY
                    if team is self.allies
                    else Decisions.GK_AREA_VIOLATION_ENEMY)
        return False

    def _is_ball_stuck(self, dt=0.0):
        """Detecta bola praticamente parada por pelo menos cinco segundos."""
        displacement = np.linalg.norm(self.ball.position - self._last_ball_position)
        self._last_ball_position = self.ball.position.copy()
        if displacement < 0.05 and np.linalg.norm(self.ball.velocity) < 1.0:
            self.ball_stuck_time += max(dt, 0.0)
        else:
            self.ball_stuck_time = 0.0
        return self.ball_stuck_time >= 5.0

    def _check_pushing_or_stalled_robot(self):
        """Hook para empurrão, perda de comunicação e robô travado."""
        return None

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
        self.prepare_penalty(self.current_decision)