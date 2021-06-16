# (c) Nikolaus Howe 2021
from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
  from matchsticks.game_graphics.game_window import GameWindow

from matchsticks.utils import check_intersection
from matchsticks.game_graphics.matchstick import Matchstick
from matchsticks.game_types import Line


class Row(object):
  def __init__(self, matchsticks: list[Matchstick], gw: GameWindow) -> None:
    """
    A row of matchsticks.

    :param matchsticks: a list of matchsticks
    :param gw: the game window
    """
    self.matchsticks = matchsticks
    self.gw = gw

  def draw(self, v_pos: float) -> None:
    """
    Draw this row.

    :param v_pos: vertical position of the center of all matchsticks in the row.
    :return:
    """
    num_sticks = len(self.matchsticks)
    for i, stick in enumerate(self.matchsticks):
      stick.draw(v_pos=v_pos,
                 h_pos=self.gw.center[1] + (i - (num_sticks - 1) / 2) * self.gw.h_spacing)

  def check_intersections(self, line: Line) -> list[Matchstick]:
    """
    Check for intersections of a given line segment with the matchsticks in this row.

    :param line: the line segment
    :return: a list of matchsticks which the line segment intersects with
    """
    intersections = []
    for stick in self.matchsticks:
      if check_intersection(stick.line, line):
        intersections.append(stick)
    return intersections
