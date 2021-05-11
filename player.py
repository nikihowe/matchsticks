# (c) Nikolaus Howe 2021

import numpy as np
import random
from abc import ABC, abstractmethod
from overrides import overrides


class Player(ABC):
  """
  An abstract class for defining players
  """

  def __init__(self, name="Alice"):
    self.name = name

  @abstractmethod
  def move(self, game):
    """
    Get the player to play a move among allowed_moves

    :param: The current game
    :return: A move in the format of an int 3-tuple
    """
    pass

  def you_win(self):
    """
    Tell the player that they won.
    :return:
    """
    pass

  def you_lose(self):
    """
    Tell the player that they lost.
    :return:
    """
    pass


class TrivialPlayer(Player):
  """
  A player which always plays the move (1, 1, 1)
  """

  @overrides
  def move(self, game):
    return 1, 1, 1


class RandomPlayer(Player):
  """
  A player which always plays random moves.
  """

  @overrides
  def move(self, game):
    return random.choice(game.get_allowed())


class MCPlayer(Player):
  """
  An on-policy first-visit MC control player.
  """
  #
  # @overrides
  # def __init__(self) -> None:
  #   super().__init__()
  #   self.Q = {}
  #   self.rewards = []
  #   self.eps = 0.05
  #   self.history = []
  #
  # def policy(self, game_word) -> int:
  #   # Choose randomly self.eps of the time
  #   if np.random.uniform() < self.eps:
  #     return np.random.choice(get_possible_moves())
  #   else:
  #     q_row = list(self.Q[game_word].items())  # Turn the dict into a list
  #     q_row.sort(key=lambda x: x[1], reverse=True)  # Sort in descending order
  #     # print("sorted row is", q_row)
  #     return q_row[0][0]  # return the move with the highest Q value
  #
  # @overrides
  # def move(self, game):
  #   # Check if we have seen this state before
  #   # If we haven't initialize the Q table for that state
  #   if not game.levels in self.Q:
  #     self.Q[game.levels.copy()] =
  #
  #
  #   return 1, 1, 1
