import random

import godata as gd

def search(position):
    intersections = list(range(0, 19**2-1))
    random.shuffle(intersections)

    for move in intersections:
        if position[move] is gd.OPEN_POINT:
            try:
                position.check_move(test_pt=move, colour=position.next_player)
            except gd.MoveError:
                pass
            else:
                break
    else:
        raise gd.MoveError('Terminal Position')

    return move
