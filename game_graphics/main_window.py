# (c) Nikolaus Howe 2021

import graphics as gfx
import PySimpleGUI as sg
from game import Game
from game_graphics.game_window import GameWindow
from game import Game
from player import VisualHumanPlayer, TrivialPlayer, RandomPlayer, PretrainedPlayer
from arena import VisualArena


class MainWindow(object):

  def __init__(self):
    # Define the window's contents
    layout = [[sg.Text(text="What's your name?", font=("Helvetica", 22)),
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
              [sg.Text(f'Your win count against this difficulty: {5}', font=('Helvetica', 16), justification='right')],  # TODO: make point to actual win count
              [sg.Button('Start game!', font=('Helvetica', 22))]]

    # Create the window
    window = sg.Window('~Matchsticks~', layout)

    # Display and interact with the Window
    event, values = window.read()

    g1 = Game(int(values['num_layers']))
    gw = GameWindow(game=g1)

    human_player = VisualHumanPlayer(gw, values['name'])

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

    window.close()

    a1 = VisualArena(g1, p1, p2, gw)
    a1.play()


if __name__ == "__main__":
  MainWindow()
