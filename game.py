# (c) Nikolaus Howe 2021

import time
import numpy as np
import os

from utils import generate_allowed


class Game(object):

  def __init__(self, num_layers=4):
    """
    A game of matchsticks.

    :param num_layers: The number of layers of (odd numbers of) matchsticks you want to start the game with.
    """

    # Check for valid number of layers
    if not 1 <= num_layers <= 100:
      print("Please choose a number of layers between 1 and 100 inclusive")
      raise ValueError

    # Create the starting layers
    self.layers = list(map(lambda x: x * 2 + 1, range(num_layers)))

    # Generate allowed moves reference (to be used by get_allowed)
    self.allowed_reference = generate_allowed(num_layers * 2 - 1)
    # print("starting allowed are", self.allowed_reference)

  def get_allowed(self):
    """
    Generate the allowed moves for the given layers.

    :return: A list of lists of allowed moves, in the format (low_idx, high_idx),
              where index - 1 is the index of the layer.
    """
    allowed = []
    for layer_n in self.layers:
      allowed.append(self.allowed_reference[layer_n - 1])
    return allowed

  def is_allowed(self, move):
    """
    Check if a given move is valid.

    :param move: The move, written as a triple (layer_i, low_idx, high_idx).
    :return: True for valid move, False otherwise.
    """
    layer_i, low, high = move

    # Make layer 0-indexed
    layer_i -= 1

    return (
          0 <= layer_i < len(self.layers)
          and 1 <= low <= high <= self.layers[layer_i]
    )

  def play_move(self, move):
    """
    Play a move.

    :param move: A tuple containing your move, in the format (layer_i, low_idx, high_idx), where:
                  - layer_i is the index of the layer you want to play on (1-indexed).
                  - low_idx is the index of the lowest matchstick to cross off (1-indexed).
                  - high_idx is the index of the highest matchstick to cross off (1-indexed.
    :return:
    """
    if not self.is_allowed(move):
      print("This is not a valid move, please try again")
      return -1

    layer_i, low_idx, high_idx = move

    # Make the layer 0-indexed
    layer_i -= 1

    # Perform move
    active_layer = self.layers.pop(layer_i)
    left_result = low_idx - 1
    right_result = active_layer - high_idx
    if left_result > 0:
      self.layers.append(left_result)
    if right_result > 0:
      self.layers.append(right_result)
    self.layers.sort()

    # Return False if the game is over,
    # and True if the game is still going
    return not not self.layers
