import itertools

import pytest

from thick_goban import go
import mcts
import tests.test_fixtures as fixt


def test_search_open_board():
    move_pt = None
    position = go.Position(size=9, komi=0.5)
    for idx in range(4):
        move_pt, last_pt = mcts.move_search(position, sim_limit=100), move_pt
        assert type(move_pt) is int
        assert move_pt != last_pt
        position.move(move_pt=move_pt)
        print(position.board)


@pytest.fixture(scope='module')
def position_moves():
    return fixt.first_position()(s=19)


@pytest.fixture(scope='module')
def unexpanded_root(position_moves):
    position, moves = position_moves

    return mcts.NodeMCTS(state=position, name='root')


def test_root(unexpanded_root):
    assert unexpanded_root.name is 'root'
    child = unexpanded_root.new_child()
    assert type(child) == mcts.NodeMCTS
    assert child in unexpanded_root.children.values()

    assert type(child.name) == int
    assert type(child.state) == type(unexpanded_root.state)

    assert child.sims == 1
    assert child.parent is unexpanded_root

    assert child.sims == unexpanded_root.sims
    assert child.sims - child.wins == unexpanded_root.wins


@pytest.fixture(scope='module')
def expanded_root(unexpanded_root):
    increasing_counter = 1  # child added above
    while True:
        try:
            _ = unexpanded_root.new_child()
        except go.MoveError:
            break
        else:
            increasing_counter += 1
            assert len(unexpanded_root.children) == increasing_counter  # must contain a new child each loop
    return unexpanded_root


def test_mutables_objects(expanded_root):
    """
    Test the mutable objects on the nodes are different objects

    With so much copying going on, it would be easy for many nodes to be pointing at the
    same state, or a number of states to be pointing at the same board object.
    """
    assert len(expanded_root.children) == 361 - 23 - 2

    testing_lambdas = [(lambda x: x.state),
                       (lambda x: x.state.actions),
                       (lambda x: x.state.board),
                       (lambda x: x.state.board._pointers),
                       (lambda x: x.state.board._board_colour), ]

    # test that nodes aren't sharing the same mutable objects
    all_nodes = list(expanded_root.children.values()) + [expanded_root]
    mutable_objects = [[func(node) for node in all_nodes] for func in testing_lambdas]

    for mutable_objs in mutable_objects:
        for obj1, obj2 in itertools.combinations(mutable_objs, r=2):
            assert type(obj1) == type(obj2)
            assert obj1 is not obj2


def test_children_of_expanded(expanded_root):
    """
    Test the various properties of the children of the expanded root node
    """
    for node in expanded_root.children.values():
        assert node.parent is expanded_root
        assert node.sims == 1

    assert expanded_root.sims == sum([child.sims for child in expanded_root.children.values()])
    assert expanded_root.sims - expanded_root.wins == sum([child.wins for child in expanded_root.children.values()])

    for idx in range(1, 200):
        best1stgen = expanded_root.bestchild()
        best1stgen = expanded_root.children[best1stgen]
        assert best1stgen in expanded_root.children.values()
        assert type(best1stgen) == mcts.NodeMCTS

        best1stgen.new_child()
        assert best1stgen.sims == 1 + sum([child.sims for child in best1stgen.children.values()])
        assert best1stgen.sims - best1stgen.wins == -1 + sum([child.wins for child in best1stgen.children.values()])
        assert expanded_root.sims == 361 - 23 - 2 + idx
        assert expanded_root.sims - expanded_root.wins == sum([child.wins for child in expanded_root.children.values()])


@pytest.fixture()
def position():
    return fixt.open_position()()


if __name__ == '__main__':
    import cProfile

    cProfile.run('expanded_root(unexpanded_root(position_moves()))')
