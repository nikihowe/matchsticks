# (c) Nikolaus Howe

from player import Player, TrivialPlayer, RandomPlayer, MCPlayer, PretrainedPlayer, HumanPlayer
from game import Game


class Arena(object):

  def __init__(self, game: Game, player_1: Player, player_2: Player, verbose: bool = False):
    self.game = game
    self.p1 = player_1
    self.p2 = player_2
    self.next_player_to_move = self.p1
    self.verbose = verbose

  def switch_active_player(self):
    if self.next_player_to_move == self.p1:
      self.next_player_to_move = self.p2
    else:
      self.next_player_to_move = self.p1

  def play(self):
    game_on = True
    move_counter = 0
    while game_on:
      if self.verbose:
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
    if self.verbose:
      print(f"{self.next_player_to_move.name} won!")
    self.switch_active_player()
    self.next_player_to_move.receive_reward(-1.)
    if self.verbose:
      print(f"{self.next_player_to_move.name} lost!")


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

  p1 = PretrainedPlayer('Alice')
  p2 = HumanPlayer('Niki')

  print(p1.Q)
  # print(p2.Q)

  # Make the players play deterministically (greedily)
  p1.eps = 0
  # p2.eps = 0

  g1 = Game()
  a1 = Arena(g1, p1, p2, verbose=True)
  a1.play()

  g1 = Game()
  a1 = Arena(g1, p2, p1, verbose=True)
  a1.play()

  # p1.save_q(p1.name)
  # p2.save_q(p2.name)
