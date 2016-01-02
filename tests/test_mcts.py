import pytest

import godata as gd
import mcts
import tests.test_fixtures as fixt

@pytest.fixture
def position():
    return fixt.open_position()()

def test_search(position):
    move_pt = None
    for _ in range(19**3):
        try:
            move_pt, last_pt = mcts.search(position), move_pt
        except gd.MoveError:
            break
        assert type(move_pt) is int
        assert move_pt != last_pt
        position.move(move_pt=move_pt)
    else:
        assert 'it is an' == 'infinite loop'