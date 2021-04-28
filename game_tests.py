import unittest
from game import Game


class TestGameBasics(unittest.TestCase):
  def test_game_start(self):
    # Check basic game
    g1 = Game()
    self.assertEqual(g1.layers, [1, 3, 5, 7])

    # Check bigger game
    g2 = Game(5)
    self.assertEqual(g2.layers, [1, 3, 5, 7, 9])

    # Check we can't make an empty game
    with self.assertRaises(ValueError):
      g3 = Game(0)

  def test_play_move(self):
    # Check basic move
    g1 = Game()
    g1.play_move((3, 4, 4))
    self.assertEqual(g1.layers, [1, 1, 3, 3, 7])

    # Check move at start of layer
    g2 = Game()
    g2.play_move((2, 1, 2))
    self.assertEqual(g2.layers, [1, 1, 5, 7])

    # Check move which clears whole row
    g3 = Game()
    g3.play_move((3, 1, 5))
    self.assertEqual(g3.layers, [1, 3, 7])
