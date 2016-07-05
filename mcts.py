"""
General Monte Carlo Tree Search algorithm

This module is a general implementation of an MCTS algorithm.
It is not intended to be specialized for go, though that is the first and only use anticipated.
It is based on the basic algorithm shown in "A Survey of Monte Carlo Tree Search Methods".
"""
from copy import deepcopy
from math import sqrt, log
from collections import Counter

from thick_goban import go
from util import tree


class NodeMCTS(tree.Node):
    """
    A node of MC search tree

    Two algorithm tuning parameters are defined at the class level.
    :CONFIDENCE_ALG: boolean
        Interpolates between usual confidence algorithm and AMAF.
        False means do not use confidence term.
        True means use it and do not use AMAF term, so the AMAF_LIMIT is ignored.
    :AMAF_LIMIT: int
        the number of MCTS simulations before the normal win rate term takes over for scoring.
    """
    CONFIDENCE_ALG = False
    AMAF_LIMIT = 20

    def __init__(self, state, name=None, children=None):
        """
        Initialize a MCTS node object
        """
        if name is None:
            self.name = state.lastmove
        else:
            self.name = name
        self.state = state
        self.wins = 0
        self.sims = 0
        self.amaf_rates = Counter()
        self.amaf_sims = Counter()
        super(NodeMCTS, self).__init__(children=children)
        self.children = {}

    def __repr__(self):
        """
        :return: A string representation of a node
        """
        return 'move: {2} n: {0} w: {1}'.format(self.sims, self.wins, self.name)

    @property
    def colour(self):
        """
        Return the two player colour of the move to be made from this node

        :return: int
        """
        return self.state.next_player

    def new_child(self, move_pt=None):
        """
        Add a new child node and play it out
        """
        new_state = deepcopy(self.state)
        if move_pt is None:
            new_state.random_move(tried=self.children.keys())
        else:
            new_state.move(move_pt=move_pt)

        child = NodeMCTS(state=new_state)
        child.parent = self
        self.children[child.name] = child

        child.random_sim()
        return child

    def random_sim(self):
        """
        Randomly simulate from the game state to a terminal state

        Updates the result up the tree.
        """
        def update_tree(moves, result):
            """
            MCTS update and All-Moves-As-First permutation style update

            Update node.amaf_rates total by sim win
                   node.amaf_sims total by 1
            for any node which can be reached by moves of the sam colour form the play out.

            Note: move_set is expected to exclude moves after the first game capture.
            Note: the colour relative scoring.

            :param move_set: {BLACK:iter, WHITE:iter}
            """
            def update_children(node, moves):
                """
                Update AMAF counters recursively
                """
                node.amaf_sims.update(moves[node.colour])
                amaf_winner = abs(result + node.colour)/2
                rate_update = {}
                for move in moves[node.colour]:
                    try:
                        r = node.amaf_rates[move]
                    except KeyError:
                        r = 0
                    rate_adj = (amaf_winner - r) / node.amaf_sims[move]
                    rate_update[move] = rate_adj
                node.amaf_rates.update(rate_update)
                for child in node.children.values():
                    update_children(node=child, moves=moves)

            nonlocal self
            self.sims += 1
            self.wins += abs(result - self.colour)/2
            root = self
            while root.parent is not None:
                root = root.parent
                root.sims += 1
                root.wins += abs(result - root.colour)/2

            update_children(node=root, moves=moves)

        terminal_state, moves = self.state.random_playout()
        result = terminal_state.winner()

        update_tree(moves=moves, result=result)

        return terminal_state

    def score(self):
        """
        Return a node's own score as formula below

        :return: float
        """
        w = self.wins
        n = self.sims
        N = self.parent.sims

        if self.CONFIDENCE_ALG:
            rate_balancer = 0
            explore_term = log(N) / sqrt(n)
        else:
            try:
                ar = self.parent.amaf_rates[self.name]
            except KeyError:
                ar = 0
            rate_balancer = max(0, ((self.AMAF_LIMIT + 1 - n) / (self.AMAF_LIMIT + 1)))
            explore_term = rate_balancer * ar

        win_rate_term = (1 - rate_balancer) * (w + 1) / (n + 1)

        return win_rate_term + explore_term

    def bestchild(self):
        """
        Find the child name with the highest score

        Formula is a mix of MCTS, AMAF, Permutation-AMAF and RAVE.
        The best AMAF child is created as a node if it is not already in the tree.

        :raises: go.MoveError
            Raised from self.new_child() calls
        :return: int
            Name of best child node
        """
        if not self.CONFIDENCE_ALG and self.AMAF_LIMIT > 0:
            scores = dict(self.amaf_rates)
        else:
            scores = {}
        for child in self.children.values():
            scores[child.name] = child.score()
        return max(scores, key=lambda x: scores[x])


def treepolicy(root):
    """Simulate a select node using MCTS with AMAF

    :param root: NodeMCTS
    """
    node = root

    while True:
        try:
            bestchildname = node.bestchild()
        except ValueError:  # no children nor AMAF totals
            node.new_child()
            break

        try:
            node = node.children[bestchildname]
        except KeyError:  # selected child is not a node yet
            pass
        else:
            continue

        try:
            node = node.new_child(move_pt=bestchildname)
        except go.MoveError:  # bad move from AMAF
            del node.amaf_rates[bestchildname]
            del node.amaf_sims[bestchildname]
        else:
            break


def move_search(state, sim_limit=1000):
    """Find a good move in a Go game

    This is the main function of the MCTS algorithm.
    All other module methods are used by it.
    sim_limit limits the total number of terminal playouts can occur before a move is returned/
    const is a constant value used in bestchild as part of move evaluation

    :param rootnode: root node with starting state
    :param sim_limit: int
    :return: action
    """
    rootnode = NodeMCTS(state=state)

    while rootnode.sims < sim_limit:
        try:
            treepolicy(rootnode)
        except go.MoveError:    # hit a terminal position
            rootnode.random_sim()   # run another simulation to mix up all the totals.

    return rootnode.bestchild()


def gof_move_search(queue, state, sim_limit=10000):
    """Pass search scores from the MCTS algorithm in to a queue

    This is the main function of the MCTS algorithm.
    All other module methods are used by it.
    sim_limit limits the total number of terminal playouts can occur before a move is returned/
    const is a constant value used in bestchild as part of move evaluation

    :param queue: multiprocessing.Queue object to allow algorithm state passing
    :param rootnode: root node with starting state
    :param sim_limit: int
    :return: action
    """
    rootnode = NodeMCTS(state=state)

    while rootnode.sims < sim_limit:
        try:
            treepolicy(rootnode)
        except go.MoveError:  # hit a terminal position
            rootnode.random_sim()  # run another simulation to mix up all the totals.

        if rootnode.sims % 10 == 0:
            child_scores = {child.name: child.score() for child in rootnode.children.values()}
            queue.put(child_scores)
