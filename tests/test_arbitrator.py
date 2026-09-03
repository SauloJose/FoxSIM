import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from simulator.rules.rules import Decisions, GameState
from simulator.simulation import Simulation


class ArbitratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.simulation = Simulation()

    @classmethod
    def tearDownClass(cls):
        cls.simulation.shutdown()

    def setUp(self):
        self.simulation.reset()
        self.arbitrator = self.simulation.arbitrator

    def test_starts_in_halt(self):
        self.assertEqual(self.arbitrator.state, GameState.HALT)

    def test_state_transitions(self):
        self.arbitrator.start_match()
        self.assertEqual(self.arbitrator.state, GameState.GAME_ON)

        self.arbitrator.stop()
        self.assertEqual(self.arbitrator.state, GameState.STOP)

        self.arbitrator.halt()
        self.assertEqual(self.arbitrator.state, GameState.HALT)

    def test_can_disable_arbitration(self):
        self.simulation.set_arbitrator_enabled(False)
        self.arbitrator.start_match()

        self.assertEqual(self.arbitrator.state, GameState.HALT)
        self.assertIsNone(self.arbitrator.evaluate(1 / 60))

        self.simulation.set_arbitrator_enabled(True)

    def test_penalty_uses_configured_position(self):
        self.arbitrator.prepare_penalty(Decisions.PENALTY_ALLY)

        self.assertEqual(
            tuple(self.simulation.ball.position),
            tuple(self.arbitrator.penalty_ally_pos),
        )

    def test_free_kick_separates_penalized_team(self):
        self.arbitrator.prepare_free_kick(Decisions.FOUL_ALLY)

        for robot in self.simulation.blue_team.robots:
            self.assertGreaterEqual(
                robot.distance_to(self.simulation.ball.x, self.simulation.ball.y),
                20.0,
            )


if __name__ == "__main__":
    unittest.main()
