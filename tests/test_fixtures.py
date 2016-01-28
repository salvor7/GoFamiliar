from collections import defaultdict

import go

def open_position():
    return go.Position

def first_position():
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
    def position_moves(s):
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
        position = go.Position(size=s)
        stones_counts = defaultdict()
        for pt, symbol in enumerate(board):
            if symbol == 'X':
                position.move(move_pt=pt, colour=go.BLACK)
                stones_counts[pt] = go.BLACK
            elif symbol == 'o':
                position.move(move_pt=pt, colour=go.WHITE)
                stones_counts[pt] = go.WHITE
        return position, stones_counts
    return position_moves

def exception_test(func, err, message):
    try:
        func()
    except err as err:
        assert message == str(err)
    else:
        assert False