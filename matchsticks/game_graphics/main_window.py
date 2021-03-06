# (c) Nikolaus Howe 2021
import PySimpleGUI as sg

from typing import Optional

from matchsticks.arena import VisualArena
from matchsticks.game import Game
from matchsticks.game_graphics.game_window import GameWindow
from matchsticks.player import PerfectPlayer, PretrainedPlayer, RandomPlayer, VisualHumanPlayer
from matchsticks.utils import BackButtonException, ClosedWindowException


def make_intro_window(last_settings: Optional[dict] = None):
  if last_settings is None:
    intro_layout = [[sg.Text("How big a game (# rows) would you like to play?", font=("Helvetica", 22)),
                     sg.Slider(key='num_layers', range=(3, 6), default_value=4, orientation='h',
                               font=('Helvetica', 16), size=(14, 22))],
                    [sg.Text("Who plays first?", font=('Helvetica', 22)),
                     sg.Radio(key='human_first', text='Human', group_id="RADIO1", default=True, font=('Helvetica', 16)),
                     sg.Radio(text='Computer', group_id="RADIO1", default=False, font=('Helvetica', 16))],
                    [sg.Text("How hard an opponent would you like to play against?", font=('Helvetica', 22)),
                     sg.InputCombo(key='computer_player',
                                   values=('Plays randomly', 'Easy', 'Medium', 'Hard', 'Perfect'),
                                   default_value='Easy',
                                   font=('Helvetica', 16), size=(14, 22))],
                    # [sg.Text(f'Your win count against this difficulty: {5}', font=('Helvetica', 16),
                    #          justification='right')],  # NOTE: this hasn't been set up yet
                    [sg.Button('Start game!', font=('Helvetica', 22))]]
  else:
    intro_layout = [[sg.Text("How big a game (# rows) would you like to play?", font=("Helvetica", 22)),
                     sg.Slider(key='num_layers', range=(3, 6), default_value=last_settings['num_layers'],
                               orientation='h', font=('Helvetica', 16), size=(14, 22))],
                    [sg.Text("Who plays first?", font=('Helvetica', 22)),
                     sg.Radio(key='human_first', text='Human', group_id="RADIO1", default=last_settings['human_first'],
                              font=('Helvetica', 16)),
                     sg.Radio(text='Computer', group_id="RADIO1", default=(not last_settings['human_first']),
                              font=('Helvetica', 16))],
                    [sg.Text("How hard an opponent would you like to play against?", font=('Helvetica', 22)),
                     sg.InputCombo(key='computer_player',
                                   values=('Plays randomly', 'Easy', 'Medium', 'Hard', 'Perfect'),
                                   default_value=last_settings['computer_player'],
                                   font=('Helvetica', 16), size=(14, 22))],
                    # [sg.Text(f'Your win count against this difficulty: {5}', font=('Helvetica', 16),
                    #          justification='right')],  # NOTE: this hasn't been set up yet
                    [sg.Button('Start game!', font=('Helvetica', 22))]]

  return sg.Window('Game Setup', intro_layout, finalize=True)


def make_playing_window():
  graph = sg.Graph(canvas_size=(300, 300), key='graph',
                   graph_bottom_left=(0, 300), graph_top_right=(300, 0),
                   enable_events=True,  # mouse click events
                   background_color='lightblue',
                   drag_submits=True)
  game_layout = [
    [graph],
    [sg.Button('Quit game', key='back', font=('Helvetica', 18))],
  ]
  return sg.Window('Matchsticks', game_layout, finalize=True)


class MainWindow(object):
  # TODO: idea: let the user train the agents by themself?
  # TODO: implement a better learning algorithm?

  def __init__(self) -> None:
    """
    The first window that the user sees. They can use it to set up a game.

    """
    self.gw = None
    self.last_settings = None
    self.intro_window = None
    self.playing_window = None
    self.run_intro()

  def run_intro(self) -> None:
    """
    Display the intro window, and record the user's inputs to set up a game.

    :return:
    """
    self.intro_window = make_intro_window(last_settings=self.last_settings)
    self.playing_window = make_playing_window()
    self.playing_window.hide()

    event, values = self.intro_window.read()
    print("event", event, values)

    if event == sg.WIN_CLOSED or event == 'Exit':
      print("closing the window!")
      self.intro_window.close()
      return

    # Save the settings so that they are the default for next time
    self.last_settings = values

    g1 = Game(int(values['num_layers']))
    self.gw = GameWindow(game=g1, window=self.playing_window)

    human_player = VisualHumanPlayer(self.gw, "human")

    computer_player_type = values['computer_player']
    if computer_player_type == 'Plays randomly':
      computer_player = RandomPlayer()
    elif computer_player_type == "Easy":
      computer_player = PretrainedPlayer("matchsticks/trained_agents/easy.player")
    elif computer_player_type == "Medium":
      computer_player = PretrainedPlayer("matchsticks/trained_agents/medium.player")
    elif computer_player_type == "Hard":
      computer_player = PretrainedPlayer("matchsticks/trained_agents/hard.player")
    elif computer_player_type == 'Perfect':
      computer_player = PerfectPlayer()
    else:
      raise ValueError("that kind of player isn't ready yet")

    if values['human_first']:
      p1 = human_player
      p2 = computer_player
    else:
      p1 = computer_player
      p2 = human_player

    self.intro_window.hide()

    a1 = VisualArena(g1, p1, p2, self.gw)
    self.run_play(a1)

  def run_play(self, a1: VisualArena):
    """
    Run a game window, showing computer moves and taking input from the user.

    :param a1: the VisualArena of the active game
    :return:
    """
    self.playing_window['graph'].erase()
    self.playing_window.un_hide()
    self.gw.draw()

    try:
      a1.play()
    except BackButtonException as _:
      print("We caught a CWCError, so we're closing the window and returning to main menu")
    except ClosedWindowException as _:
      print("the window was closed, so we don't need to close the window")
      print("but we will anyway")

    self.playing_window.close()
    self.run_intro()

    # g1 = Game(int(values['num_layers']))
    # gw = GameWindow(game=g1)
    #
    # human_player = VisualHumanPlayer(gw, values['name'])
    #
    # computer_player_type = values['computer_player']
    # if computer_player_type == 'Same move every time':
    #   computer_player = TrivialPlayer()
    # elif computer_player_type == 'Random move every time':
    #   computer_player = RandomPlayer()
    # else:
    #   raise ValueError("that kind of player isn't ready yet")
    #
    # if values['human_first']:
    #   p1 = human_player
    #   p2 = computer_player
    # else:
    #   p1 = computer_player
    #   p2 = human_player
    #
    # window.close()
    #
    # a1 = VisualArena(g1, p1, p2, gw)
    # a1.play()


if __name__ == "__main__":
  MainWindow()
