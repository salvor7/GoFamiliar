"""
This module defines the GoGame object as a representation a Go game. The GoGame object is a store of all the game states
or just the final game state of a go game.
"""
__author__ = 'salvor7'

import numpy as np


class GoGame(np.array):
    """
    The size (k) of the game board is set at object construction, can be any odd integer and is based.

    Any game state is recorded as a k by k np.array with the entries
        0 for no stone
        1 for a black stone
        -1 for a white stone

    GoGame object is a numpy.array object, with the additional entry constraints and shape constraints, ie. k by k by n
    """

    default_size = 19

    def __init__(self, game):
        """The GoGame object can be constructed as a blank board (default)
        or using
            - an sgf file (principle branch only)
            - a michi style game string
            - a 19 by 19 by n array with entries 0,1,-1
        """
        super(np.array, self).__init__()
        self += np.zeros((self.default_size, self.default_size))
