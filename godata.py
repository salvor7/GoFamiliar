from collections import namedtuple, defaultdict

import numpy as np

from util.unionfind import UnionFind

BLACK = 1
WHITE = -1


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
    for pt in range(size**2):
        if pt < size:
            up = []
        else:
            up = [pt - size]

        if pt >= size*(size - 1):
            down = []
        else:
            down = [pt + size]

        if pt % size == 0:
            left = []
        else:
            left = [pt - 1]

        if (pt + 1) % size == 0:
            right = []
        else:
            right = [pt + 1]

        yield pt, np.array(up+down+left+right)

NEIGHBORS = {n:{pt:neigh for pt, neigh in make_neighbors(size=n)}  for n in range(9, 26, 2)}

class Group(namedtuple('Group', 'colour size liberties')):
    @property
    def libs(self):
        return len(self.liberties)

OPEN_POINT = Group(colour=0, size=0, liberties=frozenset())

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
            if pt != repre:  #pointing to a removed-group representative
                self.board._pointers[pt] = pt
            return OPEN_POINT

    def __setitem__(self, key, group):
        """Set group object

        :param key: int
        :param value: Group

        >>> pos = Position()
        >>> pos[200] = Group(colour=1, size=1, liberties=4)
        >>> pos[200]
        Group(colour=1, size=1, liberties=4)
        """
        if type(group) is not Group:
            raise ValueError('Not a Group object')
        elif self.board[key] in self.groups:
            raise MoveError('Group already at ' + str(key))
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

    def move(self, move_pt, colour=None):
        """Play a move on a go board

        :param pt: int
        :param colour: +1 or -1
        :return: Position

        Completes all the checks to a ensure legal move, raising a MoveError if illegal.
        Adds the move to the position, and returns the position.
        >>> move_pt = 200
        >>> pos = Position()
        >>> pos.move(move_pt, colour=BLACK)[move_pt]
        Group(colour=1, size=1, liberties=frozenset({201, 219, 181, 199}))
        >>> pos.move(move_pt+1, colour=BLACK)[move_pt+1]
        Group(colour=1, size=2, liberties=frozenset({199, 202, 181, 182, 219, 220}))
        """
        if move_pt == self.kolock:
            raise MoveError('Playing on a ko point.')
        elif self[move_pt] is not OPEN_POINT:
            raise MoveError('Playing on another stone.')

        if colour is None:
            colour = self.next_player
        elif colour not in [BLACK, WHITE]:
            raise ValueError('Unrecognized move colour: ' + str(colour))

        list_tracking = defaultdict(list)
        count_tracking = defaultdict(int)
        for group_pt, group in self.neigh_groups(move_pt):
            if group is OPEN_POINT:
                list_tracking['liberties'] += [group_pt]
            elif group.colour == colour:
                list_tracking['liberties'] += list(group.liberties - {move_pt})
                list_tracking['player'] += [(group_pt, group)]
                count_tracking['size'] += group.size
            else: #group.colour == -colour
                if group.libs == 1:
                    list_tracking['dead opponent'] += [group_pt]
                    count_tracking['captures'] += group.size
                    del self[group_pt]
                else:
                    list_tracking['alive opponent'] += [(group_pt, group)]

        if list_tracking['liberties'] == [] and 'captures' not in count_tracking:
            raise MoveError('Playing self capture.')

        for opp_pt, opp_group in list_tracking['alive opponent']:
            del self[opp_pt]
            self[opp_pt] = Group(colour=opp_group.colour,
                                 size=opp_group.size,
                                 liberties=opp_group.liberties-{move_pt})

        for group_pt, group in list_tracking['player']:
            self.board[move_pt] = self.board[group_pt]
            del self[group_pt]

        self[move_pt] = Group(colour=colour,
                              size=count_tracking['size']+1,
                              liberties=frozenset(list_tracking['liberties']))

        if count_tracking['captures'] == 1:
            self.kolock = list_tracking['dead opponent'][0]
        else:
            self.kolock = None

        self.next_player *= -1

        return self

    def neigh_groups(self, pt):
        """Find the groups and their representatives around pt

        :param pt: int
        :yield: Group

        >>> pt = 200
        >>> next(Position().neigh_groups(pt))
        (181, Group(colour=0, size=0, liberties=frozenset()))
        """
        sent_already = []
        for qt in NEIGHBORS[self.size][pt]:
            if self.board[qt] not in sent_already:
                yield self.board[qt], self[qt]
                sent_already.append(self.board[qt])

class MoveError(Exception):
    """The exception throw when an illegal move is made.

    ie repeat play, suicide or on a ko
    """
    pass
