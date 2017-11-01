
from os import path

import h5py
import pytest
import thick_goban

import sgf
from util.directory_tools import search_tree


TEST_DIR = path.join(sgf.DATA_DIR, 'test_sets')
TEST_CSV = path.join(TEST_DIR, )


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


def test_store():
    """Test the store generator yields all the test sgf files"""
    idx = 0
    for idx, _ in enumerate(sgf.store(sgf_direc=TEST_DIR), 1):
        pass

    assert idx == len(search_tree(directory=TEST_DIR, file_sig='*.sgf'))


def test_store_parser():
    """Test that the basic attributes expected are present for each game"""
    for game_details in sgf.store_parser(sgf.store(sgf_direc=TEST_DIR)):
        for keyname in ['sgfstr', 'path', 'name', 'moves', 'setup']:
            assert keyname in game_details


def test_create_csv():
    """Test the pro sgf csv file gets created"""
    sgf.create_pro_csv(file='tests_sgf.csv', direc=TEST_DIR)


@pytest.fixture(scope='module')
def test_games():
    """Fixture created using the create pro hdf5 method"""
    test_file = TEST_H5 = path.join(TEST_DIR, 'tests_sgf.h5')
    try:
        return h5py.File(test_file, 'r')
    except OSError:
        sgf.create_pro_hdf5(file=test_file, direc=TEST_DIR, sgf_direc=TEST_DIR)
        return h5py.File(test_file, 'r')


def test_create_H5(test_games):
    """Test the created H5 file has all the test sgfs"""
    assert len(test_games) == len(search_tree(directory=TEST_DIR, file_sig='*.sgf'))


@pytest.fixture(scope='module')
def test_library():
    """Fixture of an instantiated Library object"""
    libr = sgf.Library(file=path.join(TEST_DIR, 'libtests_sgf.h5'), direc=TEST_DIR, sgf_direc=TEST_DIR)
    assert len(libr) == 115     # number of test sgf files
    return libr


def test_library_iter(test_library):
    """Test that __iter__ iterates over all keys"""
    idx = 1
    for idx, _ in enumerate(test_library, start=1):
        pass
    assert idx == len(test_library)


def test_get_item(test_library):
    """Test the getitem dunder method"""
    assert test_library['chap116']


def test_sgf_attributes(test_library):
    """Test sgf attributes method"""
    game = test_library.sgf_attributes('chap116')
    attributes = ['EV', 'PB', 'PW', 'SZ', 'KM', 'RE']
    values = ('22nd Meijin League', 'Rin Kaiho', 'Yoda Norimoto', '19', '5.5', 'W+0.5')

    for attribute, value in zip(attributes, values):
        assert game[attribute] == value


def test_sgf_position(test_library):
    """Test that an sgf position object is returned"""
    position = test_library.sgf_position('chap075')
    assert type(position) is thick_goban.go.Position
    assert position.komi == 5.5
    assert position.size == 19
