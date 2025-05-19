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
from PyQt6.QtCore import QTimer, QThread, pyqtSignal,QMutex

class SimulationThread(QThread):
    updated = pyqtSignal() #Sinal para avisar que o frame foi atualizado
    finished_cleanly = pyqtSignal() #Sinal para avisar que a limpeza foi concluída
    def __init__(self, simulator, fps=60):
        super().__init__()
        self.simulator = simulator 
        self.fps = fps 
        self.running = False 

    def run(self):
        self.running = True
        while self.running:
            start_time = time.time()
            self.simulator._main_loop()
            self.updated.emit()
            elapsed = time.time() - start_time 
            dt = max(1.0/self.fps - elapsed, 0)
            time.sleep(dt)
    
    def stop(self):
        self.running = False 
        self.finished_cleanly.emit()
        self.wait()

    def set_FPS(self, fps):
        self.fps = fps 


class Simulator:
    '''
        Classe para encapsular a lógica da simulação e controlar o loop de tempo/desenho.
    '''
    def __init__(self, page_parent, screen: SimulatorWidget, FPS: int =60):
        '''
        Inicializa o simulador do jogo com os parâmetros fornecidos.

        :param page_parent (BasicPage): Página pai que contém o simulador.

        :param screen (SimulatorWidget): Tela que o simulador utilizará para desenhar os objetos.

        :param FPS (int): Taxa de quadros por segundo (frames per second).

        '''
        #Variáveis manipulativas do simulador
        self.screen = screen  # Tela que o simulador utilizará para desenhar os objetos
        self.page_parent = page_parent
        self.log_manager = page_parent.log_manager # Puxo o manager de logs da página pai
        self.fps = int(FPS)
        
        # Criando thread de simulação
        self.sim_thread = SimulationThread(self)
        self.sim_thread.updated.connect(self._handle_draw_safe)

        # Adicionando um QMutex
        self.draw_mutex = QMutex()

        # Estados da simulação
        self.is_simulation_started  = False # Verifica se a simulação foi iniciada
        self.is_simulation_running  = False # Verifica se a simulação está rodando
        self.is_simulation_paused   = False # Informa se a simulação foi pausada
        self.is_simulation_stop     = False # Verifica se a simulação chegou ao fim
        # started -> running -> stop
        #          |  (Loop)  ^
        #          |   stop   |
        #          |__________|

        # Variáveis de desenho para a interface 
        self.draw_collision_objects = False
        self.draw_grid_collision    = False
        self.draw_trajectory_robots = False 

        #Variáveis de simulação física
        ## Parâmetros de exibição
        self.FPS: int = 60
        self.party_time: int = 60
        self.vel_sim: int = 1
        
        ## Parâmetros de física
        # robôs
        self.robot_length: float = 8.0 
        self.robot_mass: float = 1.0
        self.robot_max_speed: int  = 20
        self.robot_max_ang_speed: int =25
        self.robot_wheels_distance: float  = 8.0
        self.robot_wheels_radius: float = 6.0

        # bola 
        self.ball_radius: float = 2.135
        self.ball_mass: float =0.045
        self.ball_max_speed: int = 95
        
        # coeficientes de atrito
        self.fric_rr: float = 0.01
        self.fric_rf: float = 0.92
        self.fric_bw: float = 0.58
        self.fric_br: float = 0.95

        # coeficientes de restituição
        self.rest_rb: float = 0.95
        self.rest_rr: float = 0.6
        self.rest_bf: float = 0.8

        ## Habilitar debug visual
        self.visual_debug: bool = False

        ## Habilitar logs do sistema
        self.has_logs: bool = True

        ## Parâmetros de controle 
        # PID para distancia
        self.PID_dist_kp: float = 6.0
        self.PID_dist_ki: float = 0.0
        self.PID_dist_kd: float = 0.5

        # PID para angulo
        self.PID_angle_kp: float = 4.0
        self.PID_angle_ki: float = 0.1
        self.PID_angle_kd: float = 0.1
        
        #PID para angulo final
        self.PID_final_angle_kp: float = 1.0 
        self.PID_final_angle_ki: float = 0.5
        self.PID_final_angle_kd: float = -0.5

        # Classe para controle de variáveis externas
        self.extern_variables = SimulatorVariables()

        # Variáveis dos objetos da simulação
        self.blue_team:    Team  = None 
        self.red_team:   Team  = None 
        self.ball:      Ball  = None 
        self.field:     Field = None

        # Objeto que representa todos robôs
        self.bots = None

        # Objeto que irá servir como interface de controle
        self._control_strategy: ControlInterface = None 

        # Informações da simul
        # ação
        self.score = [0,0]
        self.timer_count = 60
        self.timer = Stopwatch(60)
        

    # =============================|GETTERS E SETTERS|==============================
    def set_FPS(self, fps):
        '''
            Método responsável por definir a taxa de quadros por segundo (FPS) do simulador.
        '''
        self.fps = max(1, int(fps))
        self.sim_thread.set_FPS(fps)
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
            self.is_simulation_running = True 
            self.sim_thread.start()

    def pause(self):
        '''
            Método responsável por pausar a simulação.
        '''
        if self.is_simulation_started and not self.is_simulation_paused :
            self.is_simulation_paused  = True
        
        if hasattr(self,'sim_thread'):
            self.sim_thread.stop()


    def resume(self):
        '''
            Método responsável por retomar a simulação após uma pausa.  
        '''
        if self.is_simulation_started and self.is_simulation_paused :
            self.is_simulation_paused  = False
        
        if hasattr(self,'sim_thread'):
            self.sim_thread.start()


    def stop(self):
        '''
            Método responsável por parar a simulação quando a partida for finalizada
        '''
        self.is_simulation_started= False
        self.is_simulation_paused  = False
        self.is_simulation_running = False 

        if hasattr(self,'sim_thread'):
            self.sim_thread.stop()

    def reset(self):
        '''
            Método responsável por reiniciar a simulação quando o evento de reset for chamado
        '''
        self.stop()
        self.get_variables_simulation()
        self.create_default_objects()
        self.cronometer = Stopwatch(60)
        self.Physics_Engine = Physics(
            allies=self.blue_team,
            enemies=self.red_team,
            ball=self.ball,
            dt=1.0/self.fps,
            field=self.field,
            screen=self.screen
        )
        self.arbitrator = Arbitrator(self.ball, self.field, self.blue_team, self.red_team, self.cronometer)
        self.screen.flip()
    
    def get_variables_simulation(self):
        # Puxa as variáveis do arquivo
        has_error, msg = self.extern_variables.load_all_configs()
        if has_error:
            self.log(message = msg, type=LogType.ERROR) 

    # Funções para setar o placar

    # Método para setar os valores dos robôs 

    # Método para puxar valores do controle de visualização
    # =============================|FUNÇÕES PRINCIPAIS|============================
    def _main_loop(self):
        '''
            Loop Principal do simulador 
        '''
        if not self.is_simulation_started or self.is_simulation_paused :
            return
        self.update()

    # Função para escolher qual a forma de controle dos robôs será utilizada
    def set_control_strategy(self, strategy: ControlInterface):
        '''
            Método responsável por definir a função de controle do robô.

            :param control_function (function): Função de controle a ser atribuída ao robô.
        '''
        self._control_strategy = strategy


    def update(self):
        '''Atualiza a lógica do jogo.'''
        if not self.is_simulation_started or self.is_simulation_paused:
            return
        try:
            if self._control_strategy:
                self._control_strategy.execute()  # Executa estratégia de controle
            if hasattr(self, 'Physics_Engine'):
                self.Physics_Engine.update()
            if hasattr(self, 'arbitrator'):
                decision = self.arbitrator.analyzer()
                if decision == Decisions.FINISH:
                    self.stop()
        except Exception as e:
            self.log(
                message=f"Erro crítico no update: {str(e)}",
                type=LogType.CRITICAL,
                priority=LogPriority.HIGH
            )
            self.stop()  # Força parada segura

    def get_arbitrator_decision(self):
        '''
            Método responsável por obter a decisão do árbitro.
        '''
        if self.arbitrator:
            return self.arbitrator.analyzer()
        return None
    
    # Método responsável por obter as variáveis da simulação na tela configurada
    def draw(self):
        '''Desenha os objetos na tela.'''
        self.draw_mutex.lock()

        if not hasattr(self, 'screen') or not self.screen:
            self.log(
                message="Tela não inicializada. Não é possível desenhar.",
                type=LogType.ERROR,
                priority=LogPriority.HIGH
            )
            return
        try:
            self.screen.back_buffer.clear()

            #Envia comandos para o backbuffer2D para organizar as chamadas
            if hasattr(self, 'ball'):
                self.ball._draw_(self.screen)
            
            if hasattr(self, 'blue_team') and hasattr(self, 'red_team'):
                for bot in self.blue_team.robots + self.red_team.robots:
                    bot._draw_(self.screen)

            # Debug visual (se habilitado)
            if self.visual_debug:
                if self.draw_collision_objects:
                    self.draw_collision()
                if self.draw_grid_collision:
                    self.draw_grid()
                if self.draw_trajectory_robots:
                    self.draw_trajectory()
            
            # Desenha esses valores no backbuffer (QPixmap)
            self.screen.render_frame()

        except Exception as e:
            self.log(
                message=f"Falha ao desenhar: {str(e)}",
                type=LogType.CRITICAL,
                priority=LogPriority.HIGH
            )
            self.stop()
        finally:
            #Passa o backbuffer para o frontbuffer e exibe na tela o desenho
            self.screen.flip()
            self.draw_mutex.unlock()

    def _handle_draw_safe(self):
        '''Desenha de forma segura no widget'''
        if not self.is_simulation_started or self.is_simulation_paused:
            self.screen.set_render_paused(True)
            return
        
        self.screen.set_render_paused(False)
        self.draw()

    def draw_collision(self):
        '''
            Desenha objetos de colisão
        '''

    def draw_grid(self):
        '''
            Desenha grade de verificação de colisão
        '''

    def draw_trajectory(self):
        '''
            Desenha a trajetória dos robôs 
        '''

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

        # Configuro o ambiente 
        self.set_environment_simulation(variables=variables)


    def set_environment_simulation(self, variables: SimulatorVariables):
        """
            Método para carregar nos locais corretos os valores que foram configurados.
        """
        # Atribui as variáveis na engine de física
        self.Physics_Engine.collision_manager.set_environment_var(variables)

        # Atribui variáveis no controle dos robôs



    def create_default_objects(self):
        '''
            Método responsável por criar os objetos da simulação no modo padrão.
        '''
        ## Cria times, robôs, bola, campo, etc na posição inicial correta
        # Crio o campo
        self.field = Field()

        # Crio os times 
        self.blue_team = Team(blue_team_positions, TeamNames.BLUE_TEAM, initial_angle=0)
        self.red_team = Team(red_team_positions, TeamNames.RED_TEAM, initial_angle=180)

        # Dando uma forma de acessar diretamente os robôs numa lista
        self.bots = self.blue_team.robots + self.red_team.robots

        # Cria a bola
        self.ball= Ball(XVBALL_INIT, YVBALL_INIT, self.field, radius=self.ball_radius)

        ## Cria arbitro e cronômetro
        # Cria o árbitro
        self.arbitrator = Arbitrator(self.ball, self.field, self.blue_team, self.red_team,self.timer)

        ## Cria objeto de física e aplica as variáveis 
        # Crio o motor de física 
        self.Physics_Engine = Physics(allies=self.blue_team, enemies=self.red_team, ball =self.ball, dt=1.0/self.FPS, field = self.field, screen=self.screen)

        # Desenha de forma segura os objetos
        self._handle_draw_safe()
    
    # =============================|FUNÇÕES DE CONTROLE|============================
    # Método para liberar recursos quando fechar a página do simulador
    def destroy(self):
        '''Libera recursos do simulador de forma segura'''
        try:
            # 1. Para a simulação se estiver rodando
            self.stop()
            
            # 2. Encerra a thread de simulação se estiver ativa
            if hasattr(self, 'sim_thread') and self.sim_thread.isRunning():
                self.sim_thread.stop()  # Chama o método stop() da thread
                self.sim_thread.wait(2000)  # Espera até 2 segundos para finalização
                
                # Verifica se a thread realmente parou
                if self.sim_thread.isRunning():
                    self.log(
                        message="Thread de simulação não respondeu ao encerramento",
                        type=LogType.WARNING,
                        priority=LogPriority.HIGH
                    )
                    self.sim_thread.terminate()  # Força encerramento se necessário
                
            # Limpa buffers da tela se necessário
            if hasattr(self, 'screen'):
                self.screen.cleanup()
                
        except Exception as e:
            self.log(
                message=f"Erro durante destruição do simulador: {str(e)}",
                type=LogType.CRITICAL,
                priority=LogPriority.HIGH
            )

    # Métodos extras para controle externo
    def is_running(self):
        return self.sim_thread.isRunning() and not self.is_simulation_paused
    
    def is_paused(self):
        '''
            Método responsável por verificar se a simulação está pausada.
        '''
        return self.is_simulation_paused 

    def is_started(self):
        '''
            Método responsável por verificar se a simulação foi iniciada.
        '''
        return self.is_simulation_started
    

    # ================================ | Método para Log | ===========================
    def log(self, message: str, type: LogType = LogType.INFO, system: LogSystem = LogSystem.SIMULATION, priority: LogPriority = LogPriority.MEDIUM):
        if self.log_manager:
            self.log_manager.add_log(Log(type, priority, message, system))