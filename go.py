import random
from collections import namedtuple, defaultdict
from copy import copy, deepcopy

import numpy as np

BLACK = 1
WHITE = -1
OPEN = 0


class Group:
    """
    A object to tracking colour, size and liberties

    >>> Group(colour=BLACK, stones={60}, liberties={61})
    BLACK Group size=1 libs=1
    """
    def __init__(self, colour, stones, liberties=None):
        """Initialize a Group

        :param colour: +1/-1
        :param stones: iter
        :param liberties: iter
        :return: None
        """
        self.colour = colour
        self._stones = set(stones)

        if liberties is None:
            self._liberties = set()
        else:
            self._liberties = set(liberties)

    def __eq__(self, other):
        """
        Group are equal if they have the same colour and positions

        :param other:
        :return:
        """
        return (self.colour == other.colour
                and self._stones == other._stones)

    @property
    def size(self):
        """:return: int for how big the group is"""
        return len(self._stones)

    @property
    def liberties(self):
        """:return: number of _liberties
        """
        return len(self._liberties)

    def add_lib(self, pt):
        """Add pt as a liberty of self

        :param pt: int
        """
        self._liberties |= {pt}

    def remove_lib(self, pt):
        """Remove pt as a liberty of self

        :param pt: int
        """
        self._liberties -= {pt}

    def combine(self, other):
        """
        Combine other into self

        Logically this occurs when it is discovered that the two groups are beside each
        other on a game board, though that is constraint is not enforced by this method.
        Be cautious when combining groups, as they can be combined by this method even
        when they are not adjacent.

        :param other: Group
        """
        if self.colour != other.colour:
            raise GroupError('Cannot combine different player groups')

        self._stones |= other._stones
        self._liberties |= other._liberties

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

        return name() + ' Group size={0} libs={1}'.format(len(self._stones), self.liberties)


