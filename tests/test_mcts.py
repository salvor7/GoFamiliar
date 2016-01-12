import random
import itertools

import pytest

import godata as gd
import mcts
import tests.test_fixtures as fixt
from sgf.library import Library
from util import tree


@pytest.fixture()
def position():
    return fixt.open_position()()


@pytest.fixture()
def position_moves():
    return fixt.first_position()(s=19)


@pytest.fixture()
def unexpanded_root(position_moves):
    position, moves = position_moves
    node_data = {'name': list(moves.keys())[-1],
             'state': position,
             'actions': position.random_playout,
             'wins': 0,
             'sims': 0,
             'parent': None,}
    return tree.Node(node_data=node_data)


@pytest.fixture()
def expanded_root(unexpanded_root):
    for action in unexpanded_root.data['actions']:
        child = mcts.expand(node=unexpanded_root, action=action)
        reward = mcts.defaultpolicy(child)
        mcts.backup(node=child, reward=reward)
    return unexpanded_root


def test_root(unexpanded_root):
    action = next(unexpanded_root.data['actions'])
    child = mcts.expand(node=unexpanded_root, action=action)
    assert type(child) == tree.Node
    assert child in unexpanded_root.children

    assert child.data['name'] == action[0]
    assert type(child.data['state']) == type(unexpanded_root.data['state'])
    assert type(child.data['actions']) == type(unexpanded_root.data['actions'])
    assert child.data['wins'] == 0
    assert child.data['sims'] == 0
    assert child.data['parent'] == unexpanded_root

    reward = mcts.defaultpolicy(child.data['state'], gd.TerminalPosition)
    mcts.backup(child, reward)
    assert child.data['sims'] == 1
    assert unexpanded_root.data['sims'] == 1
    assert child.data['wins'] == reward and child.data['wins'] == -unexpanded_root.data['wins']


def test_children(expanded_root):
    testing_lambdas = [lambda x: x.data['state'],
                       lambda x: x.data['state'].board,
                       lambda x: x.data['state'].groups,
                       lambda x: x.data['actions'],
                       lambda x: x.data['name'],]

    mutable_objects = [[func(node) for node in expanded_root.children + [expanded_root]]
                       for func in testing_lambdas]
    for mutable_objs in mutable_objects:
        for obj1, obj2 in itertools.combinations(mutable_objs, r=2):
            assert type(obj1) == type(obj2)
            assert obj1 is not obj2

    for node in expanded_root.children:
        assert node.data['parent'] is expanded_root
        assert node.data['sims'] == 1

    assert expanded_root.data['sims'] == sum([child.data['sims'] for child in expanded_root.children])
    assert expanded_root.data['wins'] == -sum([child.data['wins'] for child in expanded_root.children])

    best = mcts.bestchild(expanded_root)
    assert best.data['wins'] == 1
    assert best in expanded_root.children
    assert type(best) == tree.Node

    child = mcts.treepolicy(expanded_root)
    assert type(child) == tree.Node
    assert child in best.children

    reward = mcts.defaultpolicy(child.data['state'], gd.TerminalPosition)
    mcts.backup(node=child, reward=reward)
    assert best.data['sims'] == 2
    assert best.data['wins'] == 1 + reward
    assert expanded_root.data['sims'] == 1 + sum([child.data['sims']
                                                      for child in expanded_root.children])
    assert expanded_root.data['wins'] == reward + sum([child.data['wins']
                                                       for child in expanded_root.children])


def test_search_open_board(position, position_moves):
    move_pt = None
    for idx in range(19 ** 2 * 3):
        try:
            move_pt, last_pt = mcts.search(position), move_pt
        except gd.MoveError as err:
            assert str(err) == 'Terminal Position'
            break
        assert type(move_pt) is int
        assert move_pt != last_pt
        position.move(move_pt=move_pt)
    else:
        assert 'it is an' == 'infinite loop'
    assert idx > 200


def test_search_avoid_eyes(position_moves):
    position, moves = position_moves
    move_pt = None
    for idx in range(19 ** 2 * 3):
        try:
            move_pt, last_pt = mcts.search(position), move_pt
        except gd.MoveError as err:
            assert str(err) == 'Terminal Position'
            break
        assert move_pt not in [0, 20]
        position.move(move_pt=move_pt)
    else:
        assert 'it is an' == 'infinite loop'
    assert idx > 200


@pytest.fixture(scope='module')
def library():
    return Library(direc='sgf_store\\sgf_tests', file='sgf_tests.hdf5')


@pytest.fixture(params=list(library()))
def tsumego(request):
    tsumego_name = request.param
    correct_move = int(tsumego_name[7:10])  # correct move encoded in file name
    return library().sgf_position(tsumego_name), correct_move


def test_tsumego_solving(tsumego):
    position, correct_move = tsumego
    found_move = mcts.search(position)
    assert correct_move == found_move

