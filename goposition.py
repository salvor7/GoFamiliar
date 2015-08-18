"""
This module defines the GoPosition object as a representation a Go game snap shot as a numpy array.
"""
import numpy as np


class GoPosition(np.ndarray):
    """GoPosition object.
    
    The size (k) of the game board is set at object construction, can be any odd integer and is based.

    Any game state is recorded as a k by k np.array with the entries
        0 for no stone
        1 for a black stone
        -1 for a white stone

    GoPosition object is a numpy.array object, with the additional entry constraints and shape constraints, ie. k by k
    """
    default_size = 19

    def __init__(self, moves=None, size=default_size, komi=6.5):
        """GoPosition constructor.
        
        The GoPosition object can be constructed as a blank board 19 by 19 (default)
        or using a list of GoMoves.

        >>> print(GoPosition(size=3))
        [[0 0 0]
         [0 0 0]
         [0 0 0]]
        >>> list init test

        :param game: size by size  np.array
        :param size: size of goban
        """
        super().__init__()
        self.komi = komi
        self.lastmove = None

        for move in moves:
            self.add_move(move)


    def add_move(self, move):
        """
        Return a GoPosition post adding a move to self.
        
        Add a new k by k board representing the game state after the player move, including removing captures, and
        updating self.last_move with move.

        >>> position = GoPosition()
        >>> pos.add_move(GoMove(1,4,4))[3][3]
        1

        :param move: GoMove
        :return: GoPostion
        """
        #np.sum([boardlist[-1], board]
        pass



if __name__ == '__main__':
    import doctest

    doctest.testmod(verbose=True)