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
        new_state.random_move()

        child = NodeMCTS(state=new_state)
        self.add(child=child)
        child.random_sim()

    def random_sim(self):
        """
        Randomly simulate from the game state to a terminal state
        """
        terminal_state, moves = self.state.random_playout()
        term_value = terminal_state.value()
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

        return max(self.children, key=conf_score)


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
    node_data = {'name':None,
                'state':state,
                 'defaultpolicy':state.random_playout,
                 'wins':0,
                 'sims':0,
                 'parent':None,}
    root = tree.Node(node_data=node_data)
    node = root
    while root.data['sims'] < sim_limit:
        node = treepolicy(node, const=const)
        reward = defaultpolicy(node)
        backup(node, reward)

    return bestchild(root, c=0).data['name']


def treepolicy(node, const=0):
    """Find a node to simulate a game for.

    :param node: tree.Node
    :param const: float
    :return: tree.Node
    """
    while True:
        try:
            action = next(node.data['actions'])
        except StopIteration:
            try:
                node = bestchild(node, c=const)
            except IndexError:
                break
        else:
            return expand(node, action)
    return node
