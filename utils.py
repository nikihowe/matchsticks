# (c) Nikolaus Howe 2021
from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
  from game_graphics.game_window import Matchstick, GameWindow

from typing import Optional

from game_types import Point, Line, Move


# NOTE: consider storing this somewhere for big games
def generate_allowed(num: int = 100) -> list[list[tuple[int, int]]]:
  """
  Generate all allowed moves for layers of length up to num.

  :param num: Up to which size of layer to consider (counts even and odd).
  :return: A list of allowed moves, in the format (low_idx, high_idx).
            Position in the list encodes layer size - 1.
  """
  all_allowed = []
  for i in range(1, num + 1):
    # Define the allowed moves recursively
    if i == 1:
      allowed = [(1, 1)]
    else:
      allowed = all_allowed[i - 2] + [(j, i) for j in range(1, i + 1)]
    all_allowed.append(allowed)
  return all_allowed


def get_line_coefficients(line: Line) -> Optional[tuple[float, float]]:
  """
  Given a line, get its coefficients a and b. If the line is vertical, return None.

  :param line: the line
  :return: the a and b coefficients of the line
  """
  (x1, y1), (x2, y2) = line

  # Check for vertical line.
  if x2 == x1:
    return None

  a = (y2 - y1) / (x2 - x1)
  b = -x1 * (y2 - y1) / (x2 - x1) + y1

  return a, b


def check_point_within_segments(line1: Line, line2: Line, point: Point):
  """
  Given two line segments and the intersection point of the corresponding lines,
  check whether the intersection point is within the line segments themselves

  :param line1: the first line segment
  :param line2: the second line segment
  :param point: the point of intersection
  :return: whether or not the point of intersection is within the line segments
  """
  ((x11, y11), (x12, y12)) = line1
  ((x21, y21), (x22, y22)) = line2
  xi, yi = point
  they_intersect = (
            (x11 <= xi <= x12 or x12 <= xi <= x11)
            and
            (x21 <= xi <= x22 or x22 <= xi <= x21)
            and
            (y11 <= yi <= y12 or y12 <= yi <= y11)
            and
            (y21 <= yi <= y22 or y22 <= yi <= y21)
    )
  return they_intersect


def get_intersection_point(vertical_line: Line, other_line: Line) -> Optional[Point]:
  """
  Find the intersection point between two line segments. Note that the line must be pretty.

  :param vertical_line: The first line segment. Guaranteed to be vertical.
  :param other_line: The second line segment.
  :return: The point of intersection.
  """

  # Extract the points composing the lines
  (vertical_x1, vertical_y1), (vertical_x2, vertical_y2) = vertical_line
  (other_x1, other_y1), (other_x2, other_y2) = other_line

  # Check for vertical line. If vertical, then no intersection.
  if other_x2 == other_x1:
    return None

  # Get the coefficients of the non-vertical line
  line_coefficients = get_line_coefficients(other_line)
  if line_coefficients is None:
    return None
  other_a, other_b = line_coefficients

  x_intersect = vertical_x1
  y_intersect = other_a * vertical_x1 + other_b
  intersection_point = x_intersect, y_intersect

  they_intersect = check_point_within_segments(vertical_line, other_line, intersection_point)
  if not they_intersect:
    return None

  return x_intersect, y_intersect


def check_intersection(vertical_line: Line, other_line: Line) -> bool:
  """
  Check for intersection between two line segments.

  :param vertical_line: The first line segment. Guaranteed to be vertical.
  :param other_line: The second line segment.
  :return: Whether or not they intersect.
  """

  intersection = get_intersection_point(vertical_line, other_line)

  return not not intersection


def get_nim_sum(state: tuple[int, ...]) -> int:
  """
  Get the nim sum of a position. See https://www.archimedes-lab.org/How_to_Solve/Win_at_Nim.html

  :param state: the state of the game
  :return: the nim sum of the current position
  """
  cur_sum = 0
  for n in state:
    cur_sum ^= n
  return cur_sum


