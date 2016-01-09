import random

from math import sqrt, log

import godata as gd
from util import tree


def search(state):
    node_data = {'name':None,
                'state':state,
                 'actions':[a for a in state.actions],
                 'wins':0,
                 'sims':0,
                 'parent':None,}
    root = tree.Node(value=node_data)
    node = root
    while root.value['sims'] < 100:
        node = treepolicy(node)
        reward = defaultpolicy(node.value['state'].deepcopy())
        backup(node, reward)

    return bestchild(root, 0)['name']


def treepolicy(node):
    while len(node.value['state'].actions) > 0 and len(node.children) > 0: # non-terminal
        if len(node.value['state'].actions) > 0: # not fully expanded
            return expand(node)
        else:
            node = bestchild(node)
    return node


def expand(node):
    action = node.value['actions'].pop()
    state = node.value['state'].deepcopy()
    state.move(action)
    node_data = {'name':action,
            'state':state,
             'actions':[a for a in state.actions],
             'wins':0,
             'sims':0,
             'parent':node,}
    child = tree.Node(value=node_data)
    node.children.add(child)


def bestchild(node):
    def conf_score(node):
        wins = node.value['wins']
        sims = node.value['sims']
        c = node.value['state'].mcts_const
        par_sims = node.value['parent'].value['sims']
        return wins/sims + c * sqrt(2*log(par_sims)/sims)
    conf = [(conf_score(v), v) for v in node.children]
    conf.sort()
    return conf[0][1]


def defaultpolicy(state, MoveError):
    while len(state.actions) > 0:
        action = state.action[0]
        state.move(action)
    return state.score()


def backup(node, reward):
    while node is not None:
        node['sims'] += 1
        node['wins'] += reward
        reward = -reward
        node = node.value['parent']

