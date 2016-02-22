import itertools

import pytest

import go
import mcts
import tests.test_fixtures as fixt
from sgf.library import Library
from util import tree


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
    found_move = mcts.search(position, sim_limit=500)
    assert correct_move == found_move


@pytest.fixture()
def position():
    return fixt.open_position()()


@pytest.fixture()
def position_moves():
    return fixt.first_position()(s=19)


@pytest.fixture()
def unexpanded_root(position_moves):
    position, moves = position_moves

    return mcts.NodeMCTS(state=position, name='root')


@pytest.fixture()
def expanded_root(unexpanded_root):
    increasing_counter = 0
    while True:
        try:
            _ = unexpanded_root.new_child()
        except go.MoveError:
            break
        else:
            increasing_counter += 1
            assert len(unexpanded_root.children) == increasing_counter  #must contain a new child each loop
    return unexpanded_root


def test_root(unexpanded_root):
    assert unexpanded_root.name is 'root'
    child = unexpanded_root.new_child()
    assert type(child) == mcts.NodeMCTS
    assert child in unexpanded_root.children.values()

    assert type(child.name) == int
    assert type(child.state) == type(unexpanded_root.state)
    assert child.wins in [1, -1]
    assert child.sims == 1
    assert child.parent is unexpanded_root

    assert child.sims == unexpanded_root.sims
    assert child.wins == unexpanded_root.wins


def test_children(expanded_root):
    assert len(expanded_root.children) == 361 - 23 - 2

    testing_lambdas = [(lambda x: x.state),
                       (lambda x: x.state.actions),
                       (lambda x: x.state.board),
                       (lambda x: x.state.board._pointers),
                       (lambda x: x.state.board._board_colour),]

    # test that nodes aren't sharing the same mutable objects
    all_nodes = list(expanded_root.children.values()) + [expanded_root]
    mutable_objects = [ [func(node) for node in all_nodes] for func in testing_lambdas]

    for mutable_objs in mutable_objects:
        for obj1, obj2 in itertools.combinations(mutable_objs, r=2):
            assert type(obj1) == type(obj2)
            assert obj1 is not obj2

    for node in expanded_root.children.values():
        assert node.parent is expanded_root
        assert node.sims == 1

    assert expanded_root.sims == sum([child.sims for child in expanded_root.children.values()])
    assert expanded_root.wins == sum([child.wins for child in expanded_root.children.values()])

    for idx in range(1, 200):
        best1stgen = expanded_root.bestchild()
        assert best1stgen.wins < 0      # white move
        assert best1stgen in expanded_root.children.values()
        assert type(best1stgen) == mcts.NodeMCTS

        best1stgen.new_child()
        assert best1stgen.sims == 1 + sum([child.sims for child in best1stgen.children.values()])
        assert best1stgen.wins == -1 + sum([child.wins for child in best1stgen.children.values()])
        assert expanded_root.sims == 361 - 23 - 2 + idx
        assert expanded_root.wins == sum([child.wins for child in expanded_root.children.values()])


def test_search_open_board():
    move_pt = None
    position = go.Position(size=9, komi=0.5)
    for idx in range(4):
        try:
            move_pt, last_pt = mcts.search(position, sim_limit=300), move_pt
        except go.MoveError as err:
            assert str(err) == 'Terminal Position'
            break
        assert type(move_pt) is int
        assert move_pt != last_pt
        position.move(move_pt=move_pt)
        print(position.board)





if __name__ == '__main__':
    import cProfile
    cProfile.run('expanded_root(unexpanded_root(position_moves()))')

