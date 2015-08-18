"""This file defines the GoMove object.

>>> move = GoMove(1, 16, 4)
>>> move.player
1
>>> move.x, move.y
16, 4
"""
from collections import namedtuple

GoMove = namedtuple('Move','player x y')

class GoMove2(namedtuple('Move', 'player x y')):
    """

    :param colour: 1 or -1  for black or white
    :param x: int  1 to 19
    :param x: int  1 to 19
    """
    
    def __init__(self, player, x, y):
      """
      GoMove constructor.
      
      
      """