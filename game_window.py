# (c) Nikolaus Howe 2021

import graphics as gfx
import time

from overrides import overrides

from game import Game
from utils import check_intersection


class GameWindow(object):

  def __init__(self,
               game: Game,
               width=450,
               height=450,
               v_spacing=40,
               h_spacing=25,
               stick_length=30,
               stick_width=3):
    self.game = game
    self.win = gfx.GraphWin("Matchsticks", width, height)
    self.center = gfx.Point(width/2, height/2)
    print("center", self.center)
    self.v_spacing = v_spacing
    self.h_spacing = h_spacing
    self.stick_length = stick_length
    self.stick_width = stick_width
    self.pyramid = self.make_pyramid()
    self.draw()
    # self.main()

  def game_over(self, human_won):
    end_text = gfx.Text(gfx.Point(self.center.x/2, 4/5*self.center.y), "")
    end_text.setSize(36)
    if human_won:
      end_text.setText('You win!')
      end_text.draw(self.win)
    else:
      end_text.setText('You lose!')
      end_text.draw(self.win)
    time.sleep(5)

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

  def draw_move(self, move):
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

  def get_human_move(self):
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

  def adjust(self, move: tuple) -> None:
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

  def check_intersections(self, line: gfx.Line) -> list:
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

  def __repr__(self):
    to_ret = []
    for row in self.rows:
      line = []
      for matchstick in row.matchsticks:
        line.append(str(matchstick))
      to_ret.append(' '.join(line))
    return '\n'.join(to_ret)


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
    self.v_pos = None
    self.h_pos = None
    self.is_active = True
    self.gw = gw

  def __repr__(self):
    return f'M({self.layer}, {self.idx})'

  def set_inactive(self):
    self.is_active = False

  def draw(self, v_pos=None, h_pos=None):  # only uses these if not already drawn before
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


if __name__ == '__main__':
  gw = GameWindow(Game(5))
