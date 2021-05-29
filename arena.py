# (c) Nikolaus Howe

import time

from overrides import overrides

from player import Player, MCPlayer, PretrainedPlayer, HumanPlayer, VisualHumanPlayer
from game import Game
from game_graphics.game_window import GameWindow


class Arena(object):
  def __init__(self,
               game: Game,
               player_1: Player,
               player_2: Player,
               verbose: bool = False,
               silent: bool = False) -> None:
    """
    An arena, which coordinates the players and game.

    :param game: the game
    :param player_1: the first player (goes first)
    :param player_2: the second player
    :param verbose: whether or not to print extra information
    :param training_mode: whether or not to print the game state
    """
    self.game = game
    self.p1 = player_1
    self.p2 = player_2
    self.next_player_to_move = self.p1
    self.verbose = verbose
    self.silent = silent

  def switch_active_player(self) -> None:
    """
    Change whose turn it is.

    :return:
    """
    if self.next_player_to_move == self.p1:
      self.next_player_to_move = self.p2
    else:
      self.next_player_to_move = self.p1

  def play(self) -> None:
    """
    Run an entire game between the two players.

    :return:
    """
    game_on = True
    move_counter = 0
    while game_on:
      if not self.silent:
        print("Game state:", self.game.get_state())

      # Get the active player to choose a move
      move = self.next_player_to_move.move(self.game)
      if self.verbose:
        print(f"{self.next_player_to_move.name} chose move {move}")

      # Tell game to do the move
      game_on = self.game.play_move(move)

      # If it's a learning player, give it a reward for this move (but not on its first move)
      if isinstance(self.next_player_to_move, MCPlayer) and move_counter >= 2:
        self.next_player_to_move.receive_reward(0.)

      # Change the active player
      self.switch_active_player()

      # Increment the move counter
      move_counter += 1

    if self.verbose:
      print("Game over!")

    # Tell the players whether they won or lost
    self.next_player_to_move.receive_reward(1.)
    self.next_player_to_move.update_and_end_episode()
    if self.verbose:
      print(f"{self.next_player_to_move.name} won!")
    self.switch_active_player()
    self.next_player_to_move.receive_reward(-1.)
    self.next_player_to_move.update_and_end_episode()
    if self.verbose:
      print(f"{self.next_player_to_move.name} lost!")


class VisualArena(Arena):
  @overrides
  def __init__(self, game: Game, player_1: Player, player_2: Player, gw: GameWindow) -> None:
    """
    A special arena which interfaces with a game window,
    allowing for the game to be watched and played with a GUI.
    :param game: the game
    :param player_1: the first player (moves first)
    :param player_2: the second player
    :param gw: the game window
    """
    self.gw = gw
    super().__init__(game, player_1, player_2)

  @overrides
  def play(self) -> None:
    """
    Run an entire game between the two players, drawing computer moves,
    and accepting drawn human moves.

    :return:
    """
    game_on = True
    move_counter = 0
    while game_on:
      time.sleep(0.5)

      # print(self.gw.pyramid)
      # print()

      # print("the next player is", self.next_player_to_move.name)
      # Tell the human player to move
      # if isinstance(self.next_player_to_move, VisualHumanPlayer):
      #   print("It's the human's turn!")

      # Get the active player to choose a move
      move = self.next_player_to_move.move(self.game)

      # if move is None:
      #   self.switch_active_player()
      #   break  # Game over. Whoever clicked the 'x' loses.

      # Tell game to do the move
      game_on = self.game.play_move(move)

      # If it's a learning player, give it a reward for this move (but not on its first move)
      # if isinstance(self.next_player_to_move, MCPlayer) and move_counter >= 2:
      #   self.next_player_to_move.receive_reward(0.)
      # NOTE: no learning in the visual arena

      # Draw the move (only draw line if not a visual human player)
      if not self.next_player_to_move.is_visual_human():
        self.gw.draw_move(move)

      # Update the pyramid to reflect that the move has been played
      self.gw.pyramid.adjust(move)

      # Change the active player
      self.switch_active_player()

      # Increment the move counter
      move_counter += 1

    # Tell the game window that the game is over
    self.gw.game_over(isinstance(self.next_player_to_move, VisualHumanPlayer))


if __name__ == "__main__":
  # p1 = MCPlayer("Alice")
  # p2 = MCPlayer("Bob")
  # for i in range(100_000):
  #   if i and i % 10_000 == 0:
  #     print(i)
  #   # Player 1 goes first
  #   g1 = Game()
  #   a1 = Arena(g1, p1, p2)
  #   a1.play()
  #   p1.update()
  #   p1.end_episode()
  #   p2.update()
  #   p2.end_episode()
  #
  #   # Player 2 goes first
  #   g1 = Game()
  #   a1 = Arena(g1, p2, p1)
  #   a1.play()
  #   p1.update()
  #   p1.end_episode()
  #   p2.update()
  #   p2.end_episode()

  # p1 = PretrainedPlayer('Alice')
  # p2 = HumanPlayer('Niki')
  #
  # print(p1.Q)
  # # print(p2.Q)
  #
  # # Make the players play deterministically (greedily)
  # p1.eps = 0
  # # p2.eps = 0
  #
  # g1 = Game()
  # a1 = Arena(g1, p1, p2, verbose=True)
  # a1.play()
  #
  # g1 = Game()
  # a1 = Arena(g1, p2, p1, verbose=True)
  # a1.play()

  # p1.save_q(p1.name)
  # p2.save_q(p2.name)

  g1 = Game(4)
  gw = GameWindow(game=g1)

  p1 = PretrainedPlayer('trained_agents/Alice')
  # p1 = TrivialPlayer('Alice')
  p2 = HumanPlayer('Niki')
  # p2 = HumanPlayer(gw, 'Niki')
  # p2 = PretrainedPlayer('Bob')

  a1 = VisualArena(g1, p1, p2, gw)
  print("made the arena")

  # print(p1.Q)
  # print(p2.Q)

  # Make the players play deterministically (greedily)
  p1.eps = 0
  # p2.eps = 0

  a1.play()
