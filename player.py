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

  @abstractmethod
  def move(self, layers, allowed_moves):
    """
    Get the player to play a move among allowed_moves

    :param layers: The current layers of the game
    :param allowed_moves: The currently allowed moves of the game
    :return: A move in the format of an int 3-tuple
    """
    pass


class TrivialPlayer(Player):
  """
  A player which always plays the move (1, 1, 1)
  """

  @overrides
  def move(self, layers, allowed_moves):
    return 1, 1, 1


class RandomPlayer(Player):
  """
  A player which always plays random moves.
  """

  @overrides
  def move(self, layers, allowed_moves):
    return get_random_move(allowed_moves)
