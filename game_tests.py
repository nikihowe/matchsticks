import unittest
from game import Game


class TestGameBasics(unittest.TestCase):
  def test_game_start(self):
    # Check basic game
    g1 = Game()
    self.assertEqual(g1.layers, [1, 3, 5, 7])

    # Check tiny game
    g2 = Game(1)
    self.assertEqual(g2.layers, [1])

    # Check bigger game
    g3 = Game(5)
    self.assertEqual(g3.layers, [1, 3, 5, 7, 9])

    # Check we can't make an empty game
    with self.assertRaises(ValueError):
      g4 = Game(0)

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

    # Check move which doesn't end the game
    g4 = Game(2)
    still_going = g4.play_move((1, 1, 1))
    self.assertEqual(still_going, True)
    self.assertEqual(g4.layers, [3])

    # Check move which does end the game
    g5 = Game(1)
    still_going = g5.play_move((1, 1, 1))
    self.assertEqual(still_going, False)
    self.assertEqual(g5.layers, [])
