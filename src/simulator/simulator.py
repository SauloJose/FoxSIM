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
from data.objects.logs import *
from simulator.intelligence.core.interface import *
from simulator.simUtils import *
from PyQt6.QtCore import QTimer


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
        self.log_manager = page_parent.log_manager # Puxo o manager de logs da página pai
        self.fps = FPS
        self.timer = QTimer()
        self.timer.timeout.connect(self._main_loop)


        # Estados da simulação
        self.is_simulation_started  = False # Verifica se a simulação foi iniciada
        self.is_simulation_running  = False # Verifica se a simulação está rodando
        self.is_simulation_paused   = False # Informa se a simulação foi pausada
        self.is_simulation_stop     = False # Verifica se a simulação chegou ao fim
        # started -> running -> stop
        #          |  (Loop)  ^
        #          |   stop   |

        # Variáveis de desenho para a interface 
        self.draw_collision_objects = False
        self.draw_grid_collision    = False
        self.draw_trajectory_robots = False 

        #Variáveis de simulação física
        ## Parâmetros de exibição
        self.FPS: int 
        self.party_time: int
        self.vel_sim: int 
        
        ## Parâmetros de física
        # robôs
        self.robot_length: float 
        self.robot_mass: float 
        self.robot_max_speed: int 
        self.robot_max_ang_speed: int 
        self.robot_wheels_distance: float 
        self.robot_wheels_radius: float 

        # bola 
        self.ball_radius: float 
        self.ball_mass: float 
        self.ball_max_speed: int 
        
        # coeficientes de atrito
        self.fric_rr: float 
        self.fric_rf: float 
        self.fric_bw: float 
        self.fric_br: float 

        # coeficientes de restituição
        self.rest_rb: float 
        self.rest_rr: float
        self.rest_bf: float 

        ## Habilitar debug visual
        self.visual_debug: bool 

        ## Habilitar logs do sistema
        self.has_logs: bool

        ## Parâmetros de controle 
        # PID para distancia
        self.PID_dist_kp: float 
        self.PID_dist_ki: float
        self.PID_dist_kd: float 

        # PID para angulo
        self.PID_angle_kp: float 
        self.PID_angle_ki: float 
        self.PID_angle_kd: float 
        
        #PID para angulo final
        self.PID_final_angle_kp: float 
        self.PID_final_angle_ki: float 
        self.PID_final_angle_kd: float 

        # Classe para controle de variáveis externas
        self.extern_variables = SimulatorVariables()

        # Variáveis dos objetos da simulação
        self.allies:    Team  = None 
        self.enemies:   Team  = None 
        self.ball:      Ball  = None 
        self.field:     Field = None

        # Objeto que representa todos robôs
        self.bots = self.allies.robots + self.enemies.robots

        # Objeto que irá servir como interface de controle
        self._control_strategy: ControlInterface = None 

    # =============================|GETTERS E SETTERS|==============================
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
            Método responsável por iniciar a simulação quando o evento de iniciar for capturado
        '''
        if not self.is_simulation_running:
            self.is_simulation_started= True
            self.is_simulation_paused  = False
            self.simulation_started = True
            self.timer.start(int(1000 / self.fps))

    def pause(self):
        '''
            Método responsável por pausar a simulação.
        '''
        if self.is_simulation_started and not self.is_simulation_paused :
            self.is_simulation_paused  = True
            self.timer.stop()

    def resume(self):
        '''
            Método responsável por retomar a simulação após uma pausa.  
        '''
        if self.is_simulation_started and self.is_simulation_paused :
            self.is_simulation_paused  = False
            self.timer.start(int(1000 / self.fps))

    def stop(self):
        '''
            Método responsável por parar a simulação quando a partida for finalizada
        '''
        self.is_simulation_started= False
        self.is_simulation_paused  = False
        self.simulation_started = False
        self.timer.stop()

    def reset(self):
        '''
            Método responsável por reiniciar a simulação quando o evento de reset for chamado
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
        self.screen.flip()
    
    def get_variables_simulation(self):
        # Puxa as variáveis do arquivo
        has_error, msg = self.extern_variables.load_all_configs()
        if has_error:
            self.log(message = msg, type=LogType.ERROR) 

    # =============================|FUNÇÕES PRINCIPAIS|============================
    def _main_loop(self):
        '''
            Loop Principal do simulador 
        '''
        if not self.is_simulation_started or self.is_simulation_paused :
            return
        self.update()
        self.draw()

    # Função para escolher qual a forma de controle dos robôs será utilizada
    def set_control_strategy(self, strategy: ControlInterface):
        '''
            Método responsável por definir a função de controle do robô.

            :param control_function (function): Função de controle a ser atribuída ao robô.
        '''
        self._control_strategy = strategy


    def update(self):
        '''
            Método responsável por atualizar a lógica do jogo.
        '''
        try:
            # Aciona a interface de controle


            # Atualiza física e lógica do jogo
            if self.Physics_Engine:
                self.Physics_Engine.update()

            # Verifica situação do jogo 
            if self.arbitrator and self.arbitrator.analyzer() == Decisions.FINISH:
                self.simulation_started = False
                self.reset()

        except Exception as e :
            self.log(type=LogType.CRITICAL, message = f"Erro ao atualizar o simulador:\n {e}")
        
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
            Método responsável por desenhar os objetos na tela por meio do objeto
            SimulatorWidget().
        '''
        try:
            # Limpa o backbuffer
            self.screen.back_buffer.clear()

            # Desenha robôs
            if self.allies and self.enemies:
                for bot in self.allies.robots + self.enemies.robots:
                    bot._draw_(screen=self.screen)
            # Desenha bola
            if self.ball:
                self.ball._draw_(self.screen)

            if self.Physics_Engine and self.screen:
                # Desenhos de debug
                if self.draw_collision_objects:
                    s = 1
                if self.draw_grid_collision:
                    s = 1
                if self.draw_trajectory_robots:
                    s = 1
        except Exception as e:
            self.log(type=LogType.CRITICAL, message = f"Erro crítico ao tentar desenhar:\n {e}")
        finally:
            # Atualiza o widget no final do desenho.
            self.screen.flip()
    def update_info_bots(self):
        '''
            Atualiza os status da interface
        '''
    
    def update_info_simulation(self):
        '''
            Atualiza os dados do jogo no widget que for passado
        '''
    # =============================|Construtores|============================
    def set_variables_simulation(self, variables: SimulatorVariables):
        '''
            Método responsável por definir as variáveis da simulação.'''
        # Puxe variáveis da interface/configuração aqui
        ## Parâmetros de exibição
        self.FPS = variables.FPS 
        self.party_time = variables.party_time 
        self.vel_sim = variables.vel_sim  
        
        ## Parâmetros de física
        # robôs
        self.robot_length = variables.robot_length
        self.robot_max = variables.robot_max
        self.robot_max_speed = variables.robot_max_speed
        self.robot_max_ang_speed = variables.robot_max_ang_speed
        self.robot_wheels_distance = variables.robot_wheels_distance
        self.robot_wheels_radius =  variables.robot_wheels_radius

        # bola 
        self.ball_radius = variables.ball_radius
        self.ball_mass =variables.ball_mass
        self.ball_max_speed =variables.ball_max_speed
        
        # coeficientes de atrito
        self.fric_rr =variables.fric_rr
        self.fric_rf =variables.fric_rf
        self.fric_bw =variables.fric_bw
        self.fric_br =variables.fric_br

        # coeficientes de restituição
        self.rest_rb =variables.rest_rb
        self.rest_rr =variables.rest_rr
        self.rest_bf =variables.rest_bf

        ## Habilitar debug visual
        self.visual_debug = variables.visual_debug

        ## Habilitar logs do sistema
        self.has_logs =variables.has_logs

        ## Parâmetros de controle 
        # PID para distancia
        self.PID_dist_kp =variables.PID_dist_kp
        self.PID_dist_ki =variables.PID_dist_ki
        self.PID_dist_kd =variables.PID_dist_kd

        # PID para angulo
        self.PID_angle_kp = variables.PID_angle_kp
        self.PID_angle_ki = variables.PID_angle_ki
        self.PID_angle_kd = variables.PID_angle_kd
        
        #PID para angulo final
        self.PID_final_angle_kp = variables.PID_final_angle_kp
        self.PID_final_angle_ki = variables.PID_final_angle_ki
        self.PID_final_angle_kd = variables.PID_final_angle_kd

    def set_environment_simulation(self):
        """
            Método para carregar nos locais corretos os valores que foram configurados.
        """

    def create_objects(self):
        '''
            Método responsável por criar os objetos da simulação no modo padrão.
        '''
        # Cria times, robôs, bola, campo, etc na posição inicial correta
        

        # Cria cronômetro


        # Cria objeto de física e aplica as variáveis 


        # Cria o árbitro 

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
        bot = Robot()


    
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
        return self.is_simulation_started and not self.is_simulation_paused 

    def is_paused(self):
        '''
            Método responsável por verificar se a simulação está pausada.
        '''
        return self.is_simulation_paused 

    def is_started(self):
        '''
            Método responsável por verificar se a simulação foi iniciada.
        '''
        return self.simulation_started
    

    # ================================ | Método para Log | ===========================
    def log(self, message: str, type: LogType = LogType.INFO, system: LogSystem = LogSystem.SIMULATION, priority: LogPriority = LogPriority.MEDIUM):
        if self.log_manager:
            self.log_manager.add_log(Log(type, priority, message, system))