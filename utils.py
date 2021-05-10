# (c) Nikolaus Howe 2021

import numpy as np
import random


# NOTE: consider storing this somewhere for big games
def generate_allowed(num=100):
  """
  Generate all allowed moves for layers of length up to num.

  :param num: Up to which size of layer to consider (counts even and odd).
  :return: A list of allowed moves, in the format (low_idx, high_idx).
            Position in the list encodes layer size - 1.
  """
  all_allowed = []
  for i in range(1, num + 1):
    # Define the allowed moves recursively
    if i == 1:
      allowed = [(1, 1)]
    else:
      allowed = all_allowed[i - 2] + [(j, i) for j in range(1, i + 1)]
    all_allowed.append(allowed)
  return all_allowed


def get_random_move(allowed_moves):
  move_layer = np.random.randint(len(allowed_moves))
  move_indices = random.choice(allowed_moves[move_layer])
  move = (move_layer + 1,) + move_indices
  return move
