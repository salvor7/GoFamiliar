import itertools
import pytest
import godata as gd

@pytest.fixture(scope='module', params=[n for n in range(9,25, 2)])
def position(request):
    return gd.Position(size=request.param)

@pytest.fixture(scope='module')
def position_moves(position):
    size = position.size
    black_stones = [1, size, 1+size*2]

def test_make_neighbors(position):
    """Test neighbor making by counting occurrences of neighbors

    Corners have two neighbors; Edges points have 3, and Centre points have 4.
    """
    def result_row(i, size):
        return [i] + [i+1]*(size-2) + [i]

    size = position.size

    neigh_counts = [0]*(size**2)
    first_row = result_row(2, size)
    last_row = result_row(2, size)
    middle_row = result_row(3, size)
    desired_result = first_row + (middle_row)*(size-2) + last_row
    for c, neighs in gd.make_neighbors(size=size):
        for pt in list(neighs):
            neigh_counts[pt] += 1

    assert desired_result == neigh_counts

def test_Group_init():
    """Test Initialization of Group object
    """
    for col, size, lib in itertools.product([gd.BLACK, gd.WHITE], range(361), range(361)):
        assert gd.Group(colour=col,  size=size, liberties=lib,) == (col, size, lib)


def test_Position_initial(position):
    """Test initiliazation of Position
    """
    assert position.ko is None
    assert position.next_player is gd.BLACK
    assert len(position.board) == position.size**2
    assert len(position.groups) == 0

def test_Position_neigh_groups():
    """Test finding neighbor groups.

    """


def test_Position_move():
    pass
