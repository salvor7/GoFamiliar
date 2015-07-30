__author__ = 'salvor7'

from unittest import TestCase
import go_heatmap as ghm
import numpy as np
import pandas as pd


class GoHeatTests(TestCase):
    def test_heatmap(self):
        size = 19
        random_counts = np.random.randint(0, 100, size=(size, size))
        rows = range(size, 0, -1)
        cols = range(1, size + 1)
        df = pd.DataFrame(random_counts, index=rows, columns=cols)
        test_file = 'ghm_test.html'
        ghm.make_heatmap(df, test_file)
