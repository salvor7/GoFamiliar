from collections import deque, Counter
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


EyeCorners = namedtuple('EyeCorners', 'opp_count corner_count')
IS_AN_EYE = {EyeCorners(opp_count=0, corner_count=1),
             EyeCorners(opp_count=0, corner_count=2),
             EyeCorners(opp_count=0, corner_count=4),
             EyeCorners(opp_count=1, corner_count=4),
             }


class Group(namedtuple('Group','colour stones liberties')):
    """Union Find algorithm for Go board stone groups
    >>> Group(colour=1, stones=(123,124), liberties=frozenset({102, 103}))
    Group(colour=1, size=2, liberties=2)
    """
    @property
    def lib_count(self):
        """:return: number of group liberties
        >>> Group(colour=1, stones=(123,124), liberties=frozenset({102, 103})).lib_count
        2
        """
        return len(self.liberties)

    @property
    def size(self):
        """:return: number of stones in group
        >>> Group(colour=1, stones=(123,124), liberties=frozenset({102, 103})).size
        2
        """
        return len(self.stones)

    def __repr__(self):
        """:return: representation of Group object
        """
        return 'Group(colour={0}, size={1}, liberties={2})'.format(self.colour, self.size, self.lib_count)


OPEN_POINT = Group(colour=OPEN, stones=tuple(), liberties=frozenset(), )


