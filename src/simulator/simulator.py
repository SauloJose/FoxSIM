#Definição da classe simulator
from simulator.collision.collision import *
from simulator.objects.field import Field
from simulator.objects.ball import Ball 
from simulator.objects.robot import Robot 
from simulator.objects.team import Team
from simulator.rules.rules  import *
from ui.interface_config    import *
from simulator.game_logic   import *
from src.ui.pages.objects.SimWidget import *

import numpy as np
from PyQt6.QtCore import QTimer

class Simulator:
    '''
        Classe para encapsular a lógica da simulação e controlar o loop de tempo/desenho.
    '''
    def __init__(self, screen: SimulatorWidget, fps=60):
        self.screen = screen  # SimulatorWidget
        self.fps = fps
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

        # Inicialização dos objetos
        self.get_variables_simulation()
        self.create_objects()

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
        self.arbitrator = Arbitrator(self.ball, self.field, self.allies, self.enemies, self.screen, self.cronometer)

    def set_FPS(self, fps):
        self.fps = max(1, int(fps))
        self.timer.setInterval(int(1000 / self.fps))
        if self.Physics_Engine:
            self.Physics_Engine.dt = 1.0 / self.fps

    def start(self):
        if not self.running:
            self.running = True
            self.paused = False
            self.simulation_started = True
            self.timer.start(int(1000 / self.fps))

    def pause(self):
        if self.running and not self.paused:
            self.paused = True
            self.timer.stop()

    def resume(self):
        if self.running and self.paused:
            self.paused = False
            self.timer.start(int(1000 / self.fps))

    def stop(self):
        self.running = False
        self.paused = False
        self.simulation_started = False
        self.timer.stop()

    def reset(self):
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

    def _main_loop(self):
        if not self.running or self.paused:
            return
        self.update()
        self.draw()

    def update(self):
        # Atualiza física e lógica do jogo
        if self.Physics_Engine:
            self.Physics_Engine.update()
        if self.arbitrator and self.arbitrator.analyzer() == Decisions.FINISH:
            self.simulation_started = False
            self.reset()

    def draw(self):
        # Limpa o backbuffer
        self.screen.back_buffer.clear()
        # Desenha campo
        if self.field:
            self.field.draw(self.screen)
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
            self.Physics_Engine.collision_manager.draw_debug(self.screen)
        if self.draw_grid_collision and self.Physics_Engine:
            self.Physics_Engine.collision_manager.draw_grid(self.screen)
        # Atualiza o widget
        self.screen.update_widget()

    def get_variables_simulation(self):
        # Puxe variáveis da interface/configuração aqui
        pass

    def create_objects(self):
        # Crie times, robôs, bola, campo, etc.
        pass

    def destroy(self):
        self.stop()
        # Libere recursos se necessário

    # Métodos extras para controle externo
    def is_running(self):
        return self.running and not self.paused

    def is_paused(self):
        return self.paused

    def is_started(self):
        return self.simulation_started