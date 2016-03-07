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
                for child_name in moves[node.colour]:
                    try:
                        child = node.children[child_name]
                    except KeyError:
                        continue
                    else:
                        child.amaf_sims += 1
                        child.amaf_wins += result
                        if child.sims > 0:
                            reduced_moves = deepcopy(moves)
                            reduced_moves[node.colour] -= {child.name}
                            update_children(node=child, moves=reduced_moves)
            root = self
            root.sims += 1
            root.wins += winner
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
        Find the child with the highest upper confidence bound

        Formula from "A Survery of Monte Carlo Tree Search Methods"

        :param conf_const: float
        :param amaf_const: float
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
            try:
                return conf_const * (1 - amaf_const) * sqrt(log(N) / n)
            except ZeroDivisionError:
                return 0

        def amaf_rate(node):
            w = node.amaf_wins
            n = node.amaf_sims
            try:
                return amaf_const * (w / n)
            except ZeroDivisionError:
                return 0

        def score(node):
            return win_rate(node) + (amaf_rate(node) if conf_const == 0 else confidence(node))

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



