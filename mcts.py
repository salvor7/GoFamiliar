import random
import godata as gd


def not_eye(position, move):
    group_colour = set([group.colour for _, group in position.neigh_groups(move)])

    s = len(group_colour)
    return group_colour not in [[1] * s, [-1] * s]


def search(position):
    intersections = list(range(0, 19 ** 2 - 1))
    random.shuffle(intersections)

    for move in intersections:
        if position[move] is gd.OPEN_POINT and not_eye(position, move):
            try:
                position.check_move(test_pt=move, colour=position.next_player)
            except gd.MoveError:
                pass
            else:
                break
    else:
        raise gd.MoveError('Terminal Position')

    return move
