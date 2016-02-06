"""
General Monte Carlo Tree Search algorithm

This module is a general implementation of an MCTS algorithm.
It is not intended to be specialized for go, though that is the first and only use anticipated.
It is based on the basic algorithm shown in "A Survey of Monte Carlo Tree Search Methods".
"""
from copy import deepcopy
from math import sqrt, log

import go
from util import tree


class NodeMCTS(tree.Node):
    """
    A node of MC search tree
    """
    def __init__(self, state, children=None):
        """
        Initialize a MCTS node object
        """
        self.name = state.last_move,
        self.state = state
        self.wins = 0
        self.sims = 0
        super(NodeMCTS, self).__init__(children=children)
        children = {}

    @property
    def colour(self):
        """
        Return the two player colour

        :return: int
        """
        return self.state.next_player

    def new_child(self):
        """
        Add a new child node and play it out
        """
        new_state=deepcopy(self.state)
        new_state.random_move(tried=self.children.key())

        child = NodeMCTS(state=new_state)
        self.children[child.name] = child
        child.random_sim()
        return child

    def random_sim(self):
        """
        Randomly simulate from the game state to a terminal state

        Updates the result up the tree.
        """
        terminal_state, moves = self.state.random_playout()
        winner = terminal_state.winner()
        self.sims += 1
        self.wins += term_value
        self.update_parent(value=term_value)

    def update_parent(self, value):
        """
        Update sim results up the tree
        :param value: numeric
        """
        try:
            self.parent.sims += 1
        except AttributeError:
            pass       # root reached
        else:
            self.parent.wins += value
            self.parent.update_parent(value=value)

    def bestchild(self, c=0):
        """
        Find the child with the highest upper confidence bound

        Formula from "A Survery of Monte Carlo Tree Search Methods"
        :param c: float
        :return: NodeMCTS
        """
        def conf_score(node):
            w = node.wins
            n = node.sims
            col = self.colour       # white scores negative
            N = node.parent.sims
            return col * w / n + c * sqrt(2 * log(N) / n)

        return max(self.children.values(), key=conf_score)


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
        """Simulate a select node

        :param root: NodeMCTS
        :param const: float
        :return: NodeMCTS
        """
        node = root
        while True:
            try:
                new_child = node.new_child()
            except go.MoveError:    # no moves to expand node with
                try:
                    node = node.bestchild(c=const)
                except ValueError:      # no children either, so terminal position
                    return node
            else:
                return new_child

    root = NodeMCTS(state=state)
    while root.sims < sim_limit:
        treepolicy(root)

    return root.bestchild(c=0).name



