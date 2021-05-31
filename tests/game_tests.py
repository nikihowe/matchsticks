# (c) Nikolaus Howe 2021
import unittest
import PySimpleGUI as sg

from game import Game
from player import TrivialPlayer, RandomPlayer, MCPlayer, PretrainedPlayer
from game_graphics.game_window import GameWindow
from arena import Arena
from dojo import Dojo


class TestGameBasics(unittest.TestCase):
  def test_game_start(self):
    # Check basic game
    g1 = Game()
    self.assertEqual(g1.get_state(), (1, 3, 5, 7))

    # Check tiny game
    g2 = Game(1)
    self.assertEqual(g2.get_state(), (1,))

    # Check bigger game
    g3 = Game(5)
    self.assertEqual(g3.get_state(), (1, 3, 5, 7, 9))

    # Check we can't make an empty game
    with self.assertRaises(ValueError):
      g4 = Game(0)

  def test_play_move(self):
    # Check basic move
    g1 = Game()
    g1.play_move((3, 4, 4))
    self.assertEqual(g1.get_state(), (1, 1, 3, 3, 7))

    # Check move at start of layer
    g2 = Game()
    g2.play_move((2, 1, 2))
    self.assertEqual(g2.get_state(), (1, 1, 5, 7))

    # Check move which clears whole row
    g3 = Game()
    g3.play_move((3, 1, 5))
    self.assertEqual(g3.get_state(), (1, 3, 7))

    # Check move which doesn't end the game
    g4 = Game(2)
    still_going = g4.play_move((1, 1, 1))
    self.assertEqual(still_going, True)
    self.assertEqual(g4.get_state(), (3,))

    # Check move which does end the game
    g5 = Game(1)
    still_going = g5.play_move((1, 1, 1))
    self.assertEqual(still_going, False)
    self.assertEqual(g5.get_state(), ())


class TestPlayer(unittest.TestCase):
  def test_simple_player(self):
    g1 = Game()
    p1 = TrivialPlayer()
    self.assertEqual(p1.move(game=g1), (1, 1, 1))

  # Make sure a learning agent plays properly in certain situations,
  # after only 10_000 games of training
  # NOTE: failing (a) test(s) doesn't mean it isn't training, just that it isn't very good after 10_000
  def test_MC_agent_10_000(self):
    p1 = MCPlayer('Alice')
    p2 = RandomPlayer()  # TODO: change into optimal player later
    d1 = Dojo(p1, p2)
    d1.train_players(num_games=50_000, num_layers=2)
    # print("after training", p1.Q)

    g1 = Game(2)
    self.assertEqual(p1.move(g1), (2, 1, 3))

    g2 = Game()
    g2.reset([3])
    player_move = p1.move(g2)
    is_best_move_1 = player_move == (1, 1, 2)
    is_best_move_2 = player_move == (1, 2, 3)
    self.assertTrue(is_best_move_1 or is_best_move_2)

  def test_specific_train(self):
    p1 = MCPlayer('Alice')
    p2 = RandomPlayer()  # TODO: change to optimal player later
    d1 = Dojo(p1, p2)
    position = [4]
    d1.drill_position(num_games=50_000, position=position)
    # print(p1.Q)

    g1 = Game()
    g1.reset(position)
    player_move = p1.move(g1)
    is_best_move_1 = player_move == (1, 1, 3)
    is_best_move_2 = player_move == (1, 2, 4)
    self.assertTrue(is_best_move_1 or is_best_move_2)

  def test_save_and_load(self):
    p1 = MCPlayer('Alice')
    d1 = Dojo(p1)
    d1.train_players(num_games=1000)
    p1.save_q()
    p2 = PretrainedPlayer(p1.name)
    self.assertEqual(p1.Q, p2.Q)


class TestArena(unittest.TestCase):
  def test_trivial_game(self):
    g1 = Game()
    p1 = TrivialPlayer("TrivialAlice")
    p2 = TrivialPlayer("TrivialBob")
    a1 = Arena(g1, p1, p2, silent=True)
    a1.play()
    self.assertEqual(g1.get_state(), ())

  def test_random_game(self):
    g2 = Game()
    p1 = RandomPlayer("RandomAlice")
    p2 = RandomPlayer("RandomBob")
    a2 = Arena(g2, p1, p2, silent=True)
    a2.play()
    self.assertEqual(g2.get_state(), ())

  def test_trivial_vs_random_game(self):
    g3 = Game()
    p1 = TrivialPlayer("TrivialAlice")
    p2 = RandomPlayer("RandomBob")
    a3 = Arena(g3, p1, p2, silent=True)
    a3.play()
    self.assertEqual(g3.get_state(), ())


class TestGameWindow(unittest.TestCase):
  def test_computer_move_drawing(self):
    g1 = Game()
    graph = sg.Graph(canvas_size=(500, 500), key='graph',
                     graph_bottom_left=(0, 500), graph_top_right=(500, 0),
                     enable_events=True,  # mouse click events
                     background_color='lightblue',
                     drag_submits=True)
    window = sg.Window('Matchsticks', [[graph]], finalize=True)
    gw = GameWindow(game=g1, window=window)
    gw.draw()

    layer = 4
    left_idx = 5
    right_idx = 6
    m = (layer, left_idx, right_idx)
    gw.draw_move(m)

    # For indexing, make 0-indexed
    layer -= 1
    left_idx -= 1
    right_idx -= 1

    self.assertTrue(gw.pyramid.rows[layer].matchsticks[left_idx-1].is_active)
    self.assertFalse(gw.pyramid.rows[layer].matchsticks[left_idx].is_active)
    self.assertFalse(gw.pyramid.rows[layer].matchsticks[right_idx].is_active)
    self.assertTrue(gw.pyramid.rows[layer].matchsticks[right_idx+1].is_active)

  def test_pyramid_update(self):
    g1 = Game()
    graph = sg.Graph(canvas_size=(500, 500), key='graph',
                     graph_bottom_left=(0, 500), graph_top_right=(500, 0),
                     enable_events=True,  # mouse click events
                     background_color='lightblue',
                     drag_submits=True)
    window = sg.Window('Matchsticks', [[graph]], finalize=True)
    gw = GameWindow(game=g1, window=window)

    layer = 4
    left_idx = 5
    right_idx = 6
    m = (layer, left_idx, right_idx)
    gw.pyramid.adjust(m)

    # Check the rows are correct
    self.assertEqual(len(gw.pyramid.rows), 5)
    self.assertEqual(len(gw.pyramid.rows[0].matchsticks), 1)
    self.assertEqual(len(gw.pyramid.rows[1].matchsticks), 1)
    self.assertEqual(len(gw.pyramid.rows[2].matchsticks), 3)
    self.assertEqual(len(gw.pyramid.rows[3].matchsticks), 4)
    self.assertEqual(len(gw.pyramid.rows[4].matchsticks), 5)

    # Check a matchstick
    self.assertEqual(gw.pyramid.rows[1].matchsticks[0].layer, 2)
    self.assertEqual(gw.pyramid.rows[1].matchsticks[0].idx, 1)

  # At this point, I don't think there is a way to automatically get a move from the human
  def test_human_move_recording(self):
    pass


if __name__ == '__main__':
  unittest.main()
