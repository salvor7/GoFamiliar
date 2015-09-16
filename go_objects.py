"""Objects representation of aspects of Go.

>>> black_tengen = GoMove(player=1, x=10, y=10)
>>> black_tengen
GoMove(player=1, x=10, y=10)
>>> white_komoku = GoMove(-1,3,4)
>>> white_komoku
GoMove(player=-1, x=3, y=4)
"""

import numpy as np
from collections import namedtuple

DEFAULT_SIZE = 19

GoMove = namedtuple('GoMove','player x y')
"""GoMove object"""

class GoPosition:
    """GoPosition object.
    
    The size (k) of the game board is set at object construction, can be any odd integer and is based.

    Any game state is recorded as a k by k np.array with the entries
        0 for no stone
        1 for a black stone
        -1 for a white stone

    GoPosition object is a numpy.array object, with the additional entry constraints and shape constraints, ie. k by k
    """

    def __init__(self, moves=None, size=DEFAULT_SIZE, komi=6.5, lastmove=None, kolock=None):
        """GoPosition constructor.
        
        The GoPosition object can be constructed as a blank board 19 by 19 (default)
        or using a list of GoMoves.

        >>> print(GoPosition(size=3).board)
        [[0 0 0]
         [0 0 0]
         [0 0 0]]

        :param game: size by size  np.array
        :param size: size of goban
        """
        self.board = np.zeros((size, size), dtype=np.int)
        self.komi = komi
        self.lastmove = lastmove
        self.kolock = kolock

        try:
            for move in moves:
                self.add_move(move)
        except TypeError:
            pass


    def add_move(self, move):
        """Return a GoPosition post adding a move to self.
        
        Add a new k by k board representing the game state after the player move, including removing captures, and
        updating self.last_move with move.

        >>> position = GoPosition()
        >>> position.add_move(GoMove(1,4,4))
        >>> position.board[3][3]
        1

        :param move: GoMove
        :return: None
        """
        self.board[move.x - 1, move.y - 1] += move.player


class GoPositionArray:
    pass

class GoGame:
    pass