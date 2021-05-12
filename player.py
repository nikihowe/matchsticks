# (c) Nikolaus Howe 2021

import numpy as np
import pickle as pkl
import random
from abc import ABC, abstractmethod
from overrides import overrides

from game import Game


class Player(ABC):
  """
  An abstract class for defining players
  """

  def __init__(self, name: str = "Alice"):
    self.name = name

  @abstractmethod
  def move(self, game: Game):
    """
    Get the player to play a move among allowed_moves

    :param: The current game
    :return: A move in the format of an int 3-tuple
    """
    pass

  def receive_reward(self, reward: float):
    pass

  def update(self):
    pass

  def end_episode(self):
    pass

  def save_q(self, filename: str):
    print("Saving has not been implemented for this player")


class TrivialPlayer(Player):
  """
  A player which always plays the move (1, 1, 1)
  """

  @overrides
  def move(self, game: Game):
    return 1, 1, 1


class RandomPlayer(Player):
  """
  A player which always plays random moves.
  """

  @overrides
  def move(self, game: Game):
    return random.choice(game.get_allowed())


class MCPlayer(Player):
  """
  An on-policy first-visit MC control player.
  """

  @overrides
  def __init__(self, name='Alice') -> None:
    super().__init__(name=name)
    self.Q = {}
    self.rewards = []
    self.eps = 0.05
    self.history = []

  def policy(self, game: Game) -> int:
    # Choose randomly self.eps of the time
    if np.random.uniform() < self.eps:
      return random.choice(game.get_allowed())
    else:
      q_row = list(self.Q[game.get_state()].items())  # Turn the dict into a list
      q_row.sort(key=lambda x: x[1], reverse=True)  # Sort in descending order
      # print("sorted row is", q_row)
      return q_row[0][0]  # return the move with the highest Q value

  @overrides
  def move(self, game: Game) -> int:
    # If we've never seen this position, initialize it into the Q table
    game_state = game.get_state()
    if game_state not in self.Q:
      possible_moves = game.get_allowed()
      moves_and_values = list(map((lambda x: (x, 0.)), possible_moves))
      # print("setting moves and values", moves_and_values)
      self.Q[game_state] = dict(moves_and_values)

    # Choose a move according to the policy
    move = self.policy(game)

    # Record state and move in history
    self.history.append((game_state, move))

    return move

  def receive_reward(self, reward: float) -> None:
    self.rewards.append(reward)

  def update(self) -> None:
    discount = 0.9
    current_return = 0.
    # print("updating")
    # print("the history is", self.history)
    # print("the rewards are", self.rewards)
    for i, (word, move) in reversed(list(enumerate(self.history))):

      current_return = discount * current_return + self.rewards[i]

      # Check whether this state-action pair happened earlier
      if (word, move) in self.history[:i]:
        continue

      # Running average
      self.Q[word][move] = self.Q[word][move] * 0.9 + 0.1 * current_return

  def end_episode(self) -> None:
    self.history = []
    self.rewards = []

  def save_q(self, filename) -> None:
    with open(filename, 'wb') as f:
      pkl.dump(self.Q, f)

    print(f"Saved Q table as '{filename}'")


class PretrainedPlayer(Player):
  """
  A class which loads in a Q table
  """

  @overrides
  def __init__(self, q_filename, name=None):
    del name
    super().__init__(name=q_filename)
    try:
      with open(q_filename, 'rb') as f:
        self.Q = pkl.load(f)
    except Exception as e:
      print(f"Couldn't load file {q_filename}.")
      print("The exception was", e)

  @overrides
  def move(self, game: Game) -> int:
    # If we've never seen this position, initialize it into the Q table
    game_state = game.get_state()
    if game_state not in self.Q:
      possible_moves = game.get_allowed()
      moves_and_values = list(map((lambda x: (x, 0.)), possible_moves))
      # print("setting moves and values", moves_and_values)
      self.Q[game_state] = dict(moves_and_values)

    # Choose a move according to the policy
    move = self.policy(game)

    return move

  def policy(self, game: Game) -> int:
    q_row = list(self.Q[game.get_state()].items())  # Turn the dict into a list
    q_row.sort(key=lambda x: x[1], reverse=True)  # Sort in descending order
    # print("sorted row is", q_row)
    return q_row[0][0]  # return the move with the highest Q value


class HumanPlayer(Player):

  @overrides
  def __init__(self, name='Human'):
    super().__init__(name=name)

  @overrides
  def move(self, game: Game):
    move_str = input("Input your move in the form (layer, low, high).\n")
    try:
      move = tuple(map(int, move_str[1:-1].split(', ')))
    except Exception as e:
      print("Couldn't read your move.")
      print("The exception was", e)
      raise SystemExit

    assert (
      len(move) == 3
      and isinstance(move[0], int)
      and isinstance(move[1], int)
      and isinstance(move[2], int)
      and game.is_allowed(move)
    )

    return move
