# (c) Nikolaus Howe 2021
from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
  from matchsticks.game_graphics.game_window import GameWindow


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
    self.gw.pyramid.inactive_sticks.append(self)

  def draw(self, v_pos: float = None, h_pos: float = None) -> None:  # only uses v_pos and h_pos if not drawn before
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
    self.line = ((self.h_pos, self.v_pos - self.gw.stick_length / 2),
                 (self.h_pos, self.v_pos + self.gw.stick_length / 2))
    if self.is_active:
      stick_colour = 'black'
    else:
      stick_colour = 'red'

    self.gw.window['graph'].draw_line(*self.line, color=stick_colour, width=2)
