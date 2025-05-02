#Definição da classe simulator
from simulator.collision.collision import *
from simulator.objects.field import Field
from simulator.objects.ball import Ball 
from simulator.objects.robot import Robot 
from simulator.objects.team import Team
from simulator.rules.rules  import *
from ui.interface_config    import *
from simulator.game_logic   import *
from ui.pages.objects.openGLWidgets import *

import numpy as np

class Simulator:
    '''
        Classe para encapsular a lógica da simulação
    '''
    def __init__(self, screen: GL2DWidget):
        # === Inicializando variáveis do simulador para realizar o necessário
        # == Screen (Superfície que será utilizada para renderizar)
        self.screen = screen 
    
        # == Flags
        # Variáveis de estado da simulação
        self.running                = False 
        self.is_simulation_paused   = False 
        self.simulation_started     = False

        # Variáveis de desenho para a interface 
        self.draw_collision_objects = False
        self.draw_grid_collision    = False 

        # Variáveis que vem da interface do simulador
        self.ball_init_pos = np.array([0,0],dtype=float)


        # Timer do simulador utilizando o Core do PyQt
        self.timer = QElapsedTimer()
        self.timer.start()
        self.last_time = 0.0

        # === Parâmetros físicos do simulador
        # Robô:



        # Bola: 


        # Coeficientes de atrito e restituição:



        #Tempo de partida
        


        # == Inicializando variáveis dos objetos da simulação
        self.allies:    Team  = None 
        self.enemies:   Team  = None 
        self.ball:      Ball  = None 
        self.field:     Field = None

        #
        #Carrega variáveis da simulação
        self.get_variables_simulation() 
        
        # === Cria os objetos do simulador
        self.create_objects()   

        # === Criando um cronometro
        cronometer = Stopwatch(60)

        # === Cria a Engine de física do simulador
        self.Physics_Engine = Physics(allies=self.allies,enemies=self.enemies,ball=self.ball,dt=1.0/FPS,field=self.field,screen=self.screen)
        
        # === Cria o Árbitro do jogo
        self.arbitrator = Arbitrator(self.ball, self.field, self.allies, self.enemies, screen, cronometer)
        
        # === Puxa o endreço do widget para ele
        
    def start(self):
        '''
            Inicializa a simulação
        '''

    def stop(self):
        '''
            Finaliza a simulação
        '''

    def update(self):
        '''
            Atualiza situação da simulação
        '''
        # Atualiza 
        self.Physics_Engine.update()

        # O Árbitro analisa a situação do game
        if self.arbitrator.analyzer() == Decisions.FINISH:
            self.simulation_started = False 
            self.reset_simulation()


    def draw(self):
        '''
            Método para desenhar os objetos na superfície, dada as circunstâncias
        '''
        # Desenha o campo na screen


        # Desenha robôs da simulação


        # Desenha bola da simulação 


        # Desenhos opicionais de depuração através de Flags

        pass 

    
    def get_variables_simulation(self):
        '''
            Puxa variáveis da interface para dar início ao simulador
            garantindo que a simulação ocorra da forma que foi configurada
        '''
        pass 

    def create_objects(self):
        '''
            Construindo os objetos da simulação para tratar as variáveis corretamente
        '''
        ## Crio robôs da simulação


        ## Crio times da simulação 
        # Time aliado

        # Time inimigo

        ## Crio objeto Bola da simulação


        ## Crio objeto do campo na simulação



    def reset_simulation(self, timer: Stopwatch):
        '''
            Reposiciona objetos para reiniciar simulação
        '''
        pass

    def pause_simulation(self):
        '''
            Pausa a simulação através da flag
        '''
        pass 