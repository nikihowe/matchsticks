# (c) Nikolaus Howe

# Note that this is not a part of the bigger game, this is just a testing ground for RL trained_agents
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
      moves_and_values = list(map((lambda x: (x, 0.)), possible_moves))
      self.Q[game.word] = dict(moves_and_values)

    # Choose a move according to the policy
    move = self.policy(game.word)

    # Record state and move in history
    self.history.append((game.word, move))

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


# Now our setting is one where the rewards are summed together and only given at the end of the episode
if __name__ == "__main__":
  agent = Agent()
  episode_length = 5
  num_episodes = 5000
  np.random.seed(0)
  all_final_rewards = []
  randomness = np.random.choice(names, num_episodes * episode_length)
  for j in range(num_episodes):
    # print("Q is", agent.Q)
    g1 = Game(randomness[j*episode_length])
    episode_reward = 0
    for i in range(episode_length):
      if i:
        agent.receive_reward(0)  # Always 0 except at the end, when agent gets the true amounts all smooshed together
        g1.word = randomness[j+i]
      m = agent.move(g1)
      r = g1.move(m)
      episode_reward += r
    agent.receive_reward(episode_reward)
    all_final_rewards.append(episode_reward)
    agent.update()
    agent.eps *= 0.999
    agent.end_episode()

  import matplotlib.pyplot as plt
  from scipy.signal import savgol_filter

  smoothed_rewards = savgol_filter(all_final_rewards, 101, 3)  # window size 51, polynomial order 3

  plt.plot(smoothed_rewards, 'o')
  plt.show()


