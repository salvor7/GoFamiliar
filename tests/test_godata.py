import itertools
from collections import defaultdict
from copy import deepcopy

import pytest

import go
import tests.test_fixtures as fixt

fixture_params = [n for n in range(9, 26, 2)]


@pytest.fixture(params=fixture_params)
def position(request):
    return fixt.open_position()(size=request.param)


@pytest.fixture(params=fixture_params)
def position_moves(request):
    return fixt.first_position()(s=request.param)


def test_make_neighbors(position):
    """Corners have two neighbors; Edges points have 3, and Centre points have 4.
    """

    def result_row(i, size):
        return [i] + [i + 1] * (size - 2) + [i]

    size = position.size
    neigh_counts = [0] * (size ** 2)
    first_row = result_row(2, size)
    last_row = result_row(2, size)
    middle_row = result_row(3, size)
    desired_result = first_row + (middle_row) * (size - 2) + last_row

    for c, neighs in go.make_neighbors(size=size):
        for pt in list(neighs):
            neigh_counts[pt] += 1

    assert desired_result == neigh_counts


def test_Position_initial(position):
    assert position.kolock is None
    assert position.next_player is go.BLACK
    assert len(position.board._pointers) == position.size ** 2
    assert position.komi == -7.5


def test_Position_groups(position_moves):
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
    groups = [gd.Group(size=1, colour=1, liberties=frozenset({0, s + 1, 2})),
              gd.Group(size=1, colour=1, liberties=frozenset({2})),
              gd.Group(size=5, colour=1,
                       liberties=frozenset(
                               {0, 2, s + 1, 2 * s + 3, 3 * s, 3 * s + 1, 3 * s + 2})),
              gd.Group(size=5, colour=1, liberties=frozenset({s ** 2 - 1})),
              gd.Group(size=3, colour=-1,
                       liberties=frozenset({s + 5, 5, 2 * s + 3, 2 * s + 4})),
              gd.Group(size=8, colour=-1,
                       liberties=frozenset({(s - 1) * s - 6, (s) * s - 6, (s - 3) * s - 4,
                                            (s - 3) * s - 3, (s - 3) * s - 2,
                                            (s - 3) * s - 1,
                                            (s - 2) * s - 5})
                       ),
              ]
    for repre in position.groups:
        assert position[repre] in groups


def test_Position_board(position_moves):
    position, moves = position_moves
    s = position.size
    representatives = defaultdict(list)
    for pt in moves:
        representatives[position.board[pt]] += [pt]
        assert moves[pt] == moves[position.board[pt]]  # colour test

    assert len(representatives) == len(position.groups)

    for repre in position.groups:
        assert repre in representatives
        assert position[repre].size == len(representatives[repre])
        assert position[repre].colour == moves[repre]


def test_Position_group_handling(position_moves):
    position, moves = position_moves
    s = position.size
    position.move(move_pt=s - 1, colour=go.BLACK)
    assert position[s - 1] == go.Group(size=1, colour=go.BLACK,
                                       liberties=frozenset({s - 2, 2 * s - 1}))
    position.move(move_pt=2, colour=go.BLACK)
    assert position[1] == go.Group(size=8, colour=go.BLACK,
                                   liberties=frozenset(
                                           {0, s + 1, 2 * s + 3, 3 * s, 3 * s + 1,
                                            3 * s + 2}))


def test_move_capture(position_moves):
    position, moves = position_moves
    s = position.size

    position.move(s ** 2 - 1, go.WHITE)  # capture corner
    assert position[s ** 2 - 1] == go.Group(size=1, colour=go.WHITE,
                                            liberties=frozenset(
                                                    {(s - 1) * s - 1, s ** 2 - 2}))
    assert position[s ** 2 - 5] == go.Group(size=8, colour=go.WHITE,
                                            liberties=frozenset(
                                                    {(s - 1) * s - 6, (s) * s - 6,
                                                     (s - 3) * s - 4,
                                                     (s - 3) * s - 3, (s - 3) * s - 2,
                                                     (s - 3) * s - 1,
                                                     (s - 2) * s - 5, (s - 1) * s - 2,
                                                     (s - 1) * s - 1,
                                                     s ** 2 - 4, s ** 2 - 3}
                                            ))
    for lib in position[s ** 2 - 5].liberties | position[s ** 2 - 1].liberties:
        assert position[lib] is go.OPEN_POINT

    def kolock_point():
        position.move(2, go.WHITE)
        position.move(3, go.BLACK) # the play on a ko

    fixt.exception_test(kolock_point, go.MoveError, 'Playing on a ko point.')
    assert position[2] == go.Group(colour=go.WHITE, size=1, liberties=frozenset({3}))


def test_move_exceptions(position_moves):
    position, moves = position_moves

    def suicide_move():
        position.move((position.size ** 2) - 1, gd.BLACK)
    fixt.exception_test(suicide_move, gd.MoveError, 'Playing in a friendly eye')

    def suicide_moveII():
        position.move(0, gd.WHITE)
    fixt.exception_test(suicide_moveII, gd.MoveError, 'Playing self capture.')

    for pt in moves:
        def existing_stone():
            position.move(pt, gd.WHITE)
        fixt.exception_test(existing_stone, gd.MoveError, 'Playing on another stone.')

    def bad_colour():
        position.move(4 * position.size, 't')
    fixt.exception_test(bad_colour, ValueError, 'Unrecognized move colour: t')


def test_Position_actions(position_moves):
    position, moves = position_moves
    s = position.size
    assert (set(range(s ** 2)) - position.actions) - set(moves.keys()) == set()

    assert 2 in position.actions
    assert 3 not in position.actions
    position.move(move_pt=2, colour=go.WHITE)
    assert 2 not in position.actions
    assert 3 in position.actions    # added after capture

    term_position = position.random_playout()
    for action in term_position.actions:
        try:
            term_position.move(action, colour=go.BLACK)
        except go.MoveError:
            pass
        else:
            assert False
        try:
            term_position.move(action, colour=go.WHITE)
        except go.MoveError:
            pass
        else:
            assert False


def test_score(position_moves):
    position, moves = position_moves
    black_stones, black_liberties = 12, 8
    white_stones, white_liberties = 11, 11
    assert position.score() == black_stones + black_liberties - white_stones - white_liberties

    term_position = position.random_playout()
    assert term_position is not position
    black_stones, white_stones = 0, 0
    black_liberties, white_liberties = set(), set()
    for group in term_position.groups.values():
        if group.colour == 1:
            black_stones += group.size
            black_liberties |= group.liberties
        else:
            white_stones += group.size
            white_liberties |= group.liberties
    assert black_stones + len(black_liberties) - white_stones - len(white_liberties)


def test_Group_init():
    for col, size, lib in itertools.product([go.BLACK, go.WHITE], range(361), range(361)):
        assert go.Group(colour=col, size=size, liberties=lib, ) == (col, size, lib)

