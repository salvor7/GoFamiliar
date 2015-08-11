"""
This module defines the GoGame object as a representation a Go game. The GoGame object is a store of all the game states
or just the final game state of a go game.
"""
import numpy as np


class GoPosition(np.ndarray):
    """
    The size (k) of the game board is set at object construction, can be any odd integer and is based.

    Any game state is recorded as a k by k np.array with the entries
        0 for no stone
        1 for a black stone
        -1 for a white stone

    GoGame object is a numpy.array object, with the additional entry constraints and shape constraints, ie. k by k by n
    """

    default_size = 19

    def __init__(self, game=None, size=default_size):
        """The GoGame object can be constructed as a blank board 19 by 19 (default)
        or using
            - an sgf file (principle branch only)
            - a michi style game string
            - a k by k by n array with entries 0,1,-1

        >>> print(GoPosition(size=3))
        [[0 0 0]
         [0 0 0]
         [0 0 0]]
        >>> print(GoPosition(game='(SZ[3]B[ac]W[cc]B[ca])'))
        [[0 0 1]
         [0 0 0]
         [1 0 -1]]
        >>> michi_string = '      ..X  O..  .X.      '
        >>> print(GoPosition(game=michi_string))
        [[0 0 1]
         [-1 0 0]
         [0 1 0]]

        :param game: sgf formated string, or a michi formatted string or a k by k by n np.array
        :param size: size of goban. size of game overrides parameter
        """
        super(np.zeros(shape=(size, size), dtype=np.int8), self).__init__()

    def add_move(self, location):
        """
        Add a new k by k board representing the game state after the player move.

        >>> game = GoPosition(size=3)
        >>> print(game.add_move('B[ab]'))  #SGF format
        [[0 0 0]
         [1 0 0]
         [0 0 0]]
        >>> print(game.add_move('W(1,3)'))  #colour + coordinate format
        [[0 0 -1]
         [1 0 0]
         [0 0 0]]

        :param location: location of move in sgf format, colour + coordinate format
        :return: GoGame of new state
        """
        pass

if __name__ == '__main__':
    import doctest

    doctest.testmod(verbose=True)