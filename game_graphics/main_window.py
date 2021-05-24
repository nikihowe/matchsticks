# (c) Nikolaus Howe 2021
import PySimpleGUI as sg

from game_graphics.game_window import GameWindow
from game import Game
from player import VisualHumanPlayer, TrivialPlayer, RandomPlayer, PretrainedPlayer
from arena import VisualArena


class MainWindow(object):

  def __init__(self):
    self.graph = sg.Graph(canvas_size=(500, 500), key='graph',
                          graph_bottom_left=(0, 500), graph_top_right=(500, 0),
                          enable_events=True,  # mouse click events
                          background_color='lightblue',
                          drag_submits=True)
    self.gw = None
    self.intro_layout = [[sg.Text(text="What's your name?", font=("Helvetica", 22)),
                          sg.Input(key='name', default_text='Human Player', font=("Helvetica", 22), size=(30, 1))],
                         [sg.Text("How big a game (# rows) would you like to play?", font=("Helvetica", 22)),
                          sg.Slider(key='num_layers', range=(3, 8), default_value=4, orientation='h',
                                    font=('Helvetica', 16), size=(25, 22))],
                         [sg.Text("Who plays first?", font=('Helvetica', 22)),
                          sg.Radio(key='human_first', text='Human', group_id="RADIO1", default=True, font=('Helvetica', 16)),
                          sg.Radio(text='Computer', group_id="RADIO1", font=('Helvetica', 16))],
                         [sg.Text("How hard an opponent would you like to play against?", font=('Helvetica', 22)),
                          sg.InputCombo(key='computer_player', values=('Same move every time', 'Random move every time',
                                                                  'Easy', 'Medium', 'Hard', 'Perfect'),
                                        default_value='Same move every time',
                                        font=('Helvetica', 16), size=(25, 22))],
                         [sg.Text(f'Your win count against this difficulty: {5}', font=('Helvetica', 16),
                                  justification='right')],  # TODO: make point to actual win count
                         [sg.Button('Start game!', font=('Helvetica', 22))]]
    self.game_layout = [
      [sg.Button('Start game!', font=('Helvetica', 22))],
      [self.graph]
    ]
    # TODO: eventually, let the user train players by themselves
    # self.training_layout = [[sg.Text(text="", font=("Helvetica", 22)),
    #                       sg.Input(key='name', default_text='Human Player', font=("Helvetica", 22), size=(30, 1))],
    #                      [sg.Text("How big a game (# rows) would you like to play?", font=("Helvetica", 22)),
    #                       sg.Slider(key='num_layers', range=(3, 8), default_value=4, orientation='h',
    #                                 font=('Helvetica', 16), size=(25, 22))],
    #                      [sg.Text("Who plays first?", font=('Helvetica', 22)),
    #                       sg.Radio(key='human_first', text='Human', group_id="RADIO1", default=True,
    #                                font=('Helvetica', 16)),
    #                       sg.Radio(text='Computer', group_id="RADIO1", font=('Helvetica', 16))],
    #                      [sg.Text("How hard an opponent would you like to play against?", font=('Helvetica', 22)),
    #                       sg.InputCombo(key='computer_player', values=('Same move every time', 'Random move every time',
    #                                                                    'Easy', 'Medium', 'Hard', 'Perfect'),
    #                                     default_value='Same move every time',
    #                                     font=('Helvetica', 16), size=(25, 22))],
    #                      [sg.Text(f'Your win count against this difficulty: {5}', font=('Helvetica', 16),
    #                               justification='right')],  # TODO: make point to actual win count
    #                      [sg.Button('Start game!', font=('Helvetica', 22))]]
    self.intro_window = sg.Window('Game Setup', self.intro_layout, finalize=True)
    self.playing_window = sg.Window('Matchsticks', self.game_layout, finalize=True)
    self.playing_window.hide()
    self.run_intro()

    # TODO: add types

  def run_intro(self):
    """
    Display the intro window, and record the user's inputs to set up a game.

    :return:
    """
    self.intro_window.un_hide()
    event, values = self.intro_window.read()
    print("event", event, values)
    g1 = Game(int(values['num_layers']))
    self.gw = GameWindow(game=g1, window=self.playing_window)

    human_player = VisualHumanPlayer(self.gw, values['name'])

    computer_player_type = values['computer_player']
    if computer_player_type == 'Same move every time':
      computer_player = TrivialPlayer()
    elif computer_player_type == 'Random move every time':
      computer_player = RandomPlayer()
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
    a1.play()

    self.playing_window.hide()
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
