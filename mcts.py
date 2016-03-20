"""
General Monte Carlo Tree Search algorithm

This module is a general implementation of an MCTS algorithm.
It is not intended to be specialized for go, though that is the first and only use anticipated.
It is based on the basic algorithm shown in "A Survey of Monte Carlo Tree Search Methods".
"""
from copy import deepcopy
from math import sqrt, log
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
        return 'n: {0} w: {1}'.format(self.sims, self.wins,)

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

        return child

    def random_sim(self):
        """
        Randomly simulate from the game state to a terminal state

        Updates the result up the tree.
        """
        def update_tree(moves, result):
            """
            MCTS update and All-Moves-As-First permutation style update

            Update node.amaf_wins total by sim win
                   node.amaf_sims total by 1
            for any node which can be reached by moves of the sam colour form the play out.

            move_set is expected to exclude moves after the first game capture.
            :param move_set: {BLACK:iter, WHITE:iter}
            """
            def update_children(node, moves):
                """
                Update AMAF counters recursively
                """
                node.amaf_sims.update(moves[node.colour])
                rate_update = {}
                for move in moves[node.colour]:
                    try:
                        r = node.amaf_rates[move]
                    except KeyError:
                        r = 0
                    rate_adj = (winner - r) / node.amaf_sims[move]
                    rate_update[move] = rate_adj
                node.amaf_rates.update(rate_update)
                for child in node.children.values():
                    update_children(node=child, moves=moves)

            self.sims += 1
            self.wins += winner
            root = self
            while root.parent is not None:
                root = root.parent
                root.sims += 1
                root.wins += winner

            update_children(node=root, moves=moves)

        terminal_state, moves = self.state.random_playout()
        winner = max(0, self.colour * terminal_state.winner())

        update_tree(moves=moves, result=winner)

        return terminal_state

    def bestchild(self, conf_const=0.0, amaf_const=0.5):
        """
        Find the child name with the highest score

        Formula is a mix of MCTS, AMAF, Permutation-AMAF and RAVE.
        The best AMAF child is created as a node if it is not already in the tree.
        :param conf_const: float
        :return: NodeMCTS
        """
        def score(node):
            """Return the node score as formula below

            (n/(n+an))*(w/n) + (an/(n+an))*(aw/an) + (n/(n+an))* (c*sqrt(log(N)/n))
            :return: float
            """
            w = node.wins
            n = node.sims
            N = node.parent.sims

            try:
                an = node.parent.amaf_sims[node.name]
            except KeyError:
                an = 0
                ar = 0
            else:
                ar = node.parent.amaf_rates[node.name]
            rate_balancer = (1/(1 + exp(n - 15)))
            return (1- rate_balancer) * (w / n) + rate_balancer*(ar)


        return max(self.children.values(), key=score)


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
                node = node.bestchild()
            except ValueError:  # no children
                try:
                    node = node.new_child()
                except go.MoveError:    # terminal position
                    node = root.bestchild(conf_const=1, amaf_const=0)   # start from root again
            if node.sims == 0:
                node.random_sim()
                break

    root = NodeMCTS(state=state)
    for move in root.state.actions:
        try:
            root.new_child(move_pt=move)
        except go.MoveError:
            continue

    while root.sims < sim_limit:
        treepolicy(root)

    return root.bestchild(conf_const=0).name



