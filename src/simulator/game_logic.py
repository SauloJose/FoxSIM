from simulator.collision.collision import *
from simulator.objects.field import Field
from simulator.objects.ball import Ball 
from simulator.objects.robot import Robot 
from simulator.objects.team import Team
from simulator.rules.rules  import *
from ui.interface   import Interface
import numpy as np

class Physics:
    '''
        Engine de física responsável por atualizar o estado da simulação.
        Gerencia o movimento dos robôs e da bola, e resolve colisões via SAT.
    '''
    def __init__(self, allies: Team, enemies:Team, ball: Ball, dt: float, field: Field, screen):
        # Objetos principais da simulação
        self.team_ally = allies                 # Salvando time aliado
        self.team_enemy = enemies               # Salvando time inimigo
        self.allies = self.team_ally .robots    # Robôs aliados
        self.enemies = self.team_enemy.robots   # Robôs adversários
        self.ball = ball                        # Bola da partida
        self.dt = dt                            # Intervalo de tempo da simulação
        self.field = field                      # Campo com limites e obstáculos
        self.screen = screen                    # Tela para debug visual (caso necessário)

        # Objetos móveis que serão atualizados a cada ciclo
        self.moving_objects = [self.ball] + self.allies + self.enemies

        #Lista de todos os robôs
        self.bots = self.allies + self.enemies 

        # Lista de todos objetos de colisão do sistema (móveis + estrutura do campo)
        self.all_collision_objects = [obj.collision_object for obj in self.moving_objects]
        self.all_collision_objects.append(self.field.collision_object)

        # Gerenciador de colisões (com Spatial Hashing e SAT)
        self.collision_manager = CollisionManagerSAT(cell_size=CELL_SIZE, screen=self.screen, dt=self.dt)

        #Parte para a atualização de controle dos robôs


    # ===============================================================

    def update(self):
        '''
            Atualiza o estado físico da simulação a cada frame:
            - Detecta e resolve colisões.
            - Atualiza posições da bola e dos robôs.
        '''
        #Verifica colisões e física
        self.check_collisions()

        #Atualiza posição da bola
        self.update_ball()

        #Atualiza posição dos robôs
        self.update_bots()
    
    # ===============================================================
    def check_collisions(self):
        '''
            Detecta e resolve colisões entre todos os objetos.
        '''
        self.collision_manager.detect_and_resolve(self.all_collision_objects)

    def update_bots(self):
        '''
            Atualiza os robôs aliados e inimigos com base nas velocidades das rodas.
        '''
        #Atualiza posição dos robôs
        for bot in self.bots:
            bot.move(self.dt)




    def update_ball(self):
        '''
            Atualizo a posição da bola na interface.
        '''
        self.ball.update_position(self.dt)
