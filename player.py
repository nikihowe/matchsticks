# (c) Nikolaus Howe 2021

import numpy as np
import random
from abc import ABC, abstractmethod
from overrides import overrides

from utils import get_random_move


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
    return get_random_move(game.get_allowed())