class GroupUnionFind():
    """Manage, union and find all the Groups

    "node"s are either a Group or an int representation of a board position.
    """
    def __init__(self, size=19):
        """Initialize a union find structure for Groups

        >>> type(GroupUnionFind())
        <class 'godata.GroupUnionFind'>
        """
        self._pointers = {idx:OPEN_POINT for idx in range(size**2)}
        self._boxes = BOXES[size]
        self._neighbors = NEIGHBORS[size]

    def __getitem__(self, elem):
        """:return: Immediate parent Group of elem

        >>> GroupUnionFind()[100]
        Group(colour=0, size=0, liberties=0)
        """
        try:
            return self._pointers[elem]
        except KeyError:
            if type(elem) is int:
                return OPEN_POINT
            else:
                raise

    def __setitem__(self, elem, group):
        """Set group as parent of elem

        :param elem: int or Group
        :param group: Group
        >>> GroupUnionFind()[200] = Group(*(1,[1,2],[4,5],))
        """
        if type(group) is not Group:
            raise TypeError('Value is not a Group')
        self._pointers[elem] = group

    def colour(self, pt):
        """:return: colour of intersection

        >>> guf = GroupUnionFind()
        >>> guf[60] = Group(colour=BLACK, stones=(1,), liberties={61})
        >>> guf.colour(pt=60) is BLACK
        True
        >>> guf.colour(pt=61) is OPEN
        True
        """
        try:
            return self[pt].colour
        except KeyError:
            if type(pt) is int:
                return OPEN
            else:
                raise

    def find(self, node):
        """:return: root parent Group

        This implements the find part of the unionfind algorithm.
        >>> guf = GroupUnionFind()
        >>> guf[200] = Group(*(1, (1,2), frozenset((4,5)),))
        >>> guf[guf[200]] = Group(*(1, (1,2,3), frozenset((4,5,6))))
        >>> guf[200], guf.find(200)
        (Group(colour=1, size=2, liberties=2), Group(colour=1, size=3, liberties=3))
        """
        try:
            parent = self[node]
        except KeyError:
            return node

        while True:
            try:
                parent = self[parent]
            except KeyError:
                break
        self[node] = parent    # point node at parent
        return parent

    def add_lib(self, node, lib):
        """Return group with lib added

        :param node: int or Group
        :param lib: int
        """
        group = self.find(node)

        if lib not in group.liberties:
            colour, size, liberties = group
            new_group = Group(colour=colour, size=size, liberties=liberties|{lib})
            self[group] = new_group

    def _yield_new_stone(self, pt, colour):
        """Yield a new group representing a newly played stone

        Created as a coroutine so the Group can be created and used in calculations, but
        the the pointers will only be updated if the stone can be played.

        Takes in liberties until a non-int is passed, and then the Group is yieled.
        :param pt: int
        :param colour: +/-1
        int :yield: 1 None
                    2 new Group
        """
        if self[pt].colour is not 0:
            raise MoveError('Playing on another stone.')
        libs = set()
        while True:
            new_lib = yield
            try:
                libs |= {int(new_lib)}
            except (ValueError, TypeError):
                break
        yield   # forces a next to be called before yielding the group
        new_stone = Group(colour=colour, stones=(pt,), liberties=frozenset(libs))
        yield new_stone
        self[pt] = new_stone

    def _yield_remove_lib(self, node, lost_lib):
        """Yield a new Group, then update self

        Groups are immutable, so removing a lib requires creating a new Group object, and
        adding that new object into the pointers.
        The liberty count is generally needed before knowing if the pointers will
        change, so this is implemented as coroutine which yields the prospective group
        first, then on next() updated the pointers.
        :param node: Group or int
        :yield: 1 root Group
                2 new Group
                3 StopIteration
        """
        group = self.find(node=node)
        yield group
        colour, stones, liberties = group
        new_group = Group(colour=colour, stones=stones, liberties=liberties-{lost_lib})
        yield new_group
        self[group] = new_group

    def _yield_union(self, *args):
        """Yield the group, then complete the union

        A coroutine used to break up the computation of forming a combined group, and
        updating the union pointers.
        The properties of the combined group need to be tested before knowing the pointers will
        be updated.
        :param args: nodes
        :yield: Group
        """
        if len(args) > 1:
            root_groups = [self.find(node) for node in args]
            group_colours = Counter(group.colour for group in root_groups)
            if len(group_colours) is not 1:
                raise ValueError("Can't union different coloured groups")

            colour=next(iter(group_colours))
            stones=sum([group.stones for group in root_groups], ())
            liberties=frozenset.union(*[group.liberties for group in root_groups]) - set(stones)
            parent_group = Group(colour=colour, stones=stones, liberties=liberties,)

            yield parent_group

            for group in root_groups:
                self[group] = parent_group
        else:
            raise ValueError('Expected at least two arguments')

    def union(self, *args):
        """Union two groups together

        :param args: nodes
        :return: GroupUnionFind
        >>> guf = GroupUnionFind()
        >>> guf[1] = Group(*(1, (1,2), frozenset((0, 20,21)),))
        >>> guf[3] = Group(*(1, (3,22), frozenset((4,21,23,41))))
        >>> guf.union(1,3)
        >>> guf.find(1)
        Group(colour=1, size=4, liberties=6)
        """
        gen = self._yield_union(*args)

        next(gen)   # create group
        try:
            next(gen)   # complete update of UnionFind structure
        except StopIteration:
            pass

    def add_stone(self, stone_pt, colour):
        """Add a stone to a go board according to the rules

        :raise: ValueError
                MoveError
        """
        def find_local_group_gens():
            """fills up the local group generators dictionary

            :nonlocal param: self
            :nonlocal param: colour
            :nonlocal param: local_geners
            :raises: MoveError
            """
            def friendly_eye_check():
                """don't play in your own eyes

                :raises: MoveError
                """
                local_geners[colour] |= set()
                if OPEN not in local_geners and -colour not in local_geners: # all four same colour as stone_pt
                    opp_count = 0
                    for diag_pt in diagonals:
                        if self[diag_pt].colour == -colour:
                            opp_count += 1
                    if EyeCorners(opp_count, corner_count=len(diagonals)) in IS_AN_EYE:
                        raise MoveError('Playing in a friendly eye')

            new_stone_gen = self._yield_new_stone(pt=stone_pt, colour=colour)
            next(new_stone_gen) # prime the coroutine

            neighbors, diagonals = self._boxes[stone_pt]
            for neigh_pt in neighbors:
                if self[neigh_pt].colour is OPEN:
                    new_stone_gen.send(neigh_pt)
                    local_geners[OPEN] = OPEN   # mark open point around stone_pt
                else:
                    group_gen = self._yield_remove_lib(node=neigh_pt, lost_lib=stone_pt)
                    root_group = next(group_gen)
                    if root_group not in local_geners:  # no repeat groups
                        local_geners[root_group] &= {root_group}
                        local_geners[self[neigh_pt].colour] |= {group_gen}

            friendly_eye_check()

            new_stone_gen.send(None)
            local_geners[colour] |= {new_stone_gen}

        def capture_stones(dead_group):
            """Remove captures and update surroundings

            :nonlocal param: self
            :nonlocal param: colour
            """
            dead_group = dead_group.find()
            for dead_stone in dead_group.stones():
                self[dead_stone] = OPEN_POINT

                for neigh_pt in self._neighbors[dead_stone]:
                    if self.colour(neigh_pt) is -colour:
                        self.add_lib(node=neigh_pt, lib=dead_stone)

        def no_self_capture():
            """Reducing your own liberties to zero is an illegal move

            :nonlocal param: self
            :nonlocal param: colour
            :nonlocal param: local_geners
            :raises: MoveError
            """
            captured = ()
            for opp_group_gen in local_geners[-colour]:
                opp_group = next(opp_group_gen)
                if opp_group.lib_count == 0:
                    captured += opp_group.stones
                    capture_stones(dead_group=opp_group)
            else:
                if len(captured) == 1:
                    kolock_pt = opp_group.stones[0]
                else:
                    kolock_pt = None

            new_groups = [next(group_gen) for group_gen in local_geners[colour]]
            comb_group_gen = self._yield_union(*new_groups)
            try:
                comb_group = next(comb_group_gen)
            except ValueError:
                comb_group = new_groups[0]  # one stone
            else:
                local_geners[colour] |= {comb_group_gen}

            if len(captured) == 0 and comb_group.lib_count == 0:
                raise MoveError('Playing self capture_stones')

            return kolock_pt, captured

        def update_friendly_groups():
            """Update and/or remove opponent groups

            :nonlocal param: colour
            :nonlocal param: local_geners
            """
            for group_gen in local_geners[colour]:
                try:
                    next(group_gen)
                except StopIteration:
                    pass
                else:
                    raise RuntimeError('Group coroutines should end here')

        #---------Main steps----------
        if colour not in [BLACK, WHITE]:
            raise ValueError('Unrecognized move colour: ' + str(colour))
        local_geners = defaultdict(set)
        find_local_group_gens()
        kolock_pt, captured = no_self_capture()
        update_friendly_groups()

        return kolock_pt, captured


