import itertools
from collections import defaultdict

import pytest

import godata as gd

fixture_params = [n for n in range(9, 26, 2)]

@pytest.fixture(params=fixture_params)
def position(request):
    return gd.Position(size=request.param)

def test_make_neighbors(position):
    """Corners have two neighbors; Edges points have 3, and Centre points have 4.
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

    assert position.kolock is None
    assert position.next_player is gd.BLACK
    assert len(position.board) == position.size**2
    assert len(position.groups) == 0
    assert position.komi == 7.5

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
    stones_counts = defaultdict()
    for pt, symbol in enumerate(board):
        if symbol == 'X':
            position.move(move_pt=pt, colour=gd.BLACK)
            stones_counts[pt] = gd.BLACK
        elif symbol == 'o':
            position.move(move_pt=pt, colour=gd.WHITE)
            stones_counts[pt] = gd.WHITE
    return position, stones_counts

def exception_test(func, err, message):
    try:
        func()
    except err as err:
        assert message == str(err)
    else:
        assert False

def test_Position_getsetdel(position_moves):

    position, moves = position_moves
    #test moves made in fixture
    for pt in position.board:
        group = position[pt]
        assert type(group) == gd.Group
        assert pt in moves or group == gd.OPEN_POINT
        assert pt not in moves or group == position.groups[position.board[pt]]
    #test exceptions
    def del_no_stone():
        del position[0]
    exception_test(del_no_stone, KeyError, "'No stones at point 0'")

    def set_bad_group():
        position[0] = 1
    exception_test(set_bad_group, ValueError, 'Not a Group object')

    s = position.size
    def group_already():
        position[s] = gd.Group(size=5, colour=1, liberties=7)
    exception_test(group_already, gd.MoveError, 'Group already at ' + str(s))

    #test deleting and setting groups
    for pt in moves:
        group = position[pt]
        del position[pt]
        position[pt] = group
        assert position[pt] == group
    #test get after a delete
    del position[s]
    for pt in [s, s+1, 2*s, 2*s + 1, 2*s + 2]:
        assert position[pt] == gd.OPEN_POINT
        assert position.board[pt] == pt

def test_Position_move(position_moves):
    """ The fixture makes a number of moves,
    and these assertions test the results in the fixture.
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
    """
    position, moves = position_moves
    groups = [gd.Group(size=1, colour=1, liberties=3),
                gd.Group(size=1, colour=1, liberties=1),
                gd.Group(size=5, colour=1, liberties=7),
                gd.Group(size=5, colour=1, liberties=1),
                gd.Group(size=3, colour=-1, liberties=4),
                gd.Group(size=8, colour=-1, liberties=7),
                ]
    representatives = defaultdict(list)
    for pt in moves:
        representatives[position.board[pt]] += [pt]
        assert moves[pt] == moves[position.board[pt]]

    assert len(representatives) == len(position.groups)

    for repre in position.groups:
        assert repre in representatives
        assert position[repre].size == len(representatives[repre])
        assert position[repre].colour == moves[repre]
        assert position[repre] in groups

    #test exploits player colour as +/-1
    assert sum([group.color for group in position_moves.groups]) == position_moves.next_player

    position.move(2, gd.BLACK)
    assert position[1] == gd.Group(size=8, colour=gd.BLACK, liberties=6)

    position.move(position.size**2-1, gd.WHITE)
    assert position[position.size**2-1] == gd.Group(size=1, colour=gd.WHITE, liberties=2)
    position.move(position.size**2-2, gd.WHITE)
    assert position[position.size**2-2] == gd.Group(size=2, colour=gd.WHITE, liberties=3)

def test_move_exceptions(position_moves):
    position, moves = position_moves

    def suicide_move():
        position.move((position.size**2)-1, gd.BLACK)
    exception_test(suicide_move, gd.MoveError, 'Playing self capture.')

    def suicide_moveII():
        position.move(0, gd.WHITE)
    exception_test(suicide_moveII, gd.MoveError, 'Playing self capture.')

    def kolock_point():
        position.move(2, gd.WHITE)
        position.move(3, gd.BLACK)
    exception_test(kolock_point, gd.MoveError, 'Playing on a ko point.')

    for pt in moves:
        def existing_stone():
            position.move(pt, gd.WHITE)
        exception_test(existing_stone, gd.MoveError, 'Playing on another stone.')

    def bad_colour():
        position.move(25, 't')
    exception_test(bad_colour, ValueError, 'Unrecognized move colour: t')

def test_Position_neigh_groups(position_moves):
    position, moves = position_moves

    for pt in position.board:
        groups = [(repre, group) for repre, group in position.neigh_groups(pt)]
        assert len(groups) == len(set(groups))      #no repeat groups

        the_expected_groups = [position[neigh_pt] for neigh_pt in gd.NEIGHBORS[position.size][pt]]
        for repre, group in groups:
            assert position[repre] is group
            assert group in the_expected_groups

def test_Group_init():
    for col, size, lib in itertools.product([gd.BLACK, gd.WHITE], range(361), range(361)):
        assert gd.Group(colour=col,  size=size, liberties=lib,) == (col, size, lib)
