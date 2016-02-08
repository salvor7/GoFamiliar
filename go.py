import random
from collections import namedtuple, defaultdict
from copy import copy, deepcopy

import numpy as np

BLACK = 1
WHITE = -1
OPEN = 0


class Group(namedtuple('Group','colour stones')):
    """An object to carry the immutable elements of a group
    """
    @property
    def size(self):
        """:return: int for how big the group is"""
        return len(self.stones)

    def __repr__(self):
        """Group representation

        :return: str
        """
        def name():
            if self.colour == BLACK:
                return 'BLACK'
            elif self.colour == WHITE:
                return 'WHITE'
            else:
                return str(self.colour)

        if self == OPEN_POINT:
            return 'OPEN POINT'
        else:
            return '(' + name() + ' Group, size {0}, at {1})'.format(len(self.stones), self.stones)


OPEN_POINT = Group(colour=OPEN, stones=frozenset())


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


DIAGONALS = {n: {pt: diag for pt, neigh, diag in make_boxes(size=n)} for n in range(9, 26, 2)}


EyeCorners = namedtuple('EyeCorners', 'opp_count corner_count')
IS_AN_EYE = {EyeCorners(opp_count=0, corner_count=1),
             EyeCorners(opp_count=0, corner_count=2),
             EyeCorners(opp_count=0, corner_count=4),
             EyeCorners(opp_count=1, corner_count=4),
             }


