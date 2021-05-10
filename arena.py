# (c) Nikolaus Howe

from player import Player, TrivialPlayer
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
    while game_on:
      if self.verbose:
        print("Game state:", self.game.layers)

      # Get the active player to choose a move
      move = self.next_player_to_move.move(self.game)
      if self.verbose:
        print(f"{self.next_player_to_move.name} chose move {move}")

      # Tell game to do the move
      game_on = self.game.play_move(move)

      # Change the active player
      self.switch_active_player()

    if self.verbose:
      print("Game over!")

    # Tell the players whether they won or lost
    self.next_player_to_move.you_win()
    if self.verbose:
      print(f"{self.next_player_to_move.name} won!")
    self.switch_active_player()
    self.next_player_to_move.you_lose()
    if self.verbose:
      print(f"{self.next_player_to_move.name} lost!")


if __name__ == "__main__":
  g1 = Game()
  p1 = TrivialPlayer("Alice")
  p2 = TrivialPlayer("Bob")
  a1 = Arena(g1, p1, p2, verbose=True)

  a1.play()
