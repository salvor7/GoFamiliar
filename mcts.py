import random
import godata as gd


def is_eye(position, pt, colour):
    """Determines if pt is an eye of colour

    :param position: gd.Position
    :param pt: int
    :return: boolean
    """
    neighbors, diagonals = gd.BOXES[19][pt]
    neigh_colours = [position[pt].colour for pt in neighbors]

    if gd.OPEN in neigh_colours or -colour in neigh_colours:
        return False

    diag_colours = [position[pt].colour for pt in diagonals]

    return diag_colours.count(-colour) <= max(0, len(diag_colours) - 3)


def search(position):
    intersections = list(range(0, 19 ** 2 - 1))
    random.shuffle(intersections)

    for move in intersections:
        if position[move] is gd.OPEN_POINT and not is_eye(position, move, colour=position.next_player):
            try:
                position.check_move(test_pt=move, colour=position.next_player)
            except gd.MoveError:
                pass
            else:
                return move
    raise gd.MoveError('Terminal Position')


