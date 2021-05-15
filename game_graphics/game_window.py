# (c) Nikolaus Howe 2021

import graphics as gfx
import time

from game import Game
from utils import check_intersection
from game_types import Move


class GameWindow(object):
  def __init__(self,
               game: Game,
               width: int = 450,
               height: int = 450,
               v_spacing: int = 40,
               h_spacing: int = 25,
               stick_length: int = 30,
               stick_width: int = 3) -> None:
    """
    A window in which a game of matchsticks can be drawn and played.

    :param game: the game to be drawn and played
    :param width: window width
    :param height: window height
    :param v_spacing: vertical space between rows of matchsticks
    :param h_spacing: horizontal space between matchsticks in the same row
    :param stick_length: how long to draw matchsticks
    :param stick_width: how wide to draw matchsticks
    """
    self.game = game
    self.win = gfx.GraphWin("Matchsticks", width, height)
    self.center = gfx.Point(width/2, height/2)
    self.v_spacing = v_spacing
    self.h_spacing = h_spacing
    self.stick_length = stick_length
    self.stick_width = stick_width
    self.pyramid = self.make_pyramid()
    self.draw()

  def game_over(self, human_won: bool) -> None:
    """
    End the game by printing a message on the screen.

    :param human_won: Whether or not the human won
    :return:
    """
    end_text = gfx.Text(gfx.Point(self.center.x/2, 4/5*self.center.y), "")
    end_text.setSize(36)
    if human_won:
      end_text.setText('You win!')
      end_text.draw(self.win)
    else:
      end_text.setText('You lose!')
      end_text.draw(self.win)
    time.sleep(5)

  def make_pyramid(self) -> 'Pyramid':
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

    crossing_line = gfx.Line(gfx.Point(left_stick.h_pos - self.h_spacing/4,
                                       left_stick.v_pos),
                             gfx.Point(right_stick.h_pos + self.h_spacing/4,
                                       right_stick.v_pos))
    crossing_line.setWidth(2)
    crossing_line.setOutline('red')
    crossing_line.draw(self.win)

    # Make the crossed off sticks red and remove them from the game
    for stick_idx in range(low_idx, high_idx + 1):
      stick = self.pyramid.rows[layer].matchsticks[stick_idx]
      stick.set_inactive()
      stick.draw(stick.v_pos, stick.h_pos)

    # Now, adjust pyramid according to the move
    self.pyramid.adjust(move)

  def get_human_move(self) -> Move:
    """
    Let the human click on the game window, and extract a move from the clicks.

    :return: the move
    """
    point1 = self.win.getMouse()
    point2 = self.win.getMouse()

    human_line = gfx.Line(point1, point2)

    intersections = self.pyramid.check_intersections(human_line)

    # If there are legal intersections, draw the line and update game logic.
    # Otherwise, ask the player to draw a new line.
    if intersections and all([s.is_active for s in intersections]):
      # print("the intersections are", intersections)
      # Draw the move
      human_line.setWidth(2)
      human_line.setOutline('red')
      human_line.draw(self.win)
      for stick in intersections:
        stick.set_inactive()
        stick.draw()

      # Send the move to the game
      row = intersections[0].layer
      low = intersections[0].idx
      high = intersections[-1].idx
      move = row, low, high
      # print("move was", move)

      # Make the crossed off sticks red and remove them from the game
      for stick_idx in range(low, high + 1):
        stick = self.pyramid.rows[row-1].matchsticks[stick_idx-1]
        stick.set_inactive()
        stick.draw(stick.v_pos, stick.h_pos)

      # Now, adjust pyramid according to the move
      self.pyramid.adjust(move)

      return move

    else:
      print("Please draw a line which satisfies the following:\n"
            "- intersects at least one match\n"
            "- stays entirely within one row\n"
            "- doesn't cross any already crossed-off matches")
      return self.get_human_move()  # Let them try again

  def draw(self) -> None:
    self.pyramid.draw()


