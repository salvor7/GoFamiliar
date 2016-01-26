from collections import namedtuple, defaultdict

BLACK = 1
WHITE = -1
OPEN = 0


Group = namedtuple('Group','colour')


OPEN_POINT = Group(colour=OPEN)


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
    0 [3, 1] [4]
    1 [4, 0, 2] [5, 3]
    2 [5, 1] [4]
    3 [0, 6, 4] [1, 7]
    4 [1, 7, 3, 5] [0, 2, 8, 6]
    5 [2, 8, 4] [1, 7]
    6 [3, 7] [4]
    7 [4, 6, 8] [3, 5]
    8 [5, 7] [4]

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
        yield pt, neighbors, diagonals


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
    0 [3, 1]
    1 [4, 0, 2]
    2 [5, 1]
    3 [0, 6, 4]
    4 [1, 7, 3, 5]
    5 [2, 8, 4]
    6 [3, 7]
    7 [4, 6, 8]
    8 [5, 7]

    :param size: int for board size
    :yield: int, np.array  for coordinate and array of neighbors.
    """
    for pt, neighbors, _ in make_boxes(size=size):
        yield pt, neighbors


NEIGHBORS = {n: {pt: neigh for pt, neigh in make_neighbors(size=n)} for n in range(9, 26, 2)}


BOXES = {n: {pt: (neigh, diag) for pt, neigh, diag in make_boxes(size=n)} for n in range(9, 26, 2)}


class Board():
    """A data structure for tracking and querying go data

    It is guaranteed to implements two query methods and one state change method needed
    to implement the rules of Go.
    >>> board = Board()

    Change the colour of a point
    >>> board.change_colour(pt=200, new_colour=BLACK)

    Find the colour of a point
    >>> board.colour(pt=200) == BLACK
    True

    Find a lower bound which is at least 3 on the number of liberties a group has
    >>> len(board.liberty_lb(group_pt=200)) > 2
    True
    """

    def __init__(self, size=19):
        """Initialize a Board object

        Board uses a union find data structure using pointers in a dictionary
        :param size: int
        >>> b = Board()
        """
        self._neighbors = NEIGHBORS[size]
        self._liberties = defaultdict(set)
        self.size = size
        self._pointers = {idx:OPEN_POINT for idx in range(size ** 2)}

    def __iter__(self):
        """Iterator over the size**2 board points

        :return: iter
        """
        return iter(range(self.size ** 2))

    def __getitem__(self, item):
        """Return the group object pointed at by item

        :param item: int or Group
        :return: Group
        >>> Board()[200] == OPEN_POINT
        True
        """
        return self._pointers[item]

    def __setitem__(self, key, value):
        """Change the group key is pointing to

        :param key: int or Group
        :param value: Group
        >>> board = Board()
        >>> board[200] = Group(colour=BLACK)
        >>> board[200].colour == BLACK
        True
        """
        if type(value) is Group:
            self._pointers[key] = value
        else:
            raise BoardError('Expected Group. Got ' + str(type(value)))

    def colour(self, pt):
        """Find the colour of the board at pt

        :param pt: int
        :return: BLACK, WHITE, OPEN
        >>> Board().colour(200) == OPEN
        True
        """
        return self[pt].colour

    def change_colour(self, pt, new_colour):
        """Change the colour at pt

        :param pt: int or iter
        :param new_colour: BLACK, WHITE, OPEN
        >>> board = Board()
        >>> board.change_colour(pt=200, new_colour=BLACK)
        >>> board.colour(200) == BLACK
        True

        An acceptable argument for pt is also an iterator
        >>> board.change_colour(pt=range(19), new_colour=WHITE)
        >>> board.colour(0) == WHITE and board.colour(18) == WHITE
        True
        """
        def update_neigh_libs(pt, add):
            """Update liberties from each neighbor group

            :param pt: int
            """
            for neigh_pt in self._neighbors[pt]:
                neigh_group = self._find(neigh_pt)
                if add and neigh_group is not OPEN_POINT:
                    self._liberties[neigh_group] += {pt}
                else:
                    self._liberties[neigh_group] -= {pt}
        # ------
        if new_colour not in [BLACK, WHITE, OPEN]:
            raise BoardError('Unrecognized colour')
        try:
            points = iter(pt)
        except TypeError:
            points = [pt]
        for pt in points:
            if new_colour is OPEN:
                self[pt] = OPEN_POINT
                update_neigh_libs(pt=pt, add=True)
            else:
                self[pt] = Group(colour=new_colour)
                update_neigh_libs(pt=pt, add=False)
        pass

    def _find(self, node):
        """Follow pointers to top Group

        Updates the pointers also to make future searches require fewer loops
        :param node: int or Group
        :return: Group
        """
        parent = node
        while True:
            try:
                parent = self[parent]
            except KeyError:
                break
        self[node] = parent # shrink union-find pointer tree
        return parent

    def _find_liberties(self, node):
        """Find the liberties of the Group at node

        :param node: int or Group
        :return: set
        """
        group = self._find(node)
        if group is OPEN_POINT:
            raise BoardError('Open points do not have liberties')
        return self._liberties[group]

    def _union(self, f_node, s_node):
        """Union two groups into one

        Union is performed favouring the group with the most liberties.
        Liberties is used as a correlate of group size, so generally, the smaller group
        is added to the larger group to make _find act quicker.
        :param f_node: int or Group
        :param s_node: int of Group
        :return: Group
        """
        f_group, s_group = self._find(f_node), self._find(s_node)
        if f_group is s_group:
            raise BoardError('Cannot union same group')
        elif f_group.colour != s_group.colour:
            raise BoardError('Cannot union different colour stones')

        if len(self._liberties[f_group]) < self._liberties[s_group]:
            f_group, s_group = s_group, f_group # union
        self[s_group] = f_group
        self._liberties[f_group] |= self._liberties[s_group]
        del self._liberties[s_group]
        return f_group

    def _board_crawl(self, start_pt):
        """Generator of the points and neighbors of a single colour area

        There is no guaranteed order of the points.
        :param start_pt: int
        :yield: int
        """
        crawl_colour = self.colour(start_pt)
        to_search = {start_pt}
        while to_search:
            search_pt = to_search.pop()
            for neigh_pt in self._neighbors[search_pt]:
                yield neigh_pt
                if self.colour(neigh_pt) is crawl_colour:
                    to_search |= {neigh_pt}

    def liberty_lb(self, group_pt):
        """Return a lower bound on the number of liberties

        If it returns < 3, it is exact.
        :param group_pt: int
        :return: int
        >>> board = Board()
        >>> board.change_colour(pt=[200, 201], new_colour=BLACK)
        >>> len(board.liberty_lb(group_pt=200)) > 2
        True
        """
        for crawl_pt in self._board_crawl(start_pt=group_pt):
            if len(self._find_liberties(node=group_pt)) > 2:
                break
            elif self.colour(crawl_pt) is OPEN:
                group_liberties = self._find_liberties(node=group_pt)
                group_liberties |= {crawl_pt}
            elif self.colour(group_pt) == self.colour(crawl_pt):
                self._union(group_pt, crawl_pt)

        return self._find_liberties(node=group_pt)


class BoardError(Exception):
    """"""
    pass