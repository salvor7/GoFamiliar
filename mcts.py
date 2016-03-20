"""
General Monte Carlo Tree Search algorithm

This module is a general implementation of an MCTS algorithm.
It is not intended to be specialized for go, though that is the first and only use anticipated.
It is based on the basic algorithm shown in "A Survey of Monte Carlo Tree Search Methods".
"""
from copy import deepcopy
from math import sqrt, log, exp

from collections import Counter

import go
from util import tree


class NodeMCTS(tree.Node):
    """
    A node of MC search tree
    """
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
        Return the two player colour

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

    def bestchild(self, conf_const=False, amaf_const=15):
        """
        Find the child name with the highest score

        Formula is a mix of MCTS, AMAF, Permutation-AMAF and RAVE.
        The best AMAF child is created as a node if it is not already in the tree.

        :param conf_const: boolean
            Interpolates between usual confidence algorithm and AMAF.
            0 means do not use confidence term; 1 means do not use AMAF term.
        :param amaf_const:
            the number of MCTS simulations required for even mixing between AMAF and MCTS
            terms.
        :raises: go.MoveError
            Raised from self.new_child() calls
        :return: int
            Name of best child node
        """
        def score(node):
            """
            Return the node score as formula below

            :return: float
            """
            w = node.wins
            n = node.sims
            N = node.parent.sims

            try:
                ar = node.parent.amaf_rates[node.name]
            except KeyError:
                ar = 0
            try:
                rate_balancer = (1 - conf_const) * (1/(1 + exp(n - amaf_const)))
            except OverflowError:
                rate_balancer = 0
            return ((1- rate_balancer) * (w / n)
                    + rate_balancer * (ar)
                    + conf_const * sqrt(log(N)/n)
                    )
        if amaf_const > 0:
            scores = dict(self.amaf_rates)
        else:
            scores = {}
        for child in self.children.values():
            scores[child.name] = score(child)
        return max(scores, key=lambda x: scores[x])


def search(state, sim_limit=100, const=0):
    """Find a good action

    This is the main function of the MCTS algorithm.
    All other module methods are used by it.
    sim_limit limits the total number of terminal playouts can occur before a move is returned/
    const is a constant value used in bestchild as part of move evaluation

    :param state: state object
    :param sim_limit: int
    :param const: float
    :return: action
    """
    def treepolicy(root):
        """Simulate a select node using MCTS with AMAF

        :param root: NodeMCTS
        :param const: float
        :return: NodeMCTS
        """
        node = root

        while True:
            try:
                bestchildname = node.bestchild()
            except ValueError:  # no children or AMAF totals
                node.new_child()

            try:
                node = node.children[bestchildname]
            except KeyError:    # selected child is not a node yet
                pass
            else:
                continue

            try:
                node = node.new_child(move_pt=bestchildname)
            except go.MoveError:   # bad move from AMAF
                del node.amaf_rates[bestchildname]
                del node.amaf_sims[bestchildname]

    root = NodeMCTS(state=state)

    while root.sims < sim_limit:
        try:
            treepolicy(root)
        except go.MoveError:    # hit a terminal position
            root.random_sim()   # run another simulation to mix up all the totals.

    return root.bestchild(conf_const=False, amaf_const=0)



