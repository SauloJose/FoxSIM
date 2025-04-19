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
        # == Flags
        # Variáveis de estado da simulação
        self.running                = False 
        self.is_simulation_paused   = False 
        self.simulation_started     = False

        # Variáveis de desenho para a interface 
        self.draw_collision_objects = False
        self.draw_grid_collision    = False 

        # Variáveis que vem da interface do simulador
        
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

        # === Cria a Engine de física do simulador
        self.Physics_Engine = Physics(allies=self.allies,enemies=self.enemies,ball=self.ball,dt=1.0/FPS,field=self.field,screen=self.screen)

        # === Puxa o endreço do widget para ele
        

    def update(self):
        #Atualiza 
        pass


    def draw(self,surface):
        '''
            Método para desenhar os objetos na superfície, dada as circunstâncias
        '''
        for obj in self.objetos:
            obj.draw(surface)   

    
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
        pass

    def reset_simulation(self, timer: Stopwatch):
        '''
            Resetando a simulação
        '''
        pass

    def pause_simulation(self):
        '''
            Pausa a simulação
        '''