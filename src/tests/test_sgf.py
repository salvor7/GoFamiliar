import os
import h5py
import numpy as np
import pytest

import sgf


def test_sgf_parser():
    """
    >>> basic_branching2 = '(;SZ[19];B[jj];W[kl](;B[dd](;W[gh])   (;W[sa]))(;B[cd]))'
    >>> sgf.parser(basic_branching2)
    ['SZ[19]', 'B[jj]', 'W[kl]', ['B[dd]', ['W[gh]'], ['W[sa]']], ['B[cd]']]
    >>> complex_branching = ('(;RU[Japanese]SZ[19]KM[6.50];B[jj];W[kl]'
    ...                 '(;B[pd](;W[pp]) (;W[dc](;B[de])(;B[dp])))'
    ...                 '(;B[cd];W[dp])'
    ...                 '(;B[cq](;W[pq])  (;W[pd]))'
    ...                 '(;B[oq];W[dd]))')
    >>> for chunk in sgf.parser(complex_branching):
    ...    chunk
    'RU[Japanese]'
    'SZ[19]'
    'KM[6.50]'
    'B[jj]'
    'W[kl]'
    ['B[pd]', ['W[pp]'], ['W[dc]', ['B[de]'], ['B[dp]']]]
    ['B[cd]', 'W[dp]']
    ['B[cq]', ['W[pq]'], ['W[pd]']]
    ['B[oq]', 'W[dd]']
    """
    pass

def test_main_branch():
    """

    >>> linear_sgf = '(;KM[2.75]SZ[19];B[qd];W[dd];B[oc];W[pp];B[do];W[dq])'
    >>> for node in sgf.main_branch(sgf.parser(linear_sgf)):
    ...     print(node)
    KM[2.75]
    SZ[19]
    B[qd]
    W[dd]
    B[oc]
    W[pp]
    B[do]
    W[dq]
    >>> complex_branching = ('(;RU[Japanese]SZ[19]KM[6.50];B[jj];W[kl]'
    ...                 '(;B[pd](;W[pp])(;W[dc](;B[de])(;B[dp])))'
    ...                 '(;B[cd];W[dp])'
    ...                 '(;B[cq](;W[pq])(;W[pd]))'
    ...                 '(;B[oq];W[dd]))')
    >>> for node in sgf.main_branch(sgf.parser(complex_branching)):
    ...     print(node)
    RU[Japanese]
    SZ[19]
    KM[6.50]
    B[jj]
    W[kl]
    B[pd]
    W[pp]
    """
    pass

def test_node_to_move():
    """
    >>> try:
    ...     sgf.node_to_gomove('error')
    ... except ValueError as err:
    ...     print(err)
    "error" is not an sgf move formatted node
    """
    pass


@pytest.fixture(scope='module')
def pro_games():
    try:
        return h5py.File(sgf.SGF_H5, 'r')
    except OSError:
        sgf.read.create_pro_hdf5()
        return h5py.File(sgf.SGF_H5, 'r')


def test_all_pro_games_included(pro_games):
    assert len(pro_games) == 51508


def test_sgf_data_correct(pro_games):
    """ Test the data for a subsample of sgf

    Ensure all meta data is stored, and that the number of moves is correct
    """
    standard_attributes = ['FF', 'EV', 'PB', 'BR', 'PW', 'WR', 'KM', 'RE', 'DT', 'SZ']
    subsamplegames = {'HoshinoToshi-YamabeToshiro4762': (standard_attributes + ['PC', 'CA'], 411),
                      'HayashiYutaro-HashimotoUtaro4546': (standard_attributes + ['GM', 'CA'], 302),
                      '-1': (standard_attributes + ['PC', 'CA'], 284),
                      'ZouJunjie-ZhuSongli25339': (standard_attributes + ['RU', 'CA'], 161),
                      '.-.21425': (standard_attributes + ['PC', 'RU', 'CA'], 148),
                      'WangLei-WangYao35430': (standard_attributes + ['AP'], 121),
                      '-2432': (standard_attributes + ['PC', 'GM', 'CA'], 61),
                      }

    for gamename in subsamplegames:
        expected_attributes, expected_game_len = subsamplegames[gamename]

        # ensure all expected attributes are present
        for attr in expected_attributes:
            assert attr in pro_games[gamename].attrs

        moves = list(pro_games[gamename]['moves'])
        assert len(moves) == expected_game_len
        for m in moves:
            assert 0 <= m[0] < 19**2
