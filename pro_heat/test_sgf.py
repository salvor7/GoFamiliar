from . import sgf
import h5py
import os
import numpy as np

file = 'pro_collection.hdf5'
fpath = 'sgf_store'

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
    ...     sgf.node_to_move('error')
    ... except ValueError as err:
    ...     print(err)
    "error" is not a sgf move formatted node
    """
    pass


def test_hdf5_access():

    pro_games = h5py.File(os.path.join(fpath, file), 'r')


    print(len(pro_games['19']))
    #access size 19 games
    count_board = np.zeros(shape=(19,19), dtype=np.int)
    for idx, game in enumerate(pro_games['19']):

        player, x, y = pro_games['19'][game][0]
        count_board[x-1, y-1] += 1

    print(count_board)