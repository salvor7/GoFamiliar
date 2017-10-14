
from os import path

import h5py
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


def test_sgf_position():
    position = sgf.Library(file=path.join(sgf.TEST_DIR, 'libtests_sgf.h5'),
                           direc=sgf.TEST_DIR,
                           sgf_direc=sgf.TEST_DIR
                           ).sgf_position('chap075')
    assert position.komi == 5.5
    assert position.size == 19
