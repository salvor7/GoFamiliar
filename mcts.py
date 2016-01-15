"""General Monte Carlo Tree Search algorithm

This module is a general implementation of an MCTS algorithm.
It is not intended to be specialized for go, though that is the first and only use anticipated.
It is based on the basic algorithm shown in "A Survey of Monte Carlo Tree Search Methods".
"""
from copy import deepcopy
from math import sqrt, log

import godata as gd
from util import tree


def search(state, sim_limit=100, const=0, TerminalPosition=gd.TerminalPosition):
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


def expand(node, action):
    """Add new node in MC tree corresponding to taking action.

    "Expanding" is adding a child node with the associated state data to a non-terminal node.
    :param node: tree.Node
    :param action: action
    :return: tree.Node
    """
    state = deepcopy(node.data['state'])
    state.move(action)
    node_data = {'name': action,
                 'state': state,
                 'defaultpolicy': state.random_playout,
                 'wins': 0,
                 'sims': 0,
                 'parent': node,}
    child = tree.Node(node_data=node_data)
    node.add(child)
    return child


def bestchild(node, c=0):
    """Find the child with the highest upper confidence bound

    :param node: tree.Node
    :param c: float
    :return: tree.Node
    """
    def conf_score(node):
        wins = node.data['wins']
        sims = node.data['sims']
        player = -node.data['state'].next_player
        par_sims = node.data['parent'].data['sims']
        return player * wins / sims + c * sqrt(2 * log(par_sims) / sims)

    return max(node.children, key=conf_score)


def defaultpolicy(node):
    """The random game simulator

    :param state: game state
    :return: float
    """
    state = node.data['defaultpolicy']()
    score = state.score()
    return score/abs(score)


def backup(node, reward):
    """Record details of a sim backup the MC tree

    :param node: tree.Node
    :param reward: float
    """
    while node is not None:
        node.data['sims'] += 1
        node.data['wins'] += reward
        reward = -reward
        node = node.data['parent']
