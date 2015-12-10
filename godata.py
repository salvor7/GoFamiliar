from collections import namedtuple

from unionfind import UnionFind
import numpy as np


def make_neighbors(size=19):
    """Generator of neighbors coordinates

    In general, [c+1, c-1, c+size, c-size] are the coordinates of neighbors of a flatten board.
    Special care must be taken for the edges, and the 4 if statements limit neighbors for
    coordinates along the edge.
    Neighbor checking is the most common function in the MCTS, so we have used np.array for a
    speed boost.

    :param size: int for board size
    :yield: int, np.array  for coordinate and array of neighbors.
    """
    for pt in range(size**2):
        if pt < size:
            up = []
        else:
            up = [pt - 1]
        if pt >= size*(size - 1):
            down = []
        else:
            down = [pt + 1]
        if pt % size == 0:
            left = []
        else:
            left = [pt - size]
        if (pt + 1) % size == 0:
            right = []
        else:
            right = [pt + size]

        yield pt, np.array(up+down+left+right)

NEIGHBORS = {pt:neigh for pt, neigh in make_neighbors()}

Group = namedtuple('Group', 'colour size liberties')
OPEN_POINT = Group(colour=0, size=0, liberties=0)

class Position():
    def __init__(self, size=19):
        self.board = UnionFind(size_limit=size ** 2)
        self.groups = {}
        self.ko = None
        self.size = size
    
    def move(self, pt):
        if self.ko is not None:
            raise MoveError(str(pt) + 'is a ko point')

    def __iter__(self):
        return iter(self.board)

class MoveError(Exception):
    """The exception throw when an illegal move is made.

    ie suicide or on a ko
    """
    pass