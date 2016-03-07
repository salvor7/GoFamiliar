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
        self.amaf_wins = 0
        self.amaf_sims = 0
        super(NodeMCTS, self).__init__(children=children)
        self.children = {}

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
        new_state = deepcopy(self.state)
        new_state.random_move(tried=self.children.keys())

        child = NodeMCTS(state=new_state)
        child.random_sim()
        child.parent = self
        self.children[child.name] = child

        return child

    def random_sim(self):
        """
        Randomly simulate from the game state to a terminal state

        Updates the result up the tree.
        """
        terminal_state, moves = self.state.random_playout()
        winner = terminal_state.winner()
        self.sims += 1
        self.wins += winner
        self.update_parent(value=winner)
        winner = max(0, self.colour * terminal_state.winner())

        self.amaf_perm_update(moves=moves, result=winner)

        return terminal_state

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

    def bestchild(self, c=0.0, a=0.5):
        """
        Find the child with the highest upper confidence bound

        Formula from "A Survery of Monte Carlo Tree Search Methods"

        :param c: float
        :param a: float
        :return: NodeMCTS
        """
        def win_rate(node):
            w = node.wins
            n = node.sims
            try:
                return (1 - amaf_const) * (w / n)
            except ZeroDivisionError:
                return 0

        def confidence(node):
            n = node.sims
            N = node.parent.sims
            return c * (1 - a) * sqrt(log(N) / n)

        def amaf_rate(node):
            w = node.amaf_wins
            n = node.amaf_sims
            try:
                return amaf_const * (w / n)
            except ZeroDivisionError:
                return 0

        def score(node):
            return win_rate(node) + confidence(node) + amaf_rate(node)

        return max(self.children.values(), key=score)

    def amaf_perm_update(self, moves, result):
        """
        All-Moves-As-First permutation style update

        Update node.amaf_wins total by sim win
               node.amaf_sims total by 1
        for any node which can be reached by moves of the sam colour form the play out.

        move_set is expected to exclude moves after the first game capture.
        :param move_set: {BLACK:iter, WHITE:iter}
        """
        def update_children(node):
            for child in node.children.values():
                if child.name in moves[node.colour]:
                    child.amaf_sims += 1
                    child.amaf_wins += result
                    update_children(child)
        root = self
        parent = root.parent
        while parent is not None:
            root, parent = root.parent, parent.parent

        update_children(root)

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



