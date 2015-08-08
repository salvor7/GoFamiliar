__author__ = 'salvor7'
from unittest import TestCase
import sgf
from os import path

class SGFReaderTests(TestCase):
    test_sgf_path = 'test_sgfs'
    linear_sgf = path.join(test_sgf_path, r'linear_test.sgf')
    branching_sgf = path.join(test_sgf_path, r'branching_test.sgf')

    def test_sgf2df(self):
        print(sgf.sgf2df(self.linear_sgf))

    def test_branchreader(self):
        def diveintobranches(branchlist):
            assert '' not in branchlist

            for node in branchlist:
                if type(node) == list:
                    diveintobranches(node)
        length_of_linear_sgf = 285
        length_of_branchy_sgf = 12

        assert len(sgf.branchreader(self.linear_sgf)) == length_of_linear_sgf
        assert len(sgf.branchreader(self.branching_sgf)) == length_of_branchy_sgf

    def test_node_to_board(self):
        assert sgf.node_to_board(r'B[dd]')[3][3] == 1
        assert sgf.node_to_board(r'W[sa]')[0][18] == -1

    def test_nodelist_to_boardlist(self):
        branchlist = sgf.branchreader(self.linear_sgf)
        print(len(sgf.nodelist_to_boardlist(branchlist)))
        assert len(branchlist) == len(sgf.nodelist_to_boardlist(branchlist))