import itertools
import pytest
from . import godata as gd

fixture_params = [n for n in range(9, 26, 2)]

@pytest.fixture(params=fixture_params)
def position(request):
    return gd.Position(size=request.param)

@pytest.fixture(params=fixture_params)
def position_moves(request):
    """Sets up two positions in the
    Upper left
    .X.Xo.
    X.Xoo.
    XXX...
    ......
    Lower right
    ......
    ..oooo
    .oooXX
    .oXXX.

    (X = black, o = white)
    They do not overlap as the Positions are size_limit 9 or greater.
    """
    s = request.param
    rest_of_row = '.'*(s-5)
    first_three = rest_of_row.join([
                    '.X.Xo',
                    'X.Xoo',
                    'XXX..',''])
    last_three = rest_of_row.join(['',
                    '.oooo',
                    'oooXX',
                    'oXXX.',])
    board = first_three + '.'*s*(s-6) + last_three
    position = gd.Position(size=request.param)
    for pt, symbol in enumerate(board):
        if symbol == 'X':
            position.move(pt=pt, colour=gd.BLACK)
        elif symbol == 'o':
            position.move(pt=pt, colour=gd.WHITE)
    return position

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

def test_Position_initial(position):
    """Test initiliazation of Position
    """
    assert position.ko is None
    assert position.next_player is gd.BLACK
    assert len(position.board) == position.size**2
    assert len(position.groups) == 0

def test_Position_move(position_moves):
    """Test the move function

    The fixture tests the basic use of this function.
    """
    assert len(position_moves.groups) == 6

def test_Position_getitem(position_moves):
    """Test that every board point returns correct group

    Add several groups to a Position, and then test that the references all point to
    the correct Group
    """
    crosses = [c for c in range(position.size, position.size, 4)]
    for c in crosses:
        position.board.multi_union(iter([c] + list(gd.NEIGHBORS[c])))
        lib, size = (8, 5) if len(gd.NEIGHBORS[c]) == 4 else (5, 4)
        position.groups[c] = gd.Group(colour=(-1)**c, size=size, liberties=lib)

    for c in position.board:
        if position.board[c] not in crosses:
            assert position[c] == gd.OPEN_POINT
        elif position.board[c] in crosses:
            assert position[c] == position.groups[position.board[c]]
        else:
            assert False

def test_Position_neigh_groups():
    """Test finding neighbor groups.

    """

def test_Group_init():
    """Test Initialization of Group object
    """
    for col, size, lib in itertools.product([gd.BLACK, gd.WHITE], range(361), range(361)):
        assert gd.Group(colour=col,  size=size, liberties=lib,) == (col, size, lib)
