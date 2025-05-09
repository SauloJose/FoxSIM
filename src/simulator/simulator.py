#Definição da classe simulator
from simulator.collision.collision import *
from simulator.objects.field import Field
from simulator.objects.ball import Ball 
from simulator.objects.robot import Robot 
from simulator.objects.team import Team
from simulator.rules.rules  import *
from ui.interface_config    import *
from simulator.game_logic   import *
from ui.pages.objects.SimWidget import *

import numpy as np
from PyQt6.QtCore import QTimer

class SimulatorVariables:
    '''
        Classe para encapsular as variáveis da simulação.
    '''
    def __init__(self):
        pass




class Simulator:
    '''
        Classe para encapsular a lógica da simulação e controlar o loop de tempo/desenho.
    '''
    def __init__(self, page_parent,screen: SimulatorWidget, FPS: int =60):
        '''
        Inicializa o simulador do jogo com os parâmetros fornecidos.

        :param page_parent (BasicPage): Página pai que contém o simulador.

        :param screen (SimulatorWidget): Tela que o simulador utilizará para desenhar os objetos.

        :param FPS (int): Taxa de quadros por segundo (frames per second).

        '''
        self.screen = screen  # Tela que o simulador utilizará para desenhar os objetos
        self.page_parent = page_parent
        self.fps = FPS
        self.timer = QTimer()
        self.timer.timeout.connect(self._main_loop)
        self.running = False
        self.paused = False

        # Estados da simulação
        self.simulation_started = False
        self.is_simulation_paused = False

        # Variáveis de desenho para a interface 
        self.draw_collision_objects = False
        self.draw_grid_collision = False

        # Variáveis dos objetos da simulação
        self.allies:    Team  = None 
        self.enemies:   Team  = None 
        self.ball:      Ball  = None 
        self.field:     Field = None

        # Objeto que representa os robôs
        self.robots:   list = []

        # Cronômetro e física
        self.cronometer = Stopwatch(60)
        self.Physics_Engine = Physics(
            allies=self.allies,
            enemies=self.enemies,
            ball=self.ball,
            dt=1.0/self.fps,
            field=self.field,
            screen=self.screen
        )

        # Objeto que representa o árbitro do jogo
        self.arbitrator = Arbitrator(self.ball, self.field, self.allies, self.enemies, self.screen, self.cronometer)

    # =============================|GETTERS E SETTERS|============================
    def set_FPS(self, fps):
        '''
            Método responsável por definir a taxa de quadros por segundo (FPS) do simulador.
        '''
        self.fps = max(1, int(fps))
        self.timer.setInterval(int(1000 / self.fps))
        if self.Physics_Engine:
            self.Physics_Engine.dt = 1.0 / self.fps

    def set_cronometer(self, time_limit: int):
        '''
            Método responsável por definir o cronômetro do simulador.

            :param time_limit (int): Limite de tempo da partida em segundos.
        '''
        self.cronometer.set_duration = time_limit

    def start(self):
        '''
            Método responsável por iniciar a simulação.
        '''
        if not self.running:
            self.running = True
            self.paused = False
            self.simulation_started = True
            self.timer.start(int(1000 / self.fps))

    def pause(self):
        '''
            Método responsável por pausar a simulação.
        '''
        if self.running and not self.paused:
            self.paused = True
            self.timer.stop()

    def resume(self):
        '''
            Método responsável por retomar a simulação após uma pausa.  
        '''
        if self.running and self.paused:
            self.paused = False
            self.timer.start(int(1000 / self.fps))

    def stop(self):
        '''
            Método responsável por parar a simulação.
        '''
        self.running = False
        self.paused = False
        self.simulation_started = False
        self.timer.stop()

    def reset(self):
        '''
            Método responsável por reiniciar a simulação.   
        '''
        self.stop()
        self.get_variables_simulation()
        self.create_objects()
        self.cronometer = Stopwatch(60)
        self.Physics_Engine = Physics(
            allies=self.allies,
            enemies=self.enemies,
            ball=self.ball,
            dt=1.0/self.fps,
            field=self.field,
            screen=self.screen
        )
        self.arbitrator = Arbitrator(self.ball, self.field, self.allies, self.enemies, self.screen, self.cronometer)
        self.screen.update_widget()
    
    # =============================|FUNÇÕES PRINCIPAIS|============================
    def _main_loop(self):
        '''
            Loop Principal do simulador 
        '''
        if not self.running or self.paused:
            return
        self.update()
        self.draw()

    # Função para escolher qual a forma de controle dos robôs será utilizada
    def set_control_function(self, control_function):
        '''
            Método responsável por definir a função de controle do robô.

            :param control_function (function): Função de controle a ser atribuída ao robô.
        '''
        self.control_function = control_function
    # ============================================================================
    # =============================|FUNÇÕES AUXILIARES|============================
    def update(self):
        '''
            Método responsável por atualizar a lógica do jogo.
        '''
        # Atualiza física e lógica do jogo
        if self.Physics_Engine:
            self.Physics_Engine.update()

        # Verifica situação do jogo 
        if self.arbitrator and self.arbitrator.analyzer() == Decisions.FINISH:
            self.simulation_started = False
            self.reset()

    def get_arbitrator_decision(self):
        '''
            Método responsável por obter a decisão do árbitro.
        '''
        if self.arbitrator:
            return self.arbitrator.analyzer()
        return None
    
    # Método responsável por obter as variáveis da simulação na tela configurada
    def draw(self):
        '''
            Método responsável por desenhar os objetos na tela.
        '''
        # Limpa o backbuffer
        self.screen.back_buffer.clear()

        # Desenha robôs
        if self.allies:
            for bot in self.allies.robots:
                bot.draw(self.screen)
        if self.enemies:
            for bot in self.enemies.robots:
                bot.draw(self.screen)
        # Desenha bola
        if self.ball:
            self.ball.draw(self.screen)
        # Desenhos de debug
        if self.draw_collision_objects and self.Physics_Engine:
            s = 1
        if self.draw_grid_collision and self.Physics_Engine:
            s = 1
        # Atualiza o widget
        self.screen.update_widget()

    # =============================|FUNÇÕES DE CONFIGURAÇÃO|============================
    def set_variables_simulation(self, variables: SimulatorVariables):
        '''
            Método responsável por definir as variáveis da simulação.'''
        # Puxe variáveis da interface/configuração aqui
        pass

    def create_objects(self):
        '''
            Método responsável por criar os objetos da simulação no modo padrão.
        '''
        # Cria times, robôs, bola, campo, etc na posição inicial correta
        pass

    def create_bot(self, x, y, team: Team, bot_id: int, bot_type: str, initial_angle: float = 0.0):
        '''
            Método responsável por criar um robô e adicioná-lo ao time.

            :param x (float): Posição x inicial do robô.

            :param y (float): Posição y inicial do robô.

            :param team (Team): O time ao qual o robô será adicionado.

            :param bot_id (int): ID do robô a ser criado.

            :param bot_type (str): Tipo do robô a ser criado.

            :param initial_angle (float): Ângulo inicial do robô.
        '''
        Robot()
        pass 
    
    def create_ball(self, ball_id: int, ball_type: str):
        '''
            Método responsável por criar uma bola.

            :param ball_id (int): ID da bola a ser criada.

            :param ball_type (str): Tipo da bola a ser criada.
        '''
        if ball_id and ball_type:
            self.ball = Ball(ball_id, ball_type)
            return self.ball
        return None
    
    # =============================|FUNÇÕES DE CONTROLE|============================
    # Método para liberar recursos quando fechar a página do simulador
    def destroy(self):
        '''
            Método responsável por liberar os recursos utilizados pelo simulador.
        '''
        self.stop()

    # Métodos extras para controle externo
    def is_running(self):
        '''
            Método responsável por verificar se a simulação está em execução.
        '''
        return self.running and not self.paused

    def is_paused(self):
        '''
            Método responsável por verificar se a simulação está pausada.
        '''
        return self.paused

    def is_started(self):
        '''
            Método responsável por verificar se a simulação foi iniciada.
        '''
        return self.simulation_started