class Matchstick(object):
  def __init__(self, layer: int, idx: int, gw: GameWindow) -> None:
    """
    A matchstick object to draw in the game window.

    :param layer: which layer is the matchstick in (1-indexed)
    :param idx: where in the layer is the matchstick (1-indexed)
    :param gw: the game window
    """
    self.layer = layer
    self.idx = idx
    self.line = None  # hasn't been drawn yet
    self.v_pos = None
    self.h_pos = None
    self.is_active = True
    self.gw = gw

  def __repr__(self) -> str:
    """
    String representation for printing.

    :return: the string representation
    """
    return f'M({self.layer}, {self.idx})'

  def set_inactive(self) -> None:
    """
    Make this matchstick inactive (when it's been crossed off).

    :return:
    """
    self.is_active = False

  def draw(self, v_pos: int = None, h_pos: int = None) -> None:  # only uses these if not already drawn before
    """
    Draw this matchstick.

    :param v_pos: the vertical position of the center of the stick
    :param h_pos: the horizontal position of the center of the stick
    :return:
    """
    if not self.v_pos:
      if not v_pos:
        raise Exception('At first drawing, you need to provide v_pos and h_pos')
      self.v_pos = v_pos
    if not self.h_pos:
      if not h_pos:
        raise Exception('At first drawing, you need to provide v_pos and h_pos')
      self.h_pos = h_pos
    self.line = gfx.Line(gfx.Point(self.h_pos, self.v_pos - self.gw.stick_length / 2),
                         gfx.Point(self.h_pos, self.v_pos + self.gw.stick_length / 2))
    self.line.setWidth(self.gw.stick_width)
    if not self.is_active:
      self.line.setOutline('red')
    self.line.draw(self.gw.win)


class Row(object):
  def __init__(self, matchsticks: list[Matchstick], gw: GameWindow) -> None:
    """
    A row of matchsticks.

    :param matchsticks: a list of matchsticks
    :param gw: the game window
    """
    self.matchsticks = matchsticks
    self.gw = gw

  def draw(self, v_pos: int) -> None:
    """
    Draw this row.

    :param v_pos: vertical position of the center of all matchsticks in the row.
    :return:
    """
    num_sticks = len(self.matchsticks)
    for i, stick in enumerate(self.matchsticks):
      stick.draw(v_pos=v_pos,
                 h_pos=self.gw.center.y + (i - (num_sticks - 1) / 2) * self.gw.h_spacing)

  def check_intersections(self, line: gfx.Line) -> list[Matchstick]:
    """
    Check for intersections of a given line segment with the matchsticks in this row.

    :param line: the line segment
    :return: a list of matchsticks which the line segment intersects with
    """
    intersections = []
    for stick in self.matchsticks:
      if check_intersection(stick.line, line):
        # print("intersects with", stick)
        intersections.append(stick)
    return intersections


class Pyramid(object):
  def __init__(self, rows: list[Row], gw: GameWindow) -> None:
    """
    A pyramid of rows of matchsticks.

    :param rows: the rows of matchsticks
    :param gw: the game window
    """
    self.rows = rows
    self.gw = gw

  def draw(self) -> None:
    """
    Draw the pyramid.

    :return:
    """
    num_rows = len(self.rows)
    for i, row in enumerate(self.rows):
      row.draw(v_pos=self.gw.center.x + (i - (num_rows - 1) / 2) * self.gw.v_spacing)

  def adjust(self, move: Move) -> None:
    """
    Adjust the rows, and the matchsticks in the rows, to correspond to
    the adjustment that happens to the state when a move is played.

    :param move: the move which is played
    :return:
    """
    layer, low_idx, high_idx = move
    row = self.rows.pop(layer-1)
    left_row_list = row.matchsticks[:low_idx-1]
    if left_row_list:
      left_row = Row(left_row_list, self.gw)
      self.rows.append(left_row)
    right_row_list = row.matchsticks[high_idx:]
    if right_row_list:
      right_row = Row(right_row_list, self.gw)
      self.rows.append(right_row)
    self.rows.sort(key=lambda x: len(x.matchsticks))

    # Now adjust all the sticks
    for layer, row in enumerate(self.rows):
      for i, stick in enumerate(row.matchsticks):
        stick.layer = layer + 1
        stick.idx = i + 1

  def check_intersections(self, line: gfx.Line) -> list[Matchstick]:
    """
    Check for intersections of a line segment with matchsticks in this pyramid.
    Note that all the intersections must be with the same row, and the line must
    be drawn within the vertical limits of the row, and the line cannot intersect
    any already crossed-off matchsticks. In the case of a violation of these
    requirements, the player is asked to try again.

    :param line: the line segment
    :return: a list of matchsticks which intersect with the line segment
    """
    the_intersections = None
    for row in self.rows:
      row_intersections = row.check_intersections(line)
      if row_intersections:  # if it's not an empty list
        # Only save if there are no intersections with previous rows.
        # Otherwise, ask for the human to give a new line.
        if not the_intersections:
          the_intersections = row_intersections
        else:
          return []
    # print("the intersections", the_intersections)
    return the_intersections

  def __repr__(self) -> str:
    """
    String representation for printing.

    :return: the string representation
    """
    to_ret = []
    for row in self.rows:
      line = []
      for matchstick in row.matchsticks:
        line.append(str(matchstick))
      to_ret.append(' '.join(line))
    return '\n'.join(to_ret)


if __name__ == '__main__':
  the_game_window = GameWindow(Game(5))