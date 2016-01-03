import pytest
import godata as gd
import mcts
import tests.test_fixtures as fixt


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


def test_is_eye(position_moves):
    position, moves = position_moves
    group_eyes = [0, 20, 19 ** 2 - 1]
    for pt in position.board:
        pt_is_eye = (pt in group_eyes)
        assert mcts.is_eye(position=position, pt=pt, colour=gd.BLACK) == pt_is_eye


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

