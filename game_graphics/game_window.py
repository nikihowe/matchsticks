# (c) Nikolaus Howe 2021
import PySimpleGUI as sg

from game_graphics.pyramid import Pyramid
from game_graphics.row import Row
from game_graphics.matchstick import Matchstick
from game import Game
from utils import shorten_line
from game_types import Move


class GameWindow(object):
  def __init__(self,
               game: Game,
               window: sg.Window,
               v_spacing: int = 40,
               h_spacing: int = 25,
               stick_length: int = 30,
               stick_width: int = 3) -> None:
    """
    A window in which a game of matchsticks can be drawn and played.

    :param game: the game to be drawn and played
    :param v_spacing: vertical space between rows of matchsticks
    :param h_spacing: horizontal space between matchsticks in the same row
    :param stick_length: how long to draw matchsticks
    :param stick_width: how wide to draw matchsticks
    """
    self.game = game
    self.window = window
    self.width, self.height = window['graph'].CanvasSize
    self.center = (self.width/2, self.height/2)  # Because we set the coordinates to be a unit square
    self.v_spacing = v_spacing
    self.h_spacing = h_spacing
    self.stick_length = stick_length
    self.stick_width = stick_width
    self.pyramid = self.make_pyramid()
    self.gave_warning = False  # Only print the helper message once

  def game_over(self, human_won: bool) -> None:
    """
    End the game by printing a message on the screen.

    :param human_won: Whether or not the human won
    :return:
    """
    # end_text = gfx.Text(gfx.Point(self.center.x/2, 4/5*self.center
    # end_text.setSize(36)
    if human_won:
      print("Human wins!")
      # end_text.setText('You win!')
      # end_text.draw(self.win)
    else:
      print("Computer wins!")
      # end_text.setText('You lose!')
      # end_text.draw(self.win)
    # time.sleep(5)

  def make_pyramid(self) -> Pyramid:
    """
    Construct the pyramid of rows of matchsticks of this game window.

    :return:
    """
    state = self.game.get_state()
    pyramid_list = []
    for i, sticks_in_layer in enumerate(state):
      row_list = []
      for idx in range(sticks_in_layer):
        row_list.append(Matchstick(i+1, idx+1, self))
      row = Row(row_list, self)
      pyramid_list.append(row)
    return Pyramid(pyramid_list, self)

  def draw_move(self, move: Move) -> None:
    """
    Draw a move (from the computer) on the current pyramid.

    :param move: the move
    :return:
    """
    layer, low_idx, high_idx = move

    # Set the indices correctly
    low_idx -= 1
    high_idx -= 1
    layer -= 1

    # Draw the horizontal line
    left_stick = self.pyramid.rows[layer].matchsticks[low_idx]
    right_stick = self.pyramid.rows[layer].matchsticks[high_idx]

    crossing_line = ((left_stick.h_pos - self.h_spacing/4, left_stick.v_pos),
                     (right_stick.h_pos + self.h_spacing/4, right_stick.v_pos))
    self.window['graph'].draw_line(*crossing_line, color='red', width=2)

    # Make the crossed off sticks red and remove them from the game
    for stick_idx in range(low_idx, high_idx + 1):
      stick = self.pyramid.rows[layer].matchsticks[stick_idx]
      stick.set_inactive()
      stick.draw(stick.v_pos, stick.h_pos)

    # Update the window immediately afterwards
    self.window.refresh()

  def get_human_move(self) -> list[Matchstick]:
    """
    Get a move from the human by listening for mouse clicks on the window.
    If a move is detected, check to make sure it is allowed. If it is,
    then return it; otherwise, keep waiting for a move.

    :return: line segment start point, line segment end point, list of sticks with which the segment intersects
    """
    graph = self.window['graph']
    dragging = False
    start_point = end_point = current_line = None
    while True:
      event, values = self.window.read()
      # print("the event was", event, values)
      if event == "graph":
        x, y = values["graph"]
        if not dragging:
          start_point = (x, y)
          dragging = True
        else:
          end_point = (x, y)
        if current_line:
          graph.delete_figure(current_line)
        if None not in (start_point, end_point):
          current_line = graph.draw_line(start_point, end_point, color='red', width=2)
      elif event == "graph+UP":
        # Check the intersections. If they are good, play the move.
        # Otherwise, fall through and keep trying to get a move.
        # print("the start and end point are", start_point, end_point)
        if start_point is None or end_point is None:
          continue
        intersections = self.pyramid.check_intersections((start_point, end_point))
        print("the intersections are", intersections)
        if intersections and all([s.is_active for s in intersections]):
          # Shorten the line to make it more visually pleasing
          start_point, end_point = shorten_line((start_point, end_point), intersections, self)
          graph.delete_figure(current_line)
          current_line = graph.draw_line(start_point, end_point, color='red', width=2)

          # Return the intersections of this line
          return intersections
        else:
          graph.delete_figure(current_line)
          start_point, end_point = None, None
          dragging = False
          if not self.gave_warning:
            print("Please draw a line which satisfies the following:\n"
                  "- intersects at least one match\n"
                  "- stays entirely within one row\n"
                  "- doesn't cross any already crossed-off matches")
            self.gave_warning = True
      # TODO: make an exception for back and an exception for closed window
      elif event == 'back':
        print("going back to the setup window")
        break
      elif event == sg.WIN_CLOSED or event == 'Exit':
        print("we're closing the window")
        self.game.end()
        self.window.close()
        break

  def get_and_play_human_move(self) -> Move:
    """
    Call get_human_move to extract a move from mouse clicks. Then,
    play that move, update the drawing, and return the move.

    :return: the move
    """
    intersections = self.get_human_move()

    if intersections is None:
      return None  # game is over TODO: fix this

    # Update the colour of the crossed_off sticks
    for stick in intersections:
      stick.set_inactive()
      stick.draw()

    # Update the window for faster animation
    self.window.refresh()

    # Send the move to the game
    row = intersections[0].layer
    low = intersections[0].idx
    high = intersections[-1].idx
    move = row, low, high
    # print("move was", move)
    return move

  def draw(self) -> None:
    self.pyramid.draw()


# if __name__ == '__main__':
#   layout = [
#     [sg.Button('Start game!', font=('Helvetica', 22))],
#     [sg.Graph(canvas_size=(500, 500), key='graph',
#               graph_bottom_left=(0, 500), graph_top_right=(500, 0),
#               enable_events=True,  # mouse click events
#               background_color='lightblue',
#               drag_submits=True)]
#   ]
#   window = sg.Window('Canvas test', layout, finalize=True)
#   graph = window['graph']
#
#   the_game_window = GameWindow(Game(5))
#   # the_game_window.graph.draw_line((0.1, 0.1), (0.5, 0.5), color='black', width=2)
#
#   dragging = False
#   start_point = end_point = current_line = None
#   while True:
#     event, values = window.read()
#     if event == "graph":
#       x, y = values["graph"]
#       if not dragging:
#         start_point = (x, y)
#         dragging = True
#       else:
#         end_point = (x, y)
#       if current_line:
#           graph.delete_figure(current_line)
#       if None not in (start_point, end_point):
#         current_line = graph.draw_line(start_point, end_point, color='red', width=2)
#     elif event == "graph+UP":
#       # Tell the game to register the line
#       the_game_window.get_human_move(start_point, end_point)
#       graph.delete_figure(current_line)
#       start_point, end_point = None, None
#       dragging = False
#     elif event == sg.WIN_CLOSED or event == 'Exit':
#       break
