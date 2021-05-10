# (c) Nikolaus Howe

# Note that this is not a part of the bigger game, this is just a testing ground for RL agents
import numpy as np
from typing import Optional


names = ['one', 'two', 'three', 'four', 'five']


def corresponds(word: str, guessed: int) -> bool:
  return names[guessed - 1] == word


def get_possible_moves() -> list:
  return [1, 2, 3, 4, 5]


class Game(object):
  """
  A simple game where the goal is to learn the names of the first five digits
  """
  def __init__(self, word: Optional[str] = None) -> None:
    if word is None:
      word = np.random.choice(names)
    self.word = word

  def move(self, guessed: int) -> int:
    if not 1 <= guessed <= 5:
      print("guesses should be between 1 and 5 inclusive.")
      raise ValueError

    if corresponds(self.word, guessed):
      return 1
    else:
      return -1


class Agent(object):
  """
  A simple agent which will learn to play the game
  """
  def __init__(self) -> None:
    self.Q = {}
    self.rewards = []
    self.eps = 0.05
    self.history = []

  def policy(self, game_word) -> int:
    # Choose randomly self.eps of the time
    if np.random.uniform() < self.eps:
      return np.random.choice(get_possible_moves())
    else:
      q_row = list(self.Q[game_word].items())  # Turn the dict into a list
      q_row.sort(key=lambda x: x[1], reverse=True)  # Sort in descending order
      # print("sorted row is", q_row)
      return q_row[0][0]  # return the move with the highest Q value

  def move(self, game: Game) -> int:
    # If we've never seen this position, initialize it into the Q table
    if game.word not in self.Q:
      possible_moves = get_possible_moves()
      moves_and_values = list(map((lambda x: (x, 3.)), possible_moves))
      self.Q[game.word] = dict(moves_and_values)

    # Choose a move according to the policy
    move = self.policy(game.word)

    # Record state and move in history
    self.history.append((game.word, move))

    return move

  def receive_reward(self, reward: int) -> None:
    self.rewards.append(reward)

  def update(self) -> None:
    for i, (word, move) in reversed(list(enumerate(self.history))):
      self.Q[word][move] = self.Q[word][move] * 0.9 + 0.1 * self.rewards[i]

# TODO: move from a reward-per-move setting to a all-rewards-after-episode setting
if __name__ == "__main__":
  agent = Agent()
  episode_length = 10
  num_episodes = 30
  for _ in range(num_episodes):
    print("Q is", agent.Q)
    g1 = Game()
    for _ in range(episode_length):
      m = agent.move(g1)
      r = g1.move(m)
      agent.receive_reward(r)
    agent.update()

  print(agent.Q)
