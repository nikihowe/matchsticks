# (c) Nikolaus Howe 2021

import graphics as gfx


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


def check_intersection(vertical_line: gfx.Line, other_line: gfx.Line) -> bool:
  """
  Check for intersection between two line segments.

  :param vertical_line: The first line segment. Guaranteed to be vertical.
  :param other_line: The second line segment.
  :return: Whether or not they intersect.
  """
  our_p1 = vertical_line.p1
  our_x1 = our_p1.x
  our_y1 = our_p1.y

  our_p2 = vertical_line.p2
  # our_x2 = our_p2.x  # This is the same as x1, so don't need to calculate
  our_y2 = our_p2.y

  their_p1 = other_line.p1
  their_x1 = their_p1.x
  their_y1 = their_p1.y

  their_p2 = other_line.p2
  their_x2 = their_p2.x
  their_y2 = their_p2.y

  # Check for vertical line. If vertical, then no intersection.
  if their_x2 == their_x1:
    return False

  their_a = (their_y2 - their_y1) / (their_x2 - their_x1)
  their_b = -their_x1 * (their_y2 - their_y1) / (their_x2 - their_x1) + their_y1

  x_intersect = our_x1
  y_intersect = their_a * our_x1 + their_b

  they_intersect = (
    (their_x1 <= x_intersect <= their_x2 or their_x2 <= x_intersect <= their_x1)
    and
    (our_y1 <= y_intersect <= our_y2 or our_y2 <= y_intersect <= our_y1)
    and
    (their_y1 <= y_intersect <= their_y2 or their_y2 <= y_intersect <= their_y1)
  )

  line_is_pretty = (
    (our_y1 <= their_y1 <= our_y2 or our_y2 <= their_y1 <= our_y1)
    and
    (our_y1 <= their_y2 <= our_y2 or our_y2 <= their_y2 <= our_y1)
  )

  return they_intersect and line_is_pretty


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
