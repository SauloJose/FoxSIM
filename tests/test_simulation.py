import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

import pygame

from simulator.simulation import Simulation
from ui.interface_config import (
    CONFIG_HEIGHT_PX,
    SCOREBOARD_HEIGHT_PX,
    WINDOWS_FIELD_HEIGHT_PX,
    WINDOWS_FIELD_WIDTH_PX,
)


class SimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.simulation = Simulation()

    @classmethod
    def tearDownClass(cls):
        cls.simulation.shutdown()

    def setUp(self):
        self.simulation.reset()
        self.simulation.target_debug_ids.clear()

    def press_control(self, key):
        event = pygame.event.Event(
            pygame.KEYDOWN,
            key=key,
            mod=pygame.KMOD_CTRL,
        )
        self.simulation._handle_key(event)

    def test_robot_order_and_ids(self):
        self.assertEqual(
            [(robot.id_robot, robot.role) for robot in self.simulation.blue_team.robots],
            [(0, "goalkeeper"), (1, "attacker1"), (2, "attacker2")],
        )

    def test_debug_shortcuts_select_expected_robots(self):
        self.press_control(pygame.K_1)
        self.assertEqual(self.simulation.target_debug_ids, {0})

        self.press_control(pygame.K_2)
        self.assertEqual(self.simulation.target_debug_ids, {0, 1})

        self.press_control(pygame.K_3)
        self.assertEqual(self.simulation.target_debug_ids, {0, 1, 2})

    def test_ctrl_four_toggles_all_targets(self):
        self.press_control(pygame.K_4)
        self.assertEqual(self.simulation.target_debug_ids, {0, 1, 2})

        self.press_control(pygame.K_4)
        self.assertEqual(self.simulation.target_debug_ids, set())

    def test_render_keeps_expected_window_size(self):
        self.simulation.render()
        expected_size = (
            WINDOWS_FIELD_WIDTH_PX,
            WINDOWS_FIELD_HEIGHT_PX + SCOREBOARD_HEIGHT_PX + CONFIG_HEIGHT_PX,
        )
        self.assertEqual(self.simulation.screen.get_size(), expected_size)


if __name__ == "__main__":
    unittest.main()
