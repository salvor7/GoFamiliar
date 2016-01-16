from collections import namedtuple, defaultdict
import random
from copy import deepcopy

import numpy as np
from util.unionfind import UnionFind


#"colours" of the pieces which might be on the board
BLACK = 1
WHITE = -1
OPEN = 0


def make_boxes(size=19):
    """Generator of box coordinates

    Neighbor checking is the most common function in the MCTS, so we have used np.array for a
    speed boost.

    This doctest creates the boxes for this grid.
    0 1 2
    3 4 5
    6 7 8
    >>> for c, neigh, diag in make_boxes(size=3):
    ...     print(c, neigh, diag)
    0 [3 1] [4]
    1 [4 0 2] [5 3]
    2 [5 1] [4]
    3 [0 6 4] [1 7]
    4 [1 7 3 5] [0 2 8 6]
    5 [2 8 4] [1 7]
    6 [3 7] [4]
    7 [4 6 8] [3 5]
    8 [5 7] [4]

    :param size: int for board size
    :yield: int, np.array  for coordinate and array of neighbors.
    """
    for pt in range(size ** 2):
        if pt < size:
            up = None
            up_left = None
            up_right = None
        else:
            up = pt - size
            up_left = pt - size - 1
            up_right = pt - size + 1

        if pt >= size * (size - 1):
            down = None
            down_left = None
            down_right = None
        else:
            down = pt + size
            down_left = pt + size - 1
            down_right = pt + size + 1

        if pt % size == 0:
            left = None
            up_left = None
            down_left = None
        else:
            left = pt - 1

        if (pt + 1) % size == 0:
            right = None
            up_right = None
            down_right = None
        else:
            right = pt + 1
        neighbors = [pt for pt in (up, down, left, right) if pt is not None]
        diagonals = [pt for pt in (up_left, up_right, down_right, down_left) if pt is not None]
        yield pt, np.array(neighbors, dtype=np.int16), np.array(diagonals, dtype=np.int16)


def make_neighbors(size=19):
    """Generator of neighbors coordinates

    In general, [c+1, c-1, c+size, c-size] are the coordinates of neighbors of a flatten board.
    Special care must be taken for the edges, and the 4 if statements limit neighbors for
    coordinates along the edge.
    Neighbor checking is the most common function in the MCTS, so we have used np.array for a
    speed boost.

    This doctest creates the neighbors for this grid.
    0 1 2
    3 4 5
    6 7 8
    >>> for c, neigh in make_neighbors(size=3):
    ...     print(c,neigh)
    0 [3 1]
    1 [4 0 2]
    2 [5 1]
    3 [0 6 4]
    4 [1 7 3 5]
    5 [2 8 4]
    6 [3 7]
    7 [4 6 8]
    8 [5 7]

    :param size: int for board size
    :yield: int, np.array  for coordinate and array of neighbors.
    """
    for pt, neighbors, _ in make_boxes(size=size):
        yield pt, neighbors


NEIGHBORS = {n: {pt: neigh for pt, neigh in make_neighbors(size=n)} for n in
             range(9, 26, 2)}


BOXES = {n: {pt: (neigh, diag) for pt, neigh, diag in make_boxes(size=n)} for n in
             range(9, 26, 2)}


class Group(namedtuple('Group', 'colour size liberties')):
    @property
    def libs(self):
        return len(self.liberties)


OPEN_POINT = Group(colour=OPEN, size=0, liberties=frozenset())


