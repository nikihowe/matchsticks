# (c) Nikolaus Howe 2021

import numpy as np
import pickle as pkl
import random
from abc import ABC, abstractmethod
from overrides import overrides

from game import Game
from game_graphics.game_window import GameWindow
from utils import get_nim_sum, imagine_move

from game_types import Move


class Player(ABC):
  def __init__(self, name: str = "Alice") -> None:
    """
    An abstract class for defining players

    :param name: the name given to this player
    """
    self.name = name

  @abstractmethod
  def move(self, game: Game) -> Move:
    """
    Get the player to play a move among allowed_moves

    :param: The current game
    :return: A move in the format of an int 3-tuple
    """
    pass

  def receive_reward(self, reward: float) -> None:
    """
    Tell the player what reward they got for the turn.

    :param reward: The instantaneous reward
    :return:
    """
    pass

  def update_and_end_episode(self) -> None:
    """
    Tell the player that the game is over, and it's time to update
    their beliefs about which moves are best.

    :return:
    """
    pass

  def save_q(self, filename: str) -> None:
    """
    Tell the player to save their Q table

    :param filename: the filename to save it as
    :return:
    """
    print("Saving has not been implemented for this player")

  def is_visual_human(self) -> bool:
    """
    Check whether or not the player is a human playing using the GUI.

    :return: player is human AND player is using GUI
    """
    return isinstance(self, VisualHumanPlayer)


class TrivialPlayer(Player):
  """
  A player which always plays the move (1, 1, 1)
  """

  @overrides
  def move(self, game: Game) -> Move:
    """
    Cross one stick off the smallest sub-row

    :param game: the game
    :return: the move
    """
    return 1, 1, 1


class RandomPlayer(Player):
  """
  A player which always plays random moves.
  """

  @overrides
  def move(self, game: Game) -> Move:
    """
    Chooses a move uniformly at random.

    :param game: the game
    :return: the move
    """
    return random.choice(game.get_allowed())


class MCPlayer(Player):
  @overrides
  def __init__(self, name='Alice') -> None:
    """
    An on-policy first-visit MC control player.

    :param name: name to give the player
    """
    super().__init__(name=name)
    self.Q = {}
    self.rewards = []
    self.eps = 0.05
    self.history = []

  def policy(self, game: Game) -> Move:
    """
    An epsilon-greedy policy using a Q table for state-action value estimation.

    :param game: the game
    :return: the chosen move
    """
    # Choose randomly self.eps of the time
    if np.random.uniform() < self.eps:
      return random.choice(game.get_allowed())
    else:
      q_row = list(self.Q[game.get_state()].items())  # Turn the dict into a list
      q_row.sort(key=lambda x: x[1], reverse=True)  # Sort in descending order
      # print("sorted row is", q_row)
      return q_row[0][0]  # return the move with the highest Q value

  @overrides
  def move(self, game: Game) -> Move:
    """
    Chose a move according to an epsilon-greedy policy,
    record it in the episode history, and then play it.

    :param game: the game
    :return: the move
    """
    # If we've never seen this position, initialize it into the Q table
    game_state = game.get_state()
    if game_state not in self.Q:
      possible_moves = game.get_allowed()
      moves_and_values = list(map((lambda x: (x, 0.1)), possible_moves))
      # print("setting moves and values", moves_and_values)
      self.Q[game_state] = dict(moves_and_values)

    # Choose a move according to the policy
    move = self.policy(game)

    # Record state and move in history
    self.history.append((game_state, move))

    return move

  def receive_reward(self, reward: float) -> None:
    """
    Store the reward from this timestep, to be learned from later.

    :param reward: the reward at this time
    :return:
    """
    self.rewards.append(reward)

  def update_and_end_episode(self) -> None:
    """
    Use the stored state-move history, and reward history, to
    update the Q-table according to an exponential averaging approach.
    Then, clear the state-move history and reward history.

    :return:
    """
    discount = 0.9
    current_return = 0.
    # print("updating")
    # print("the history is", self.history)
    # print("the rewards are", self.rewards)
    for i, (word, move) in reversed(list(enumerate(self.history))):

      current_return = discount * current_return + self.rewards[i]

      # Check whether this state-action pair happened earlier
      # NOTE: in matchsticks, this can never happen
      # if (word, move) in self.history[:i]:
      #   continue

      # Running average
      self.Q[word][move] = self.Q[word][move] * 0.9 + 0.1 * current_return

    # End the episode by clearing histories
    self.history = []
    self.rewards = []

  def save_q(self, filename: str = None) -> None:
    """
    Save the Q-table to disk, for future loading.

    :param filename: what to save it as
    :return:
    """
    if not filename:
      filename = self.name

    with open(filename, 'wb') as f:
      pkl.dump(self.Q, f)

    print(f"Saved Q table as '{filename}'")


