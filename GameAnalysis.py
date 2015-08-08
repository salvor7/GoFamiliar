"""
This module defines the go analysis functions of the GoFamiliar.
"""

__author__ = 'salvor7'

from bokeh.charts import HeatMap, show, output_file
from bokeh.palettes import Spectral11 as palette


def make_heatmap(count_array, output_save='ghm.html'):
    """Displays a heatmap, based on counts_array, overlayed on a goban.

    :param count_array: numpy.array, k by k
    :param output_save: string
    :return: HeatMap
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