class GroupError(Exception):
    """Errors occuring due to the misfunctioning of Group objects"""
    pass


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

        Board uses a union find data structure using _pointers in a dictionary
        :param size: int
        >>> b = Board()
        """
        self.neighbors, self.diagonals = NEIGHBORS[size], DIAGONALS[size]
        self.size = size
        self._pointers = [None for _ in range(size ** 2)]
        self._board_colour = [OPEN for _ in range(size ** 2)]

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
            if self._board_colour[pt] == BLACK:
                repre += BLACKstr
            elif self._board_colour[pt] == WHITE:
                repre += WHITEstr
            elif self._board_colour[pt] == OPEN:
                repre += OPENstr

            if (pt + 1) % self.size == 0:
                repre += '\n'
        return repre

    def __getitem__(self, item):
        """Return the group object pointed at by item

        :param item: int or Group
        :return: Group
        >>> Board()[200] is None
        True
        """
        return self._pointers[item]

    def __deepcopy__(self, memo):
        """Return a mid depth copy of self

        Not all the mutable properties change, so multiple Board objects can point to the
        same sub-object without conflict.
        :return: Board
        """
        board = copy(self)
        board._pointers = deepcopy(self._pointers)
        board._board_colour = copy(self._board_colour)

        return board

    def colour(self, pt):
        """Find the colour of the board at pt

        :param pt: int
        :return: BLACK, WHITE, OPEN
        >>> Board().colour(200) == OPEN
        True
        """
        return self._board_colour[pt]

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
                self._pointers[pt] = None
                self._board_colour[pt] = OPEN
            else:
                self._pointers[pt] = Group(colour=new_colour,
                                           stones={pt}, )
                self._board_colour[pt] = new_colour

                for neigh_pt in self.neighbors[pt]:     # remove pt as a liberty
                    neigh_group, _ = self._find(neigh_pt)
                    try:
                        neigh_group.remove_lib(pt)
                    except AttributeError:
                        pass    # group is None

    def _find(self, pt):
        """Follow _pointers to Group

        Updates the _pointers also to make future searches require fewer loops
        :param pt: int
        :return: Group, int
        """
        pointer = pt
        target = self._pointers[pointer]
        while True:
            try:
                pointer, target = target, self._pointers[target]
            except TypeError:
                break
            else:
                self._pointers[pt] = pointer
        return target, pointer

    def _union(self, f_pt, s_pt):
        """Union two groups into one

        Union is performed favouring the group with the most _stones.
        :param f_pt: int
        :param s_pt: int
        :return: Group
        """
        if self._board_colour[f_pt] is OPEN or self._board_colour[s_pt] is OPEN:
            raise BoardError('Cannot union with an open point')
        elif self._board_colour[f_pt] != self._board_colour[s_pt]:
            raise GroupError('Cannot union with different colours')

        (f_group, f_at), (s_group, s_at) = self._find(f_pt), self._find(s_pt)
        if f_group is s_group:
            return f_group
        elif f_group.size >= s_group.size:
            f_group.combine(s_group)
            self._pointers[s_at] = f_at
            return f_group
        else:
            s_group.combine(f_group)
            self._pointers[f_at] = s_at
            return s_group

    def _board_crawl(self, start_pt):
        """Generator of the points and neighbors of a single colour area

        There is no guaranteed order of the points.
        :param start_pt: int
        :yield: int
        """
        crawl_colour = self._board_colour[start_pt]
        to_search = {start_pt}
        searched = set()
        while to_search:
            search_pt = to_search.pop()
            yield search_pt     # yield start_pt coloured _stones
            searched |= {search_pt}
            for neigh_pt in self.neighbors[search_pt]:
                if (self._board_colour[neigh_pt] != crawl_colour):
                    yield neigh_pt
                    searched |= {neigh_pt}
                elif (neigh_pt not in searched):
                    to_search |= {neigh_pt}

    def discover_liberties(self, group_pt, limit=3):
        """Discover more _liberties of the group at group_pt

        If limit is finite, then the search is terminated when a certain number of
        _liberties have been found. Most liberty questions only require distinguishing
        1, 2, or more _liberties.
        :param group_pt: int
        :limit: float
        :return: int
        >>> board = Board()
        >>> board.change_colour(pt=[20, 21], new_colour=BLACK)
        >>> board.discover_liberties(group_pt=20, limit=8)
        6
        """
        if self._board_colour[group_pt] is OPEN:
            raise BoardError("Open point does not have liberties")

        for crawl_pt in self._board_crawl(start_pt=group_pt):
            try:
                group = self._union(group_pt, crawl_pt)
            except BoardError:  # occurs when unioning with an open point
                group.add_lib(crawl_pt)
            except GroupError:  # occurs when combining different colours
                pass
            if group.liberties >= limit:
                break

        return group.liberties

    def remove_group(self, dead_pt=None):
        """Remove a group and return the captured stone locations

        :param dead_pt: int
        :return: set
        >>> board = Board()
        >>> board.change_colour(pt=200, new_colour=BLACK)
        >>> board.remove_group(dead_pt=200)
        {200}
        """
        try:
            dead_points = iter(dead_pt)
        except TypeError:
            dead_points = [dead_pt]
        groups_to_remove = set(self._find(pt=pt)[1] for pt in dead_points)
        groups_to_remove = [self._pointers[pt] for pt in groups_to_remove]
        captured = set()
        for dead_group in groups_to_remove:
            captured |= set(dead_group._stones)
            self.change_colour(pt=dead_group._stones, new_colour=OPEN)
        return captured

    def discover_all_libs(self):
        """Run full liberty search on every pt on board

        This will ensure every point only points at the actual group object it is apart of
        >>> board = Board()
        >>> board.change_colour(pt=[20, 21, 23], new_colour=BLACK)
        >>> board.discover_all_libs()
        >>> board._find(pt=20)[0].liberties
        6
        >>> board._find(pt=23)[0].liberties
        4
        """
        for pt in self:
            try:
                self.discover_liberties(group_pt=pt, limit=np.infty)
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
        stones = sum(self.board._board_colour)

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

    def _move_coroutine(self, move_pt, colour=None):
        """A coroutine splitting of the move function into check and updates

        The expense of move is quite large, and a substantial part of that is the checks
        required for legal play.
        There are also application for when we need a legal move, but we do not want
        to complete it.
        The move coroutine allows the check to be performed, and MoveErrors
        to be raised without completing the move itself.
        An example of how to use this coroutine is the self.move function.

        :param move_pt: int
        :param colour: +1/-1
        :raise: MoveError
        :raise: StopIteration
        :return: coroutine generator
        """

        def friendly_eye(pt, colour):
            """Check whether pt is as friendly eye"""
            nonlocal neigh_points

            if -colour not in neigh_points and OPEN not in neigh_points:
                opp_count = 0
                diags = self.board.diagonals[pt]
                for diag_pt in diags:
                    if self.board._board_colour[diag_pt] == -colour:
                        opp_count += 1
                if EyeCorners(opp_count, corner_count=len(diags)) in IS_AN_EYE:
                    return True
            return False

        def self_capture(move_pt, colour):
            """Reducing your own _liberties to zero is an illegal move"""
            nonlocal neigh_points
            nonlocal neigh_dead

            open_neighbor = (OPEN in neigh_points)

            enemy_points = neigh_points[-colour]
            for enemy_pt in enemy_points:
                liberties = self.board.discover_liberties(group_pt=enemy_pt, limit=2)
                if liberties == 1:
                    neigh_dead[-colour] |= {enemy_pt}
            capturing_move = (len(neigh_dead[-colour]) > 0)

            if open_neighbor or capturing_move: # first exit
                return False

            alive_neighbor = False
            friendly_points = neigh_points[colour]
            for friendly_pt in friendly_points:
                liberties = self.board.discover_liberties(group_pt=friendly_pt, limit=2)
                alive_neighbor = (liberties > 1) or alive_neighbor

            if alive_neighbor: # final exit
                return False
            else:
                return True

        if colour is None:
            colour = self.next_player
        elif colour not in [BLACK, WHITE]:
            raise MoveError('Unrecognized move colour: ' + str(colour))

        if move_pt == self.kolock:
            raise MoveError(str(move_pt) + ' is a ko locked point')
        elif self.board._board_colour[move_pt] is not OPEN:
            raise MoveError('Playing on another stone')

        neigh_points = defaultdict(set)
        for neigh_pt in self.board.neighbors[move_pt]:
            neigh_colour = self.board._board_colour[neigh_pt]
            neigh_points[neigh_colour] |= {neigh_pt}

        if friendly_eye(move_pt, colour):
            raise MoveError(str(move_pt) + ' is a play in a friendly eye')

        neigh_dead = defaultdict(set)

        if self_capture(move_pt, colour):
            raise MoveError(str(move_pt) + ' is self capture')

        yield   # may never return here, and that's fine

        self.board.change_colour(pt=move_pt, new_colour=colour)
        captured = self.board.remove_group(dead_pt=neigh_dead[-colour])
        self.actions |= captured
        self.actions -= {move_pt}

        self.kolock = captured.pop() if len(captured) == 1 else None # single stone caught

        self.next_player = -colour
        self.lastmove = move_pt

    def move(self, move_pt, colour=None):
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
        BLACK Group size=1 libs=0
        """
        if colour is None:
            colour = self.next_player

        move_routine = self._move_coroutine(move_pt=move_pt, colour=colour)
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

    def random_move(self, tried=None):
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
            sample_list = random.sample(self.actions - tried, k=1)

            move_pt = sample_list[0]
            try:
                self.move(move_pt)
            except MoveError:
                tried |= {move_pt}
            else:
                return move_pt
        raise MoveError('No moves to take')

    def random_playout(self):
        """Return score after playing to a terminal position randomly

        :return: float
        >>> type(Position(size=9).random_playout()[0])
        <class 'go.Position'>
        """
        position = deepcopy(self)
        passes = 0
        moves = {BLACK:set(), WHITE:set()}
        while passes < 2:
            try:
                colour = position.next_player
                moves[colour] |= {position.random_move()}
            except MoveError:
                position.pass_move()
                passes +=1
            else:
                passes = 0
        for colour in moves:
            moves[colour] &= self.actions

        return position, moves


class MoveError(Exception):
    """The exception throw when an illegal move is made.

    ie repeat play, suicide or on a ko
    """
    pass
