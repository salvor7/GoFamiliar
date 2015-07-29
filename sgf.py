import re
import numpy as np
from string import ascii_letters
import pandas

size = 19
branch_start = '('
branch_end = ')'
node_marker = ';'
newline = '\n'
sgf_move_patt = re.compile(r'[BW][\[][a-s]{2}[\]]')
player_assign = {'B': 1, 'W': -1}
letter_coord_id = {letter: coord for letter, coord in zip(ascii_letters, range(size))}


def branchreader(sgfstr):
    """

    :param sgfstr:
    :return:
    """
    if type(sgfstr) == str:
        sgfchunks = sgfstr.replace(newline, '').split(branch_start)
    else:
        sgfchunks = sgfstr

    chunk = sgfchunks[0]
    game = []
    if chunk == '':
        game = branchreader(sgfchunks[1:])
    else:
        game += chunk.replace(branch_end, '').split(node_marker)
        if sgfchunks[1:]:
            game.append(branchreader(sgfchunks[1:]))

    while '' in game:
        game.remove('')
    return game


def node_to_board(node):
    """
    :param node:
    :return:
    """
    board = np.zeros((size, size), dtype=np.int8)
    #TODO consider using a dataframe instead of an array
    try:
        move = re.findall(sgf_move_patt, node)[0]
    except IndexError:
        return board

    player = player_assign[move[0]]
    x_coord, y_coord = letter_coord_id[move[2]], letter_coord_id[move[3]]

    board[y_coord][x_coord] += player

    return board


def nodelist_to_boardlist(nodelist):
    """

    :param nodelist:
    :return:
    """
    boardlist = [np.zeros((size, size), dtype=np.int8)]
    for node in nodelist:
        board = node_to_board(node)
        boardlist.append(np.sum([boardlist[-1], board], axis=0))

    return np.array(boardlist)


def printsgf(branchlist, level=0):
    """

    :param branchlist:
    :param level:
    :return:
    """
    for branch in branchlist:
        if type(branch) == str:
            print('     ' * level + branch)
        else:
            printsgf(branch, level+1)


def remove_captures(move_board, board):
    pass