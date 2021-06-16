# (c) Nikolaus Howe 2021
from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
  from matchsticks.game_graphics.game_window import GameWindow

from matchsticks.utils import check_intersection
from matchsticks.game_graphics.row import Row
from matchsticks.game_graphics.matchstick import Matchstick
from matchsticks.game_types import Move, Line


class Pyramid(object):
  def __init__(self, rows: list[Row], gw: GameWindow) -> None:
    """
    A pyramid of rows of matchsticks.

    :param rows: the rows of matchsticks
    :param gw: the game window
    """
    self.rows = rows
    self.gw = gw
    self.inactive_sticks = []

  def draw(self) -> None:
    """
    Draw the pyramid.

    :return:
    """
    num_rows = len(self.rows)
    for i, row in enumerate(self.rows):
      row.draw(v_pos=self.gw.center[0] + (i - (num_rows - 1) / 2) * self.gw.v_spacing)

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

  def check_intersections(self, line: Line) -> list[Matchstick]:
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

    # First, check intersections with the inactive sticks
    for stick in self.inactive_sticks:
      if check_intersection(stick.line, line):
        return []

    # If there are none, then we're ok to check intersections with the active sticks
    for row in self.rows:
      row_intersections = row.check_intersections(line)
      if row_intersections:  # if it's not an empty list
        # Only save if there are no intersections with other rows.
        # Otherwise, ask for the human to give a new line.
        if not the_intersections:
          the_intersections = row_intersections
        else:
          return []
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
