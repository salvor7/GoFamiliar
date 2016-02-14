import itertools
from collections import defaultdict, namedtuple
import numpy as np

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
    QuasiGroup = namedtuple('QuasiGroup', 'colour, stones')
    groups = [QuasiGroup(colour=1, stones={3},),
              QuasiGroup(colour=1, stones={1},),
              QuasiGroup(colour=1, stones={s, 2*s, 2*s+1, 2*s+2, s+2}, ),
              QuasiGroup(colour=1, stones={s**2-s-1, s**2-3, s**2-4, s**2-s-2, s**2-2}),
              QuasiGroup(colour=-1, stones={4, s+3, s+4}, ),
              QuasiGroup(colour=-1, stones={s*(s-2)-4, s*(s-2)-3, s*(s-2)-2, s*(s-2)-1,
                                          s*(s-1)-5, s*(s-1)-4, s*(s-1)-3,
                                          s**2-5}),
              ]
    position.board.discover_all_libs()

    for pt in position.board:
        group, _ = position.board._find(pt=pt)
        assert group is None or QuasiGroup(colour=group.colour, stones=group._stones) in groups

    position.move(move_pt=s-1, colour=go.BLACK)
    assert position.board._find(s-1)[0] == go.Group(stones={s-1}, colour=go.BLACK,)
    position.move(move_pt=2, colour=go.BLACK)
    position.board.discover_liberties(group_pt=2, limit=np.infty)
    assert position.board._find(1)[0] == go.Group(colour=go.BLACK,
                                               stones={1, 2, 3,
                                                       s, s+2,
                                                       2*s, 2*s+1, 2*s+2,})


def test_move_capture(position_moves):
    position, moves = position_moves
    s = position.size

    position.move(s ** 2 - 1, go.WHITE)  # capture corner
    assert position.board._find(s ** 2 - 1)[0] == go.Group(stones={s**2-1}, colour=go.WHITE,)

    position.board.discover_liberties(s ** 2 - 5, limit=np.infty)
    position.board.discover_liberties(s ** 2 - 1, limit=np.infty)
    group1, _ = position.board._find(pt=s**2-1)
    group2, _ = position.board._find(pt=s**2-5)
    for lib in (group1._liberties | group2._liberties):
        assert position.board._find(lib)[0] is None
        assert lib in position.actions

    def kolock_point():
        position.move(2, go.WHITE)
        position.move(3, go.BLACK) # the play on a ko

    with pytest.raises(go.MoveError) as excinfo:
        kolock_point()
    assert 'ko locked point' in str(excinfo.value)

    assert position.board._find(2)[0] == go.Group(colour=go.WHITE, stones={2}, )


def test_position_playout(position):
    """Added to test a bug where during playout _stones were not being removed
    when they had no _liberties.
    """
    passes = 0
    moves = []
    board = position.board
    while passes < 2:
        try:
            moves.append(position.random_move())
        except go.MoveError:
            position.pass_move()
            passes +=1
        else:
            passes = 0
            for pt in board:
                if board.colour(pt) is not go.OPEN:
                    for neigh_pt in board.neighbors[pt]:
                        group, _ = board._find(pt=neigh_pt)
                        try:
                            # pt is no longer in the liberty set
                            assert pt not in group._liberties
                        except AttributeError:
                            assert group is None
                else:
                    assert pt in position.actions


def test_move_exceptions(position_moves):
    position, moves = position_moves

    def suicide_move():
        position.move((position.size ** 2) - 1, go.BLACK)

    def suicide_moveII():
        position.move(0, go.WHITE)

    def play_on_all_moves():
        for pt in moves:
            def existing_stone():
                position.move(pt, go.WHITE)
            yield existing_stone

    def bad_colour():
        position.move(4 * position.size, 't')

    excep_functionsI = [(suicide_move,'friendly eye'),
                        (suicide_moveII,'self capture'),
                        (bad_colour,'Unrecognized move colour')
                       ]

    excep_functions2 = [(func,'Playing on another stone')
                            for func in play_on_all_moves()]
    excep_functions = dict(excep_functionsI+excep_functions2)
    for excep_func, message in excep_functions.items():
        with pytest.raises(go.MoveError) as excinfo:
            excep_func()
        assert message in str(excinfo.value)


def test_Position_actions(position_moves):
    position, moves = position_moves
    s = position.size
    assert (set(range(s ** 2)) - position.actions) - set(moves.keys()) == set()

    assert 2 in position.actions
    assert 3 not in position.actions
    position.move(move_pt=2, colour=go.WHITE)
    assert 2 not in position.actions
    assert 3 in position.actions    # added after capture

    position.move(move_pt=s**2-1, colour=go.WHITE)
    assert {s**2-s-1, s**2-3, s**2-4, s**2-s-2, s**2-2}.issubset(position.actions)

    term_position, moves = position.random_playout()
    for action in term_position.actions:
        with pytest.raises(go.MoveError):
            term_position.move(action, colour=go.BLACK)
        with pytest.raises(go.MoveError):
            term_position.move(action, colour=go.WHITE)


def test_score(position_moves):
    position, moves = position_moves
    black_stones, black_liberties = 12, 8
    white_stones, white_liberties = 11, 11
    komi = -7.5
    assert position.score() == black_stones + black_liberties - white_stones - white_liberties + komi

    term_position, moves = position.random_playout()
    assert term_position is not position

    score = term_position.komi
    for pt in term_position.board:
        score += term_position.board.colour(pt)
        if term_position.board.colour(pt) == go.OPEN:
            # will find the 1 neighbor colour unless it is a seki liberty, then its 0
            neigh_colours = set([term_position.board.colour(neigh_pt)
                                    for neigh_pt in term_position.board.neighbors[pt]])
        else:
            neigh_colours = []
        score += sum(neigh_colours)

    assert score == term_position.score()


def test_Group_init():
    for col, pt in itertools.product([go.BLACK, go.WHITE], range(361)):
        group = go.Group(colour=col, stones={pt} )
        assert group.colour == col
        assert group.size == 1
        assert group.liberties == 0
