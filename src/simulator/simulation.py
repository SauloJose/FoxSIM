import pygame
import pygame_gui
import numpy as np
import pymunk

from simulator.objects.team import Team, blue_team_positions, red_team_positions
from simulator.objects.ball import Ball
from simulator.objects.field import Field
from simulator.objects.timer import Stopwatch
from simulator.rules.rules import Arbitrator, Decisions
from simulator.intelligence.BT.strategies import StrategyManager, TeamStrategy
from ui.interface import Interface
from ui.interface_config import *


class Simulation:
    """Controla o ciclo de vida, entrada, atualização e renderização do jogo."""

    def __init__(self):
        pygame.init()
        self._create_window()
        self._create_world()
        self._create_objects()
        self._create_strategies()
        self._create_state()

    def _create_window(self):
        window_size = (
            int(WINDOWS_FIELD_WIDTH_PX),
            int(WINDOWS_FIELD_HEIGHT_PX + SCOREBOARD_HEIGHT_PX + CONFIG_HEIGHT_PX),
        )
        self.screen = pygame.display.set_mode(window_size)
        self.manager = pygame_gui.UIManager(
            (WINDOWS_FIELD_WIDTH_PX + SIDEBAR_WIDTH_PX,
             WINDOWS_FIELD_HEIGHT_PX + SCOREBOARD_HEIGHT_PX + CONFIG_HEIGHT_PX)
        )
        self.clock = pygame.time.Clock()

    def _create_world(self):
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)
        self.space.damping = 0.9995
        self.space.collision_slop = 0.01
        self.space.collision_bias = (1 - 0.4) ** 60
        self.space.iterations = 30

    def _create_objects(self):
        self.interface = Interface(self.screen)
        self.field = Field(
            self.space,
            width=FIELD_INTERNAL_WIDTH_IN_PX,
            height=FIELD_INTERNAL_HEIGHT_IN_PX,
            color=FIELD_COLOR,
        )
        self.ball = Ball(
            XVBALL_INIT,
            YVBALL_INIT,
            field=self.field,
            space=self.space,
            radius=BALL_RADIUS_CM,
            color=BALL_COLOR,
        )
        self.blue_team = Team(blue_team_positions, BLUE_TEAM, initial_angle=0, space=self.space)
        self.red_team = Team(red_team_positions, RED_TEAM, initial_angle=180, space=self.space)
        self.bots = self.blue_team.robots + self.red_team.robots
        self.timer = Stopwatch(TIMER_PARTY)
        self.arbitrator = Arbitrator(
            self.ball,
            self.field,
            self.blue_team,
            self.red_team,
            self.interface,
            self.timer,
        )

    def _create_strategies(self):
        blue_manager = StrategyManager(
            profile="aggressive",
            factory=TeamStrategy(
                enemy_goal_pos=MID_GOALAREA_E,
                ally_goal_x=MID_GOALAREA_A[0],
            ),
        )
        self.blue_trees = blue_manager.build_trees_for_team(self.blue_team.robots)

        red_manager = StrategyManager(
            profile="defensive",
            factory=TeamStrategy(
                enemy_goal_pos=MID_GOALAREA_A,
                ally_goal_x=MID_GOALAREA_E[0],
            ),
        )
        self.red_trees = red_manager.build_trees_for_team(self.red_team.robots)

    def _create_state(self):
        self.game_started = False
        self.draw_collision_objects = False
        self.target_debug = False
        self.target_debug_ids = set()
        self.is_game_paused = False
        self.selected_robot = None
        self.running = True
        self.frame_count = 0

    def reset(self):
        """Restaura a partida ao estado inicial sem recriar a simulação."""
        self.timer.reset()
        self.timer.duration = TIMER_PARTY
        self.ball.reset_position()
        self.blue_team.reset_positions()
        self.red_team.reset_positions()
        self.interface.score = [0, 0]

    def handle_events(self):
        """Processa os eventos de janela, teclado e mouse do frame atual."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event)
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion()
            elif event.type == pygame.MOUSEBUTTONUP:
                self._release_selected_robot()

    def _handle_key(self, event):
        if event.key == pygame.K_d:
            self.target_debug = not self.target_debug
        elif event.key == pygame.K_c:
            self.draw_collision_objects = not self.draw_collision_objects
        elif event.key == pygame.K_p:
            self.is_game_paused = not self.is_game_paused
            if self.is_game_paused:
                self.timer.pause()
            else:
                self.timer.resume()
        elif event.mod & pygame.KMOD_CTRL and event.key in (
                pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
            if event.key == pygame.K_4:
                if len(self.target_debug_ids) == 3:
                    self.target_debug_ids.clear()
                else:
                    self.target_debug_ids = {0, 1, 2}
                return

            robot_id = event.key - pygame.K_1
            if robot_id in self.target_debug_ids:
                self.target_debug_ids.remove(robot_id)
            else:
                self.target_debug_ids.add(robot_id)

    def _handle_mouse_down(self, event):
        x, y = pygame.mouse.get_pos()
        point = screen_to_virtual([x, y])

        if self.is_game_paused:
            self._select_robot(point)
            if self.selected_robot is None and self.field.RectUtil.contains(point):
                self.ball.position = point
                self.ball.body.velocity = (0.0, 0.0)
            if event.button == 3 and self.selected_robot is not None:
                self.selected_robot.rotate(15)

        if self.interface.start_button.collidepoint(x, y) and not self.is_game_paused:
            self.game_started = True
            self.timer.start()
        elif self.interface.reset_button.collidepoint(x, y) and not self.is_game_paused:
            self.game_started = False
            self.reset()

    def _select_robot(self, point):
        self.selected_robot = None
        pymunk_point = (float(point[0]), float(point[1]))
        for bot in self.bots:
            bot._is_selected = False
            if bot.shape.point_query(pymunk_point).distance <= 0:
                bot._is_selected = True
                self.selected_robot = bot
                break

    def _handle_mouse_motion(self):
        if self.selected_robot is None or not self.is_game_paused:
            return
        x, y = pygame.mouse.get_pos()
        point = screen_to_virtual([x, y])
        if not pygame.mouse.get_pressed()[0]:
            return

        pymunk_point = (float(point[0]), float(point[1]))
        can_move = all(
            other_bot == self.selected_robot
            or other_bot.shape.point_query(pymunk_point).distance > 0
            for other_bot in self.bots
        )
        if can_move:
            self.selected_robot.new_position(*point)

    def _release_selected_robot(self):
        if self.selected_robot is not None:
            self.selected_robot._is_selected = False
            self.selected_robot = None

    def update(self, dt):
        """Atualiza a inteligência, a física e as regras da partida."""
        if self.is_game_paused:
            return

        if self.game_started:
            self.frame_count += 1
            for bot in self.blue_team.robots:
                self.blue_trees[bot.id_robot].tick(
                    bot, self.ball, self.blue_team.robots, self.red_team.robots, dt
                )
            for bot in self.red_team.robots:
                self.red_trees[bot.id_robot].tick(
                    bot, self.ball, self.red_team.robots, self.blue_team.robots, dt
                )

        fixed_dt = 1 / 60.0
        for bot in self.bots:
            bot.apply_motor_forces(fixed_dt)
        self.space.step(fixed_dt)
        self.ball.clamp_velocity()
        self.ball.apply_damping(dt)

        if self.game_started:
            self.handle_arbitrator_decision(self.arbitrator.evaluate())

    def handle_arbitrator_decision(self, decision):
        """Ponto de extensão para decisões do árbitro e eventos da partida."""
        if decision == Decisions.FINISH:
            self.game_started = False

    def render(self):
        """Desenha o frame atual e atualiza a janela."""
        self.interface.get_states(
            draw_collision_objects=self.draw_collision_objects,
            target_debug=self.target_debug,
            running=self.game_started,
            is_game_paused=self.is_game_paused,
            target_debug_ids=self.target_debug_ids,
            fps=self.clock.get_fps(),
        )
        self.interface.draw(
            time_left=self.timer.get_time_left(),
            screen=self.screen,
            ball=self.ball,
            field=self.field,
            robots=self.bots,
            target_debug_ids=self.target_debug_ids,
        )
        self.interface.draw_robot_logs(self.screen, self.blue_team, self.red_team)
        pygame.display.flip()

    def run(self):
        """Executa o loop principal até a janela ser fechada."""
        try:
            while self.running:
                dt = self.clock.tick(FPS) / 1000.0
                self.handle_events()
                self.update(dt)
                self.render()
        finally:
            self.shutdown()

    def shutdown(self):
        """Libera os recursos da interface gráfica."""
        pygame.quit()