class Position():
    """A Go game position object

    An object to track all the aspects of a go game. It uses a "thick" representation of
    the board to store group information.
    >>> Position().size
    19
    >>> Position(size=13).size
    13
    """

    def __init__(self, moves=None, size=19, komi=7.5, lastmove=None, kolock=None):
        """Initialize a Position with a board of size**2

        :param size: int
        >>> pos = Position()
        """
        self.board = UnionFind(size_limit=size ** 2)
        self.groups = {}
        self.kolock = kolock
        self.komi = komi
        self.size = size
        self.next_player = BLACK
        self.actions = set(range(size ** 2))

        try:
            for pt in moves:
                self.move(pt)
        except TypeError:
            pass

    def __getitem__(self, pt):
        """Return group pt is a part of

        If point have bi group, returns an OPEN_POINT group object.
        :param pt: int
        :return: Group
        >>> Position()[200]
        Group(colour=0, size=0, liberties=frozenset())
        """
        repre = self.board[pt]
        try:
            return self.groups[repre]
        except KeyError:
            if pt != repre:  # pointing to a removed-group representative
                self.board._pointers[pt] = pt
            return OPEN_POINT

    def __setitem__(self, key, group):
        """Set group object

        :param key: int
        :param data: Group

        >>> pos = Position()
        >>> pos[200] = Group(colour=1, size=1, liberties=frozenset({199, 201, 219, 181}))
        >>> pos[200]
        Group(colour=1, size=1, liberties=frozenset({201, 219, 181, 199}))
        """
        if type(group) is not Group:
            raise ValueError('Not a Group object')
        self.groups[self.board[key]] = group

    def __delitem__(self, pt):
        """Delete group at point pt

        :param pt: int
        >>> pos = Position()
        >>> pos[100] = Group(size=1, colour=1, liberties=frozenset(NEIGHBORS[19][100]))
        >>> del pos[100]
        """
        repre = self.board[pt]
        try:
            del self.groups[repre]
        except KeyError:
            raise KeyError('No stones at point ' + str(pt))

    def pass_move(self):
        """Execute a passing move
        """
        self.kolock = None
        self.next_player *= -1

    def random_playout(self):
        """Play a random move

        :return: int
        >>> type(Position().random_playout())
        <class 'godata.Position'>
        """
        position = deepcopy(self)
        passes = 0
        while passes < 2:
            tried = set()
            while tried != position.actions:
                move_pt = random.sample(position.actions - tried, k=1)[0]
                try:
                    position.move(move_pt)
                except MoveError:
                    tried |= {move_pt}
                    continue
                passes = 0
                tried = set()   # a move resets tried
            position.pass_move()
            passes +=1

        return position

    def score(self):
        """Return the score

        Well defined on any position, but quite inaccurate for non-terminal positions.
        :return: int
        >>> Position().score()
        0
        """
        black_stones, white_stones = 0, 0
        black_liberties, white_liberties = set(), set()
        for group in self.groups.values():
            if group.colour == 1:
                black_stones += group.size
                black_liberties |= group.liberties
            else:
                white_stones += group.size
                white_liberties |= group.liberties
        return black_stones + len(black_liberties) - white_stones - len(white_liberties)

    def move(self, move_pt, colour=None):
        """Play a move on a go board

        :param pt: int
        :param colour: +1 or -1
        :raise: ValueError
        :raise: MoveError
        :return: Position

        Completes all the checks to a ensure legal move, raising a MoveError if illegal.
        Adds the move to the position, and returns the position.
        >>> move_pt = 200
        >>> pos = Position()
        >>> pos.move(move_pt, colour=BLACK)
        >>> pos[move_pt]
        Group(colour=1, size=1, liberties=frozenset({201, 219, 181, 199}))
        >>> pos.move(move_pt+1, colour=BLACK)
        >>> pos[move_pt+1]
        Group(colour=1, size=2, liberties=frozenset({199, 202, 181, 182, 219, 220}))
        """
        def basic_checks():
            """Check move can be played

            :nonlocal param: self
            :nonlocal param: move_pt
            :nonlocal assigned param: colour
            """
            nonlocal colour

            if colour is None:
                colour = self.next_player
            elif colour not in [BLACK, WHITE]:
                raise ValueError('Unrecognized move colour: ' + str(colour))
            if move_pt == self.kolock:
                raise MoveError('Playing on a ko point.')
            elif self[move_pt] is not OPEN_POINT:
                raise MoveError('Playing on another stone.')

        def no_friendly_eye():
            """Do not play in a friendly eye space

            :nonlocal param: self
            :nonlocal param: move_pt
            :nonlocal param: colour
            :return: dict
            """
            neighbors, diagonals = BOXES[self.size][move_pt]
            neigh_groups = {self.board[neigh_pt]:self[neigh_pt] for neigh_pt in neighbors}

            if OPEN_POINT not in neigh_groups.values():
                neigh_colours = [group.colour for group in neigh_groups.values()]
                if -colour not in neigh_colours:
                    diag_colours = [self[pt].colour for pt in diagonals]
                    if diag_colours.count(-colour) <= max(0, len(diag_colours) - 3):
                        raise MoveError('Playing in a friendly eye')

            return neigh_groups

        def no_self_capture():
            """Reducing your own liberties to zero is an illegal move

            :nonlocal param: move_pt
            :nonlocal param: colour
            :nonlocal param: neigh_groups
            :return: dict
            """
            neigh_details = defaultdict(list)
            for group_pt, group in neigh_groups.items():
                if group is OPEN_POINT:
                    neigh_details['my liberties'] += [group_pt]
                elif group.colour == colour:
                    neigh_details['my liberties'] += list(group.liberties - {move_pt})
                    neigh_details['my groups'] += [(group_pt, group)]
                    neigh_details['my size'] += [group.size]
                elif group.libs == 1:
                    neigh_details['dead opponent'] += [(group_pt, group)]
                else:
                    neigh_details['alive opponent'] += [(group_pt, group)]

            if 'dead opponent' not in neigh_details and neigh_details['my liberties'] == []:
                raise MoveError('Playing self capture.')

            return neigh_details

        def capture(dead_pt):
            """Remove captures and update surroundings

            :nonlocal param: neigh_groups
            """
            def neigh_groups_dict(pt):
                """Return the groups around pt

                :param pt: int
                :return: dict
                """
                neighbors = NEIGHBORS[self.size][dead_pt]
                return {self.board[neigh_pt]:self[neigh_pt] for neigh_pt in neighbors}

            tracking = defaultdict(list)
            tracking['to remove'] = [dead_pt]
            while len(tracking['to remove']) > 0:
                remove_pt = tracking['to remove'].pop()
                for group_pt, group in neigh_groups_dict(remove_pt).items():
                    if group.colour == -self[dead_pt].colour:
                        # add liberties back
                        self[group_pt] = Group(colour=group.colour, size=group.size,
                                               liberties=group.liberties | {remove_pt})
                for neigh_pt in NEIGHBORS[self.size][remove_pt]:
                    # spread out search
                    not_removed = neigh_pt not in tracking['removed']
                    in_dead_group = (self[neigh_pt].colour == self[dead_pt].colour)
                    if not_removed and in_dead_group:
                        tracking['to remove'] += [neigh_pt]

                tracking['removed'] += [remove_pt]
                self.actions |= {remove_pt}

            del self[dead_pt]
            for removed_pt in tracking['removed']:
                _ = self[removed_pt]    # update unionfind in getitem

        def update_groups():
            """Update and/or remove opponent groups

            :nonlocal param: move_pt
            :nonlocal param: colour
            :nonlocal param: neigh_details
            """
            for opp_pt, opp_group in neigh_details['alive opponent']:
                self[opp_pt] = Group(colour=opp_group.colour,
                                 size=opp_group.size,
                                 liberties=opp_group.liberties - {move_pt})

            captured = 0
            for dead_pt, dead_group in neigh_details['dead opponent']:
                captured += dead_group.size
                capture(dead_pt)

            if captured == 1:
                self.kolock = neigh_details['dead opponent'][0][0]
            else:
                self.kolock = None

            for group_pt, group in neigh_details['my groups']:
                self.board[move_pt] = self.board[group_pt]
                del self[group_pt]

            self[move_pt] = Group(colour=colour,
                                  size=sum(neigh_details['my size']) + 1,
                                  liberties=frozenset(neigh_details['my liberties']))
        #---------Main steps----------
        basic_checks()
        neigh_groups = no_friendly_eye()
        neigh_details = no_self_capture()
        update_groups()

        self.next_player = -colour
        self.actions -= {move_pt}


class MoveError(Exception):
    """The exception throw when an illegal move is made.

    ie repeat play, suicide or on a ko
    """
    pass


class TerminalPosition(StopIteration):
    """Exception raised when a position is terminal and a move is attempted.
    """
    pass