import pytest
import godata as gd
import mcts
import tests.test_fixtures as fixt
from sgf.library import Library


@pytest.fixture()
def position():
    return fixt.open_position()()


@pytest.fixture()
def position_moves():
    return fixt.first_position()(s=19)


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
    correct_move = int(tsumego_name[7:10])
    return library().sgf_position(tsumego_name), correct_move

def test_tsumego_solving(tsumego):
    position, correct_move = tsumego
    found_move = mcts.search(position)
    assert correct_move == found_move
