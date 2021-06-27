# (c) Nikolaus Howe 2021
from tqdm import trange
from typing import Optional

from matchsticks.arena import Arena
from matchsticks.game import Game
from matchsticks.player import MCPlayer, Player


class Dojo(object):
  def __init__(self,
               p1: Optional[Player] = None,
               p2: Optional[Player] = None) -> None:
    """
    A dojo for automated player training.

    :param p1: the first player (if any)
    :param p2: the second player (if any)
    """
    if not p1:
      p1 = MCPlayer()
    if not p2:
      p2 = MCPlayer()

    if not isinstance(p1, MCPlayer) and not isinstance(p2, MCPlayer):
      raise Exception('Neither of these players can be trained!')

    self.p1 = p1
    self.p2 = p2

  def _train_loop(self, g1: Game, num_games: int) -> None:
    """
    Run the training loop.

    :param g1: the game
    :param num_games: the number of
    :return:
    """
    starting_position = g1.get_state()

    for i in trange(num_games):
      # Make each player start half the time
      if i % 2:
        p1 = self.p1
        p2 = self.p2
      else:
        p1 = self.p2
        p2 = self.p1
      a1 = Arena(g1, p1, p2, silent=True)
      a1.play()
      p1.update_and_end_episode()
      p2.update_and_end_episode()
      g1.reset(starting_position)

  def train_players(self,
                    num_games: int,
                    num_layers: Optional[int] = 4) -> None:
    """
    Train the players in the dojo.

    :param num_games: for how many games
    :param num_layers: how many layers should the game have (default 4)
    :return:
    """
    g1 = Game(num_layers)
    self._train_loop(g1, num_games)

  def drill_position(self, num_games: int, position: list[int]) -> None:
    """
    Train the agents on a given position.

    :param num_games: how many games to train for
    :param position: the position to train on
    :return:
    """
    # Make a game that's big enough to store all possible states
    # which come from this position
    g1 = Game(int((max(position)+2) // 2))
    g1.reset(position)
    self._train_loop(g1, num_games)

  def get_player(self, second=False) -> Player:
    """
    Return the player.

    :param second: if true, returns the second player instead of the first
    :return: the player
    """
    if not second:
      return self.p1
    else:
      return self.p2


if __name__ == "__main__":
  d = Dojo()
  d.train_players(5_000, 4)
  easy = d.get_player()
  easy.save_q("trained_agents/easy.player")

  d = Dojo()
  d.train_players(20_000, 4)
  med = d.get_player()
  med.save_q("trained_agents/medium.player")

  d = Dojo()
  d.train_players(1_000_000, 5)
  hard = d.get_player()
  hard.save_q("trained_agents/hard.player")
