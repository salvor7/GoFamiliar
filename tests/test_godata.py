import itertools
from collections import defaultdict
from copy import deepcopy

import pytest

import godata as gd
from tests.test_fixtures import exception_test, first_position

fixture_params = [n for n in range(9, 26, 2)]

@pytest.fixture(params=fixture_params)
def position(request):
    return gd.Position(size=request.param)

@pytest.fixture(params=fixture_params)
def position_moves(request):
    return first_position()(s=request.param)

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

def test_Position_getsetdel(position_moves):

    position, moves = position_moves
    s = position.size
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
    s = position.size
    groups = [gd.Group(size=1, colour=1, liberties=frozenset({0, s+1, 2})),
                gd.Group(size=1, colour=1, liberties=frozenset({2})),
                gd.Group(size=5, colour=1,
                         liberties=frozenset({0, 2, s+1, 2*s + 3, 3*s, 3*s + 1, 3*s + 2})),
                gd.Group(size=5, colour=1, liberties=frozenset({s**2 - 1})),
                gd.Group(size=3, colour=-1,
                         liberties=frozenset({s+5, 5, 2*s + 3, 2*s + 4})),
                gd.Group(size=8, colour=-1,
                         liberties=frozenset({(s-1)*s - 6, (s)*s - 6, (s-3)*s - 4,
                                              (s-3)*s - 3, (s-3)*s - 2, (s-3)*s - 1,
                                              (s-2)*s - 5})
                         ),
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

    position.move(move_pt=s-1, colour=gd.BLACK)
    assert position[s-1] == gd.Group(size=1, colour=gd.BLACK,
                                     liberties=frozenset({s-2, 2*s-1}))
    position.move(move_pt=2, colour=gd.BLACK)
    assert position[1] == gd.Group(size=8, colour=gd.BLACK,
                                   liberties=frozenset({0, s+1, 2*s + 3, 3*s, 3*s + 1, 3*s + 2}))

def test_check_moves(position_moves):
    position, moves = position_moves
    s = position.size

    test_lists, test_counts = position.check_move(test_pt=2, colour=gd.BLACK)
    assert type(test_lists) is defaultdict
    assert len(test_lists) == 3
    assert test_lists['test point'] == 2
    assert len(test_lists['my groups']) == 3
    assert set(test_lists['groups liberties']) == {0, s+1, 2*s + 3, 3*s, 3*s + 1, 3*s + 2}

    assert type(test_counts) is defaultdict
    assert len(test_counts) == 2
    assert test_counts['test point'] == 2
    assert test_counts['groups size'] == 7

    positionII = deepcopy(position)
    def mismatch_test_and_move():
        position.move(move_pt=0, colour=gd.BLACK, test_lists=test_lists, test_counts=test_counts)
    exception_test(mismatch_test_and_move, ValueError, 'Tested point and move point not equal')
    position.move(move_pt=2, colour=gd.BLACK, test_lists=test_lists)

    test_lists, test_counts = positionII.check_move(test_pt=2, colour=gd.WHITE)
    assert len(test_lists) == 4
    assert test_lists['test point'] == 2
    assert test_lists['groups liberties'] == []
    assert len(test_lists['alive opponent']) == 2
    assert len(test_lists['dead opponent']) == 1

    assert len(test_counts) == 2
    assert test_counts['test point'] == 2
    assert test_counts['captures'] == 1

def test_move_capture(position_moves):
    position, moves = position_moves
    s = position.size

    position.move(s**2-1, gd.WHITE)         #capture corner
    assert position[s**2-1] == gd.Group(size=1, colour=gd.WHITE,
                                        liberties=frozenset({(s-1)*s - 1, s**2 - 2}))
    assert position[s**2-5] == gd.Group(size=8, colour=gd.WHITE,
                                        liberties=frozenset(
                                            {(s-1)*s - 6, (s)*s - 6, (s-3)*s - 4,
                                              (s-3)*s - 3, (s-3)*s - 2, (s-3)*s - 1,
                                              (s-2)*s - 5, (s-1)*s - 2, (s-1)*s - 1,
                                             s**2 - 4, s**2 - 3}
                                            )
                                        )
    for lib in position[s**2-5].liberties | position[s**2-1].liberties:
        assert position[lib] is gd.OPEN_POINT

    def kolock_point():
        position.move(2, gd.WHITE)
        position.move(3, gd.BLACK)
    exception_test(kolock_point, gd.MoveError, 'Playing on a ko point.')
    assert position[2] == gd.Group(colour=gd.WHITE, size=1, liberties=frozenset({3}))

def test_move_exceptions(position_moves):
    position, moves = position_moves

    def suicide_move():
        position.move((position.size**2)-1, gd.BLACK)
    exception_test(suicide_move, gd.MoveError, 'Playing self capture.')

    def suicide_moveII():
        position.move(0, gd.WHITE)
    exception_test(suicide_moveII, gd.MoveError, 'Playing self capture.')

    for pt in moves:
        def existing_stone():
            position.move(pt, gd.WHITE)
        exception_test(existing_stone, gd.MoveError, 'Playing on another stone.')

    def bad_colour():
        position.move(4*position.size, 't')
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
