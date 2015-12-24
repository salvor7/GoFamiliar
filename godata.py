from collections import namedtuple

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

Group = namedtuple('Group', 'colour size liberties')
OPEN_POINT = Group(colour=0, size=0, liberties=0)

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

        :param pt: int
        :return: Group
        >>> pt = 200
        >>> Position()[pt]
        Group(colour=0, size=0, liberties=0)
        """
        repre = self.board[pt]
        try:
            return self.groups[repre]
        except KeyError:
            if pt is not repre:  #pointing to a dead group representative
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
        self.groups[self.board[key]] = group

    def __delitem__(self, pt):
        """Delete group at point pt

        :param pt: int
        >>> pos = Position()
        >>> pos[100] = Group(size=1, colour=1, liberties=4)
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
        >>> pt = 200
        >>> pos = Position()
        >>> pos.move(pt, colour=BLACK)[pt]
        Group(colour=1, size=1, liberties=4)
        >>> pos.move(pt+1, colour=BLACK)[pt+1]
        Group(colour=1, size=2, liberties=6)
        """
        if move_pt == self.kolock:
            raise MoveError('Playing on a ko point.')
        elif self[pt] is not OPEN_POINT:
            raise MoveError('Playing on another stone.')

        if colour is None:
            colour = self.next_player
        elif colour not in [BLACK, WHITE]:
            raise ValueError('Unrecognized move colour: ' + str(colour))

        liberty_count = 0
        player_groups = []
        dead_opp_groups = []
        for qt, group in self.neigh_groups(pt):
            if group is OPEN_POINT:
                liberty_count += 1
            elif group.colour == colour:
                liberty_count += group.liberties - 1
                player_groups += [qt]
            elif group.liberties == 1:
                dead_opp_groups += [qt]
        if liberty_count == 0 and len(dead_opp_groups) == 0:
            raise MoveError('Playing self capture.')

        #Checks complete. Start making changes to Position
        size = 0
        for group_pt in player_groups:
            try:
                size += self[group_pt].size
            except KeyError:
                continue
            self.board[move_pt] = group_pt
            try:
                del self[group_pt]
            except KeyError:
                group_merged = (self.board[group_pt] == self.board[move_pt])
                if not group_merged:
                    raise
        self[move_pt] = Group(colour=colour, size=size+1, liberties=liberty_count)

        captured = 0
        for group_pt in dead_opp_groups:
            captured += self[group_pt].size
            try:
                del self[group_pt]
            except KeyError:
                group_removed = (self.board[group_pt] == self.board[move_pt])
                if not group_removed:
                    raise

        if captured == 1:
            self.ko = dead_opp_groups[0]
        else:
            self.ko = None

        self.next_player *= -1

        return self

    def neigh_groups(self, pt):
        """Find the groups and their representatives around pt

        :param pt: int
        :yield: Group

        >>> pt = 200
        >>> next(Position().neigh_groups(pt))
        (181, Group(colour=0, size=0, liberties=0))
        """
        for qt in NEIGHBORS[self.size][pt]:
            yield self.board[qt], self[qt]

class MoveError(Exception):
    """The exception throw when an illegal move is made.

    ie repeat play, suicide or on a ko
    """
    pass