class PretrainedPlayer(Player):
  @overrides
  def __init__(self, q_filename: str, name: str = None) -> None:
    """
    Like the MCPlayer, but loads in a Q-table instead, and doesn't explore or learn.

    :param q_filename: filename of the piclked Q-table
    :param name: name to give the player
    """
    super().__init__(name=q_filename if not name else name)
    try:
      with open(q_filename, 'rb') as f:
        self.Q = pkl.load(f)
    except Exception as e:
      print(f"Couldn't load file {q_filename}.")
      print("The exception was", e)

  def policy(self, game: Game) -> Move:
    """
    Choose a move greedily according to the Q-table.

    :param game: the game
    :return: the best move, according to the Q-table
    """
    q_row = list(self.Q[game.get_state()].items())  # Turn the dict into a list
    random.shuffle(q_row)
    q_row.sort(key=lambda x: x[1], reverse=True)  # Sort in descending order
    # print("sorted row is", q_row)
    return q_row[0][0]  # return the move with the highest Q value

  @overrides
  def move(self, game: Game) -> Move:
    """
    Choose a move using a greedy policy, and play it.

    :param game: the game
    :return: the move
    """
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


class HumanPlayer(Player):
  @overrides
  def __init__(self, name: str = 'Human') -> None:
    """
    A human player, who plays through the CLI.

    :param name: the name for this player
    """
    super().__init__(name=name)

  @overrides
  def move(self, game: Game) -> Move:
    """
    Ask the player for a move in the CLI.

    :param game:
    :return:
    """
    move_str = input("Input your move in the form (layer, low, high).\n")
    try:
      move = Move(map(int, move_str[1:-1].split(', ')))
      if not isinstance(move, tuple):
        raise Exception('not a tuple')
      if not len(move) == 3:
        raise Exception('incorrect format')
    except Exception as e:
      print("Couldn't read your move. Please try again, making sure it's in the right format.")
      print(f"By the way, the exception was '{e}'")
      return self.move(game)

    return move


class VisualHumanPlayer(HumanPlayer):
  @overrides
  def __init__(self, gw: GameWindow, name='Human') -> None:
    """
    A human player which plays through the GUI.

    :param gw: the game window
    :param name: the name for this player
    """
    self.gw = gw
    super().__init__(name)

  @overrides
  def move(self, game: Game) -> Move:  # TODO: remove passed game, make attribute
    """
    Get a move from the human through the GUI, and play it.

    :param game: the game
    :return: the move
    """
    the_move = self.gw.get_and_play_human_move()
    # print("the human moved", the_move)
    return the_move


class PerfectPlayer(Player):  # TODO: add tests for this player
  @overrides
  def move(self, game: Game) -> Move:
    # TODO: docstring
    cur_nim_sum = get_nim_sum(game.get_state())
    allowed_moves = game.get_allowed()
    random.shuffle(allowed_moves)  # So it doesn't always play the same thing
    if cur_nim_sum == 0:  # There is no good move to play, so choose one at random
      return random.choice(allowed_moves)
    else:
      zero_nim_sum_move = None
      for move in allowed_moves:
        resulting_state = imagine_move(game.get_state(), move)
        move_nim_sum = get_nim_sum(resulting_state)
        # Check for game-ending move, and play immediately
        if move_nim_sum == 1 and all(num == 1 for num in resulting_state):
          return move
        # Store zero move, but don't play, in case there is a game-ending move
        elif move_nim_sum == 0 and zero_nim_sum_move is None:
          zero_nim_sum_move = move

      # Play the zero-preserving move, if present
      if zero_nim_sum_move is not None:
        return zero_nim_sum_move

      # If we get here, it means that we didn't find an appropriate move,
      # so play at random
      print("I think we should never get here?")
      print("state:", game.get_state())
      print("nim sum:", cur_nim_sum)
      return random.choice(allowed_moves)


if __name__ == '__main__':
  s = get_nim_sum((5, 1, 2, 2))
  print(s)
