"""Go analysis functions of the GoFamiliar implemented in kivy."""

from kivy.app import App
from kivy.graphics import Color, Ellipse
from kivy.uix.widget import Widget
from kivy.lang import Builder

from bokeh.charts import HeatMap, show, output_file
from bokeh.palettes import Spectral11 as palette

import numpy as np

size = 19

Builder.load_string(
'''
<HeatGridWidget>:
    canvas:
        Color:
            hsv: 0.01, 1, 1
''')


class HeatGridWidget(Widget):
    """

    """

    def __init__(self, prob_array=None):
        """Constructs the HeatGridWidget

        The prob_array is an array of values x: 0 <= x <= 1.

        :param prob_array: ndarray
        :return: None
        """
        super().__init__()

        if prob_array:
            self.array = prob_array
        else:
            self.array = np.random.rand(size, size)

        print(self.array)
        assert all([0 <= value and value <= 1 for value in np.nditer(self.array)])
        self.spread = 30


    def set_canvas(self):
        with self.canvas:
            it = np.nditer(self.array)
            Color(*(0.8, 0.8, 0.8), mode='hsv')
            Ellipse(pos=(30,30), size=(0.9*self.spread, 0.9*self.spread))
            while not it.finished:

                position = tuple((x*self.spread, y*self.spread)
                                    for x,y in it.multi_index)


class GoFamiliar(App):

    def build(self):
        return HeatGridWidget()

if __name__ == '__main__':
    GoFamiliar().run()


# def make_heatmap(count_array, output_save='ghm.html'):
#     """Displays a heatmap overlaid on a goban.
#
#     :param count_array: numpy.array, k by k
#     :param output_save: string
#     :return: k by k goban HeatMap display
#     """

#
# def add_games(games_array, prev_counts=None):
#     """Sum a set of GoPositions.
#
#     For each interection, function counts the number of times black, white and no-one has played there.
#     Counts are recorded as three integer arrays, one each for black, white and no-one.
#
#     New counts are added to prev_counts if not None.
#     >>> not sure what to test
#
#     :param games_array: n array of GoPositions.
#     :param prev_counts: numpy.array, integer entries, shape k by k (default None)
#     :return: k by k by 3 integer array
#     """
#     pass
#
#
# def intersection_ownership(count_array):
#     """Returns chart showing end of game expected ownership.
#
#     Chart is overlaid in a goban, and each intersection shows x% black, y% gray (or clear) and z% white
#     where x+y+z = 100 and represent the percentage chance of end of game ownership.
#
#     >>> not sure what to test
#
#     :param count_array: numpy.array, k by k by 3, integer
#     :return: k by k goban display
#     """
#     pass
#
#
# def __random_game_accessor(size=19, number_positions=1000000, yield_size=2 ** 14):
#     """Yields randomly generated sets of GoPositions.
#
#     >>> Need tests
#
#     :param number_positions: int = number of random games to yield total
#     :param size: int = game board size (default 19)
#     :param yield_size: int = number of random games to yield at a once
#     :yield: random array of GoPositions
#     """
#
#     for __ in range(number_positions // yield_size):
#         yield random.random_integers(-1, 1, (yield_size, size, size))
#     rem = number_positions % yield_size
#     yield random.random_integers(-1, 1, (rem, size, size))
#
#
# def __compute_spots(position_array_iter, size=19):
#     """Calculate the percentage chance of intersection ownership.
#
#     >>> need tests
#
#     :param position_array_iter: iterator  over a set of go positions
#     :param size: size of the games in the iterator
#     :return: (float array, float array) = the percentages for both black and white intersection ownership
#     """
#     black = np.zeros((size, size))
#     white = np.zeros((size, size))
#
#     corr_factor = 0.5 / number_games
#     for game_array in position_array_iter:
#         bmw = np.sum(game_array, 0)
#         bpw = np.sum(np.abs(game_array), 0)
#
#         new_black = np.multiply(np.add(bmw, bpw), corr_factor)
#         new_white = np.multiply(np.subtract(bmw, bpw), corr_factor)
#
#         black = np.add(black, new_black)
#         white = np.add(white, new_white)
#     return black, white
#
#
# def __compute_score(position_array_iter, size=19):
#     """Compute expected score.
#
#     Positive indicated black is winning; negative indicates white is winning.
#
#     :param position_array_iter: iterator  over a set of go positions
#     :return: float = expected final score given the position array
#     """
#     return np.sum(np.add(__compute_spots(position_array_iter, size)))
