"""
This module defines the go analysis functions of the GoFamiliar.
"""
from bokeh.charts import HeatMap, show, output_file
from bokeh.palettes import Spectral11 as palette


def make_heatmap(count_array, output_save='ghm.html'):
    """Displays a heatmap, based on counts_array, overlaid on a goban.

    :param count_array: numpy.array, k by k
    :param output_save: string
    :return: k by k goban HeatMap display
    """

    output_file(output_save)
    show(HeatMap(count_array, palette=palette))

def add_games(games_array, prev_counts=None):
    """For each interection, function counts the number of times black, white and no-one has played there. Counts are
    recorded as three integer arrays, one each for black, white and no-one.

    New counts are added to prev_counts if not None.

    :param games_array: numpy.array, -1,0,1 entries, shape k by k by n
    :param prev_counts: numpy.array, integer entries, shape k by k (default None)
    :return: k by k by 3 integer array
    """
    pass

def intersection_ownership(count_array):
    """Returns a k by k chart overlaid on a goban showing end of game expected ownership of each intersection as a go
    stone coloured x% black, y% gray (or clear) and z% white where x+y+z = 100 and represent the percentage chance of
    end of game ownership.

    :param count_array: numpy.array, k by k by 3, integer
    :return: k by k goban display
    """
    pass