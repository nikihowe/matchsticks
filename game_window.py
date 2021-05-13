# (c) Nikolaus Howe 2021

import graphics as gfx

from overrides import overrides

from game import Game
from utils import check_intersection


class GameWindow(object):

  def __init__(self,
               game: Game,
               width=400,
               height=400,
               v_spacing=40,
               h_spacing=30,
               stick_length=30,
               stick_width=2):
    self.game = game
    self.win = gfx.GraphWin("Matchsticks", width, height)
    self.center = gfx.Point(width/2, height/2)
    self.v_spacing = v_spacing
    self.h_spacing = h_spacing
    self.stick_length = stick_length
    self.stick_width = stick_width
    self.pyramid = self.make_pyramid()
    self.main()

  def make_pyramid(self):
    state = self.game.get_state()
    pyramid_list = []
    for i, sticks_in_layer in enumerate(state):
      row_list = []
      for idx in range(sticks_in_layer):
        row_list.append(Matchstick(i+1, idx+1, self))
      row = Row(row_list, self)
      pyramid_list.append(row)
    return Pyramid(pyramid_list, self)

  def main(self):
    while self.game.is_still_on():
      self.draw()
      point1 = self.win.getMouse()
      point2 = self.win.getMouse()

      human_line = gfx.Line(point1, point2)

      intersections = self.pyramid.check_intersections(human_line)
      print("intersects", intersections)

      # If there are legal intersections, draw the line and update game logic.
      # Otherwise, ask the player to draw a new line.
      if intersections and all([s.is_active for s in intersections]):
        human_line.setWidth(2)
        human_line.setOutline('red')
        human_line.draw(self.win)
        for stick in intersections:
          stick.set_inactive()
      else:
        print("Please draw a line which satisfies the following:\n"
              "- intersects at least one match\n"
              "- stays entirely within one row\n"
              "- doesn't cross any already crossed-off matches")
      # here, do stuff to process the mouse clicks

  def draw(self):
    # This should take into account the current layers, if we want (option to always clean board or not)
    self.pyramid.draw()


class Pyramid(object):
  def __init__(self, rows: list, gw: GameWindow):
    self.rows = rows
    self.gw = gw

  def draw(self):
    num_rows = len(self.rows)
    for i, row in enumerate(self.rows):
      row.draw(v_pos=self.gw.center.x + (i - (num_rows - 1) / 2) * self.gw.v_spacing)

  def check_intersections(self, line: gfx.Line) -> list:
    the_intersections = None
    for row in self.rows:
      row_intersections = row.check_intersections(line)
      # TODO: will later move this check to sub-rows instead of rows
      if row_intersections:  # if it's not an empty list
        # Only save if there are no intersections with previous rows.
        # Otherwise, ask for the human to give a new line.
        if not the_intersections:
          the_intersections = row_intersections
        else:
          return []
    return the_intersections


# TODO: will have to create a sub-row object for once we have some crossed off
class Row(object):
  def __init__(self, matchsticks: list, gw: GameWindow):
    self.matchsticks = matchsticks
    self.gw = gw

  def draw(self, v_pos):
    num_sticks = len(self.matchsticks)
    for i, stick in enumerate(self.matchsticks):
      stick.draw(v_pos=v_pos,
                 h_pos=self.gw.center.y + (i - (num_sticks - 1) / 2) * self.gw.h_spacing)

  def check_intersections(self, line: gfx.Line):
    intersections = []
    for stick in self.matchsticks:
      if check_intersection(stick.line, line):
        # print("intersects with", stick)
        intersections.append(stick)
    return intersections


class Matchstick(object):
  def __init__(self, layer: int, idx: int, gw: GameWindow):
    self.layer = layer
    self.idx = idx
    self.line = None  # hasn't been drawn yet
    self.is_active = True
    self.gw = gw

  def __repr__(self):
    return f'Matchstick({self.layer}, {self.idx})'

  def set_inactive(self):
    self.is_active = False

  def draw(self, v_pos, h_pos):
    self.line = gfx.Line(gfx.Point(h_pos, v_pos - self.gw.stick_length / 2),
                         gfx.Point(h_pos, v_pos + self.gw.stick_length / 2))
    self.line.setWidth(self.gw.stick_width)
    if not self.is_active:
      self.line.setOutline('red')
    self.line.draw(self.gw.win)


if __name__ == '__main__':
  gw = GameWindow(Game(5))
