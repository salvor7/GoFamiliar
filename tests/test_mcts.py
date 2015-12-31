import pytest

import godata as gd
import mcts

@pytest.fixture
def position():
    return gd.Position()

def test_search(position):
    assert type(mcts.search(position)) is int