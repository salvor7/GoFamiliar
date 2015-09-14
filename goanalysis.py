"""Go analysis functions of the GoFamiliar implemented in kivy."""

from kivy.app import App
from kivy.uix.widget import Widget


import numpy as np
import random


def make_heatmap(count_array, output_save='ghm.html'):
    """Displays a heatmap overlaid on a goban.

    >>> not sure what to test

    :param count_array: numpy.array, k by k
    :param output_save: string
    :return: k by k goban HeatMap display
    """

    output_file(output_save)
    show(HeatMap(count_array, palette=palette))

def add_games(games_array, prev_counts=None):
    """Sum a set of GoPositions.

    For each interection, function counts the number of times black, white and no-one has played there.
    Counts are recorded as three integer arrays, one each for black, white and no-one.

    New counts are added to prev_counts if not None.
    >>> not sure what to test

    :param games_array: n array of GoPositions.
    :param prev_counts: numpy.array, integer entries, shape k by k (default None)
    :return: k by k by 3 integer array
    """
    pass


def intersection_ownership(count_array):
    """Returns chart showing end of game expected ownership.

    Chart is overlaid in a goban, and each intersection shows x% black, y% gray (or clear) and z% white
    where x+y+z = 100 and represent the percentage chance of end of game ownership.

    >>> not sure what to test

    :param count_array: numpy.array, k by k by 3, integer
    :return: k by k goban display
    """
    pass


def __random_game_accessor(size=19, number_positions=1000000, yield_size = 2**14):
    """Yields randomly generated sets of GoPositions.

    >>> Need tests

    :param number_positions: int = number of random games to yield total
    :param size: int = game board size (default 19)
    :param yield_size: int = number of random games to yield at a once
    :yield: random array of GoPositions
    """

    for __ in range(number_positions//yield_size):
        yield random.random_integers(-1, 1, (yield_size, size, size))
    rem = number_positions % yield_size
    yield random.random_integers(-1, 1, (rem, size, size))


def __compute_spots(position_array_iter, size=19):
    """Calculate the percentage chance of intersection ownership.

    >>> need tests

    :param position_array_iter: iterator  over a set of go positions
    :param size: size of the games in the iterator
    :return: (float array, float array) = the percentages for both black and white intersection ownership
    """
    black = np.zeros((size, size))
    white = np.zeros((size, size))

    corr_factor = 0.5/number_games
    for game_array in position_array_iter:
        bmw = np.sum(game_array, 0)
        bpw = np.sum(np.abs(game_array), 0)

        new_black = np.multiply(np.add(bmw, bpw), corr_factor)
        new_white = np.multiply(np.subtract(bmw, bpw), corr_factor)

        black = np.add(black, new_black)
        white = np.add(white, new_white)
    return black, white


def __compute_score(position_array_iter, size=19):
    """Compute expected score.

    Positive indicated black is winning; negative indicates white is winning.

    :param position_array_iter: iterator  over a set of go positions
    :return: float = expected final score given the position array
    """
    return np.sum(np.add(__compute_spots(position_array_iter,size)))