class Position():
    """A Go game position object

    An object to track all the aspects of a go game. It uses a "thick" representation of
    the board to store group information.
    >>> Position().size
    19
    >>> Position(size=13).size
    13
    """
    def __init__(self, *, moves=None, size=19, komi=7.5, lastmove=None, kolock=None):
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
        self.board = GroupUnionFind(size=size)

        try:
            for pt in moves:
                self.move(pt)
        except TypeError:
            pass

    def pass_move(self):
        """Execute a passing move

        >>> Position().pass_move()
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
                black_liberties |= group.lib_count
            else:
                white_stones += group.size
                white_liberties |= group.lib_count
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
        >>> pos.board[move_pt]
        Group(colour=1, size=1, liberties=4)
        >>> pos.move(move_pt+1, colour=BLACK)
        >>> pos.board.find(move_pt+1)
        Group(colour=1, size=2, liberties=6)
        """
        kolock_pt, captured = self.board.add_stone(stone_pt=move_pt, colour=colour)
        self.kolock = kolock_pt
        self.actions |= {captured}
        self.actions -= {move_pt}
        self.next_player = -colour
        self.lastmove = move_pt


class MoveError(Exception):
    """The exception throw when an illegal move is made.

    ie repeat play, suicide or on a ko
    """
    pass
#
#
# class TerminalPosition(StopIteration):
#     """Exception raised when a position is terminal and a move is attempted.
#     """
#     pass