class Board():
    """A data structure for tracking and querying go data

    "node"s mentioned below are either a Group object or an int representation of a
    board position.
    """

    def __init__(self, size=19):
        """Initialize a Board object

        Board uses a union find data structure using pointers in a dictionary
        :param size: int
        >>> b = Board()
        """
        self.neighbors, self.diagonals = NEIGHBORS[size], DIAGONALS[size]
        self._liberties = defaultdict(set)
        self.size = size
        self._pointers = {idx:OPEN_POINT for idx in range(size ** 2)}

    def __iter__(self):
        """Iterator over the size**2 board points

        :return: iter
        """
        return iter(range(self.size ** 2))

    def __repr__(self):
        """String representation of a Board

        :return: str
        >>> print(repr(Board(size=9)))
        ---------
        ---------
        ---------
        ---------
        ---------
        ---------
        ---------
        ---------
        ---------
        <BLANKLINE>
        """
        BLACKstr = 'X'
        WHITEstr = 'o'
        OPENstr = '-'

        repre = ''
        for pt in self:
            if self._pointers[pt].colour == BLACK:
                repre += BLACKstr
            elif self._pointers[pt].colour == WHITE:
                repre += WHITEstr
            elif self._pointers[pt].colour == OPEN:
                repre += OPENstr

            if (pt + 1) % self.size == 0:
                repre += '\n'
        return repre

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
        >>> board[200] = Group(colour=BLACK, stones=frozenset({200}))
        >>> board[200].colour == BLACK
        True
        """
        if type(value) is Group:
            self._pointers[key] = value
        else:
            raise BoardError('Expected Group. Got ' + str(type(value)))

    def __delitem__(self, key):
        """Delete an item from pointers using a special method

        :param key: node
        """
        del self._pointers[key]

    def __deepcopy__(self, memo):
        """Return a mid depth copy of self

        Not all the mutable properties change, so multiple Board objects can point to the
        same sub-object without conflict.
        :return: Board
        """
        board = copy(self)
        board._liberties = deepcopy(self._liberties)
        board._pointers = copy(self._pointers)

        return board

    def colour(self, pt):
        """Find the colour of the board at pt

        :param pt: int
        :return: BLACK, WHITE, OPEN
        >>> Board().colour(200) == OPEN
        True
        """
        return self._pointers[pt].colour

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
        if new_colour not in [BLACK, WHITE, OPEN]:
            raise BoardError('Unrecognized colour')

        try:
            points = iter(pt)
        except TypeError:
            points = [pt]

        for pt in points:
            if new_colour is OPEN:
                self._pointers[pt] = OPEN_POINT
            elif self._pointers[pt].colour != new_colour:

                self._pointers[pt] = Group(colour=new_colour, stones=frozenset({pt}))
                try:
                    del self._pointers[self._pointers[pt]]      # ensure no old trees are revived
                except KeyError:
                    pass

                for neigh_pt in self.neighbors[pt]:     # remove pt as a liberty
                    neigh_group = self._find(neigh_pt)
                    self._liberties[neigh_group] -= {pt}

    def _find(self, node):
        """Follow pointers to top Group

        Updates the pointers also to make future searches require fewer loops
        :param node: int or Group
        :return: Group
        """
        parent = node
        while True:
            try:
                parent = self._pointers[parent]
            except KeyError:
                break
        self._pointers[node] = parent # shrink union-find pointer tree
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
        if f_group == s_group:
            raise BoardError('Cannot union same group')
        elif f_group.colour != s_group.colour:
            raise BoardError('Cannot union different colour stones')
        elif f_group is OPEN_POINT:
            raise BoardError('Cannot union with OPEN POINT')

        union_group = Group(colour=f_group.colour, stones=f_group.stones | s_group.stones)
        try:
            del self._pointers[union_group]       # ensure no old trees are revived
        except KeyError:
            pass
        self._pointers[s_group] = union_group
        self._pointers[f_group] = union_group
        self._liberties[union_group] |= (self._liberties[f_group] | self._liberties[s_group])
        for group in [f_group, s_group]:
            try:
                del self._liberties[group]
            except KeyError:
                pass
        return union_group

    def _board_crawl(self, start_pt):
        """Generator of the points and neighbors of a single colour area

        There is no guaranteed order of the points.
        :param start_pt: int
        :yield: int
        """
        crawl_colour = self._pointers[start_pt].colour
        to_search = {start_pt}
        searched = set()
        while to_search:
            search_pt = to_search.pop()
            yield search_pt     # yield start_pt coloured stones
            searched |= {search_pt}
            for neigh_pt in self.neighbors[search_pt]:
                if (self._pointers[neigh_pt].colour != crawl_colour):
                    yield neigh_pt
                    searched |= {neigh_pt}
                elif (neigh_pt not in searched):
                    to_search |= {neigh_pt}

    def group_liberties(self, group_pt, limit=3):
        """Return liberties of the group at group_pt

        If limit is finite, then the search is terminated when a certain number of
        liberties have been found. Most liberty questions only require knowning if there
        are 1, 2, or more liberties.
        :param group_pt: int
        :limit: float
        :return: int
        >>> board = Board()
        >>> board.change_colour(pt=[20, 21], new_colour=BLACK)
        >>> len(board.group_liberties(group_pt=20, limit=8))
        6
        """
        group = self._find(node=group_pt)
        if group == OPEN_POINT:
            raise BoardError('Open point does not have liberties')

        for crawl_pt in self._board_crawl(start_pt=group_pt):
            if len(self._liberties[group]) >= limit:
                break
            elif self._pointers[crawl_pt].colour is OPEN:
                self._liberties[group] |= {crawl_pt}
            try:
                group = self._union(group_pt, crawl_pt)
            except BoardError:
                pass

        return self._liberties[group]

    def remove_group(self, dead_node=None):
        """Remove a group and return the captured stone locations

        :param dead_pt: int
        :return: set
        >>> board = Board()
        >>> board.change_colour(pt=200, new_colour=BLACK)
        >>> board.remove_group(dead_node=200)
        {200}
        """
        try:
            dead_nodes = iter(dead_node)
        except TypeError:
            dead_nodes = [dead_node]
        groups_to_remove = set(self._find(node=node) for node in dead_nodes)
        captured = set()
        for dead_group in groups_to_remove:
            try:
                del self._liberties[dead_group]     # no liberties explored yet
            except KeyError:
                pass
            captured |= set(dead_group.stones)
            self.change_colour(pt=dead_group.stones, new_colour=OPEN)
        return captured

    def collapse_uftree(self):
        """Run full liberty search and find on every pt on board

        This will ensure every point only points at the actual group object it is apart of
        """
        for pt in self:
            try:
                self.group_liberties(group_pt=pt, limit=np.infty)
            except BoardError:
                pass
            self._find(pt)


class BoardError(Exception):
    """Error raised by Board objects when a query or transaction cannot be completed"""
    pass


class Position():
    """A Go game position object

    An object to track all the aspects of a go game. It uses a "thick" representation of
    the board to store group information.
    >>> Position().size
    19
    >>> Position(size=13).size
    13
    """
    def __init__(self, *, moves=None, size=19, komi=-7.5, lastmove=None, kolock=None):
        """Initialize a Position with a board of size**2

        :param size: int
        >>> pos = Position()
        """
        self.kolock = kolock
        self.komi = komi
        self.size = size
        self.lastmove = lastmove
        self.next_player = BLACK
        self.actions = set(range(size ** 2))
        self.board = Board(size=size)

        try:
            for pt in moves:
                self.move(pt)
        except TypeError:
            pass

    def score(self):
        """Return the score of the position

        Scored for black being positive.
        :return: float
        >>> Position().score() == -7.5
        True
        """
        stones = sum([self.board.colour(pt) for pt in self.board])
        eyes = 0

        for pt in self.actions:
            neigh_col = set(self.board.colour(neigh_pt) for neigh_pt in self.board.neighbors[pt])
            eyes += sum(neigh_col)
        return stones + eyes + self.komi

    def winner(self):
        """Return the winner of self

        :return: +/-1
        """
        score = self.score()
        return int(score/abs(score))

    def _move_coroutine(self, move_pt, colour=None, playback=True):
        """A coroutine splitting of the move function into check and updates

        The expense of move is quite large, and a substantial part of that is the checks
        required for legal play.
        There are also application for when we need a legal move, but we do not want
        to complete it.
        The move coroutine allows the check to be performed, and MoveErrors
        to be raised without completing the move itself.
        An example of how to use this coroutine is the self.move function.

        Playback refers to playing back into spots stones have been captured from. In
        general, this is desirable as it is in the rules, but it is rarely useful. And in
        playout, allowing play back extends the playout well past a normal length game, so
        disallowing it in random playout will reduce the time spent.
        :param move_pt: int
        :param colour: +1/-1
        :param playback: boolean
        :raise: MoveError
        :raise: StopIteration
        :return: coroutine generator
        """

        def friendly_eye(pt, colour):
            """Check whether pt is as friendly eye"""
            neigh_colours = set(self.board.colour(neigh_pt)
                                for neigh_pt in self.board.neighbors[move_pt])
            if {colour} == neigh_colours:
                opp_count = 0
                diags = self.board.diagonals[pt]
                for diag_pt in diags:
                    if self.board[diag_pt].colour == -colour:
                        opp_count += 1
                if EyeCorners(opp_count, corner_count=len(diags)) in IS_AN_EYE:
                    return True
            return False

        def self_capture(pt, colour):
            """Reducing your own liberties to zero is an illegal move"""
            nonlocal neigh_dead

            pt_is_self_capture = True
            neigh_alive = defaultdict(set)
            for neigh_pt in self.board.neighbors[move_pt]:  #check neighbor groups
                try:
                    liberties = self.board.group_liberties(group_pt=neigh_pt, limit=2)
                except BoardError:      # when neigh_pt is OPEN
                    pt_is_self_capture = False
                    continue

                neigh_col = self.board.colour(neigh_pt)
                if liberties == {move_pt}:
                    neigh_dead[neigh_col] |= {neigh_pt}
                else:
                    neigh_alive[neigh_col] |= {neigh_pt}

            if pt_is_self_capture and (colour not in neigh_alive) and (-colour not in neigh_dead):
                return True
            else:
                return False

        if colour is None:
            colour = self.next_player
        elif colour not in [BLACK, WHITE]:
            raise MoveError('Unrecognized move colour: ' + str(colour))

        if move_pt == self.kolock:
            raise MoveError('Playing in a ko locked point')
        elif self.board.colour(pt=move_pt) is not OPEN:
            raise MoveError('Playing on another stone')
        elif playback and friendly_eye(move_pt, colour):
            raise MoveError('Playing in a friendly eye')

        neigh_dead = defaultdict(set)

        if self_capture(move_pt, colour):
            raise MoveError('Playing self capture')

        yield   # may never return, and that's fine

        self.board.change_colour(pt=move_pt, new_colour=colour)
        captured = self.board.remove_group(dead_node=neigh_dead[-colour])
        if playback:
            self.actions |= captured
        self.actions -= {move_pt}

        self.kolock = captured.pop() if len(captured) == 1 else None # single stone caught

        self.next_player = -colour
        self.lastmove = move_pt

    def move(self, move_pt, colour=None, playback=True):
        """Play a move on a go board

        :param pt: int
        :param colour: +1 or -1
        :raise: MoveError

        Completes all the checks to a ensure legal move, raising a MoveError if illegal.
        Adds the move to the position, and returns the position.
        >>> move_pt = 200
        >>> pos = Position()
        >>> pos.move(move_pt, colour=BLACK)
        >>> pos.board[move_pt]
        (BLACK Group, size 1, at frozenset({200}))
        """
        if colour is None:
            colour = self.next_player

        move_routine = self._move_coroutine(move_pt=move_pt, colour=colour, playback=playback)
        next(move_routine)      # prime the coroutine ie execute to first yield
        try:
            next(move_routine)      # complete the coroutine
        except StopIteration:
            pass
        else:
            raise MoveError('Move coroutine did not end when expected')

    def pass_move(self):
        """Execute a passing move

        >>> Position().pass_move()
        """
        self.next_player *= -1
        self.kolock = None
        self.lastmove = None

    def random_move(self, tried=None, playback=True):
        """Play one random move

        Legal move choosen uniformly at random and taken if possible
        :param tried: iter of move coordinates
        >>> move = Position().random_move()
        """
        if tried is None:
            tried = set()
        else:
            tried = set(tried)
        while tried != self.actions:
            sample_list =  random.sample(self.actions - tried, k=1)
            move_pt = sample_list[0]
            try:
                self.move(move_pt, playback=playback)
            except MoveError:
                tried |= {move_pt}
            else:
                return move_pt
        raise MoveError('No moves to take')

    def random_playout(self, playback=True):
        """Return score after playing to a terminal position randomly

        :return: float
        >>> type(Position(size=9).random_playout()[0])
        <class 'go.Position'>
        """
        position = deepcopy(self)
        passes = 0
        moves = []
        while passes < 2:
            try:
                moves.append(position.random_move(playback=playback))
            except MoveError:
                position.pass_move()
                passes +=1
            else:
                passes = 0
        return position, moves


class MoveError(Exception):
    """The exception throw when an illegal move is made.

    ie repeat play, suicide or on a ko
    """
    pass