def imagine_move(state: tuple[int, ...], move: Move) -> tuple[int, ...]:
  """
  Imagine the resulting state after taking a move

  :param state: the current state of the game
  :param move: the move
  :return: the new state of the game
  """
  cur_state = list(state)
  layer_i, low_idx, high_idx = move

  # Make the layer 0-indexed
  layer_i -= 1

  # Imagine performing move
  active_layer = cur_state.pop(layer_i)
  left_result = low_idx - 1
  right_result = active_layer - high_idx
  if left_result > 0:
    cur_state.append(left_result)
  if right_result > 0:
    cur_state.append(right_result)

  return tuple(cur_state)


def shorten_line(line: Line, intersections: list[Matchstick], gw: GameWindow) -> Line:
  """
  Shorten a line so that it fits nicely within the row and doesn't get too close to adjacent sticks when drawn

  :param line: the line to shorten
  :param intersections: the sticks that the line intersects with
  :param gw: the game window
  :return: the shortened line
  """
  # Get the smallest and largest x coordinates of the intersected sticks
  smallest_stick_x = get_min_x(intersections)
  largest_stick_x = get_max_x(intersections)

  # All the sticks are on the same row, so they all have the same y coordinates
  y_low = intersections[0].v_pos - gw.stick_length / 2
  y_high = intersections[0].v_pos + gw.stick_length / 2

  # Adjust the x and y coordinates
  new_line = chop_y(line, y_low, y_high)
  new_line = chop_x(new_line, smallest_stick_x - gw.h_spacing/3, largest_stick_x + gw.h_spacing/3)

  return new_line


def chop_y(line: Line, low_y: float, high_y: float) -> Line:
  """
  Chop a line segment between two horizontal lines

  :param line: the line segment to chop
  :param low_y: the lower y position to chop at
  :param high_y: the upper y position to chop at
  :return: the newly chopped line segment
  """
  (x1, y1), (x2, y2) = line
  if y2 < y1:
    line = (x2, y2), (x1, y1)

  a, b = get_line_coefficients(line)
  new_low_y = max(low_y, line[0][1])
  new_high_y = min(high_y, line[1][1])

  new_low_x = 1/a * (new_low_y - b)
  new_high_x = 1/a * (new_high_y - b)

  new_line = (new_low_x, new_low_y), (new_high_x, new_high_y)

  return new_line


def chop_x(line: Line, low_x: float, high_x: float) -> Line:
  """
    Chop a line segment between two vertical lines

    :param line: the line segment to chop
    :param low_x: the lower x position to chop at
    :param high_x: the upper x position to chop at
    :return: the newly chopped line segment
    """
  (x1, y1), (x2, y2) = line
  if x2 < x1:
    line = (x2, y2), (x1, y1)

  a, b = get_line_coefficients(line)
  new_low_x = max(low_x, line[0][0])
  new_high_x = min(high_x, line[1][0])

  new_low_y = a * new_low_x + b
  new_high_y = a * new_high_x + b

  new_line = (new_low_x, new_low_y), (new_high_x, new_high_y)

  return new_line


def get_min_x(sticks: list[Matchstick]) -> float:
  """
  Get the minimum x coordinate among a list of sticks

  :param sticks: a list of sticks
  :return: the minimum x coordinate
  """
  min_x = None
  for stick in sticks:
    if min_x is None or stick.h_pos < min_x:
      min_x = stick.h_pos
  return min_x


def get_max_x(sticks: list[Matchstick]) -> float:
  """
    Get the maximum x coordinate among a list of sticks

    :param sticks: a list of sticks
    :return: the maximum x coordinate
    """
  max_x = None
  for stick in sticks:
    if max_x is None or stick.h_pos > max_x:
      max_x = stick.h_pos
  return max_x


# def create_player(player_type: str) -> Player:
#   if player_type == 'Trivial':
#     return TrivialPlayer('Computer')
#   elif player_type == 'Random':
#     return RandomPlayer('Computer')
#   elif player_type == 'Pretrained':
#     return PretrainedPlayer('trained_agents/Alice', 'Computer')
#   elif player_type == 'Human':
#     return HumanPlayer('Human')
#   elif player_type == 'VisualHuman':
#     return VisualHumanPlayer(name='Human')
#   else:
#     raise TypeError("That type of player is not available.")
