import unittest
from main import Game


class MyTestCase(unittest.TestCase):
    game = Game()
    game.play_round()

    def test_something(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
