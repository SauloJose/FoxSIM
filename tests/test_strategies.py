import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from simulator.intelligence.BT.bt_conditions import IsClosestToBall
from simulator.intelligence.BT.bt_core import Status
from simulator.intelligence.BT.strategies import StrategyManager, TeamStrategy
from simulator.simulation import Simulation


class StrategyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.simulation = Simulation()

    @classmethod
    def tearDownClass(cls):
        cls.simulation.shutdown()

    def test_builds_one_tree_per_robot(self):
        manager = StrategyManager(
            profile="aggressive",
            factory=TeamStrategy(
                enemy_goal_pos=(100.0, 0.0),
                ally_goal_x=20.0,
            ),
        )
        trees = manager.build_trees_for_team(self.simulation.blue_team.robots)

        self.assertEqual(set(trees), {0, 1, 2})
        self.assertIsNot(trees[0], trees[1])
        self.assertIsNot(trees[1], trees[2])

    def test_goalkeeper_is_not_attacker_candidate(self):
        goalkeeper = self.simulation.blue_team.robots[0]
        condition = IsClosestToBall()

        result = condition.tick(
            goalkeeper,
            self.simulation.ball,
            self.simulation.blue_team.robots,
            self.simulation.red_team.robots,
            1 / 60,
        )

        self.assertEqual(result, Status.FAILURE)

    def test_go_to_point_updates_target_without_overwriting_real_velocity(self):
        robot = self.simulation.blue_team.robots[1]
        real_velocity_before = robot.velocity.copy()
        target = robot.position + [20.0, 10.0]

        robot.go_to_point(target, target_angle=None, dt=1 / 60)

        self.assertEqual(tuple(robot.target_position), tuple(target))
        self.assertEqual(tuple(robot.velocity), tuple(real_velocity_before))
        self.assertGreater((robot.desired_velocity ** 2).sum(), 0.0)


if __name__ == "__main__":
    unittest.main()
