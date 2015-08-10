"""
>>> 1+1
3
>>> print(
... 'you')
you6
"""
from os import walk, path
import fnmatch

import re
from string import ascii_letters

import numpy as np
import pandas as pd


size = 19
branch_start = '('
branch_end = ')'
node_marker = ';'
newline = '\n'
# found regex details at http://www.nncron.ru/help/EN/add_info/regexp.htm Operators section
sgf_patt = re.compile(r'[A-Z][A-Z]?\[.+?\]')
player_assign = {'B': 1, 'W': -1}
letter_coord_id = {letter: coord for letter, coord in zip(ascii_letters, range(size))}



def sgf2df(sgf_file):
    """Create a pandas series object from an sgf file.

    :param sgf_file: an sgf file string
    :return: Pandas series object
    """
    with open(sgf_file, encoding="utf8") as file:
        linear_sgf = file.read()
    print(re.findall(sgf_patt, linear_sgf))



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
    #TODO change to a dataframe instead of an array
    try:
        move = re.findall(sgf_patt, node)[0]
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
            try:
                print('     ' * level + branch)
            except UnicodeEncodeError:
                pass
        else:
            printsgf(branch, level+1)


def remove_captures(move_board, board):
    pass


if __name__ == '__main__':
    matches = []
    sgf_dir = r'C:\AllProgrammingProjects\GoFamiliar\sgf_store\baduk-pro-collection'
    #TODO factor this directory search out of project to a utilities project
    """code snippet to find all files in a directory tree found at
        http://stackoverflow.com/questions/2186525/use-a-glob-to-find-files-recursively-in-python"""
    for root, dirnames, filenames in walk(sgf_dir):

        for filename in fnmatch.filter(filenames, '*.sgf'):
            # DO LATER add other sgf features to other dataframe columns
            # DO LATER rotate and flip all games

            with open(path.join(root, filename), encoding='utf-8') as sgf_file:
                # TODO deal with the chinese characters in the sgf files
                pass # printsgf(sgf_file.read())

            break
                # TODO - open files and add sgf game string to dataframe

    # TODO output dataframe to json or csv. call is pro game master file or soemthing

    import doctest

    doctest.testmod(verbose=True)
