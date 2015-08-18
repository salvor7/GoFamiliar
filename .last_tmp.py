"""This module deals with all sgf related transformations.
"""
import re
from string import ascii_letters
import numpy as np

from gomove import GoMove

newline = '\n'
node_marker = r';'


def sgf_parser(sgf_str):
    """Return sgf_str as recursive list of lists.

    >>> linear_sgf = '(;KM[2.75]SZ[19];B[qd];W[dd];B[oc];W[pp];B[do];W[dq])'
    >>> sgf_parser(linear_sgf)
    ['KM[2.75]', 'SZ[19]', 'B[qd]', 'W[dd]', 'B[oc]', 'W[pp]', 'B[do]', 'W[dq]']
    >>> basic_branching1 = '(;(;B[qd];W[dd];B[oc])(;B[do];W[dq]))'
    >>> sgf_parser(basic_branching1)
    [['B[qd]', 'W[dd]', 'B[oc]'], ['B[do]', 'W[dq]']]
    >>> basic_branching2 = '(;B[dd](;W[gh];B[df])(;W[sa];B[as])(;W[cf]))'
    >>> sgf_parser(basic_branching2)
    [´B[dd]´, ['W[gh]', 'B[df]']['W[sa]', 'B[as]']['W[cf]']]
    >>> complex_branching = ('(;RU[Japanese]SZ[19]KM[6.50];B[jj];W[kl]'
    ...                 '(;B[pd](;W[pp])(;W[dc](;B[de])(;B[dp])))'
    ...                 '(;B[cd];W[dp])'
    ...                 '(;B[cq](;W[pq])(;W[pd]))'
    ...                 '(;B[oq];W[dd]))')
    >>> for chunk in sgf_parser(complex_branching):
    ...    chunk
    'RU[Japanese]'
    'SZ[19]'
    'KM[6.50]'
    'B[jj]'
    'W[kl]'
    ['B[pd]',['W[pp]'],['W[dc]',['B[de]'],[B[dp]]]]
    ['B[cd]','W[dp]']
    ['B[cq]',['W[pq]'],['W[pd]']]
    ['B[oq]','W[dd]']


    :param sgf_str: string in sgf format
    :return: list containing recursive structure of strings and lists
    """
    sgf_str = sgf_str.replace(newline, '')
    sgf_str = sgf_str.replace(node_marker,'')
    assert sgf_str[0] == '('
    #print(sgf_str)
    sgf_info_patt = re.compile(r'[A-Z][A-Z]?\[.+?\]')
    try:
        first_close = sgf_str.index(')')
    except ValueError:
        raise ValueError('Not an sgf: ' + sgf_str)

    try:
        second_open = sgf_str[1:].index('(') + 1
    except ValueError:
        #no second opening brace => single branch
        parsed_sgf = re.findall(sgf_info_patt, sgf_str)
        return parsed_sgf

    if first_close > second_open:
        main_branch = sgf_str[1:second_open]
        main_nodes = re.findall(sgf_info_patt, main_branch)

        subbranches = sgf_parser(sgf_str[second_open:])
        parsed_sgf = main_nodes + subbranches
    elif second_open > first_close:
        subbranch1 = sgf_parser(sgf_str[:second_open])
        remaining_branches = sgf_parser(sgf_str[second_open:])
        if type(remaining_branches[0]) == str:
            parsed_sgf = [subbranch1, remaining_branches]
        else:
            parsed_sgf = [subbranch1] + remaining_branches

    return parsed_sgf
#
# def sgf_reader(sgf_file):
#     """Read in the sgf meta data, and then recursively read the branch structure of an sgf file into a tree structure.
#
#     >>> import os
#     >>> folder = 'sgf_store\\\\test_sgfs'
#     >>> linear = 'linear_test.sgf'
#     >>> linear_game = sgf_reader(os.path.join(folder, linear))
#     >>> '' not in linear_game
#     True
#     >>> for node in linear_game:
#     ...     if not re.match(sgf_info_patt, node):
#     ...         print('something got in to that sgf')
#
#     >>> branchy = 'branching_test.sgf'
#     >>> branchy_game = sgf_reader(os.path.join(folder, branchy))
#     >>> #something
#
#     :param sgf_file: string = linear location and name
#     :return: tree of sgf nodes
#     """
#     def recur_branching(sgfchunks):
#         """
#
#         :param sgfchunks: list of sgf strings
#         :return: list of nodes and lists
#         """
#         game = []
#         front_chunk = sgfchunks[0]
#         print(front_chunk)
#         if branch_end in front_chunk:
#             front_chunk = front_chunk.replace(branch_end,'',1)
#
#             recur_branching([front_chunk])
#         else:
#             game += re.findall(sgf_info_patt, front_chunk)
#
#         if sgfchunks[1:]:
#             other_chunks = recur_branching(sgfchunks[1:])
#             game.append(other_chunks)
#
#         while '' in game:
#             game.remove('')
#
#         return game
#
#     branch_start = '('
#     branch_end = ')'
#
#
#
#     with open(sgf_file, encoding="utf8") as file:
#         sgfstr = file.read()
#
#     sgfchunks = sgfstr.replace(newline, '').split(branch_start)
#
#     game = recur_branching(sgfchunks)
#
#     return game
#
# def node_to_move(node):
#     """Return the GoMove for an sgf move node.
#
#     >>> move = node_to_move(r'B[dc]')
#     >>> move.player
#     1
#     >>> move.x
#     4
#     >>> move.y
#     3
#
#     :param node: sgf node eg B[ah]
#     :return: GoMove
#     """
#     size = 19
#     letter_coord_id = {letter: coord for letter, coord in zip(ascii_letters, range(size))}
#     player_assign = {'B': 1, 'W': -1}
#     # found regex patterns at http://www.nncron.ru/help/EN/add_info/regexp.htm Operators section
#
#     sgf_move_patt = re.compile(r'[BW]\[[a-s][a-s]\]')
#
#     board = np.zeros((size, size), dtype=np.int8)
#     try:
#         move = re.findall(sgf_info_patt, node)[0]
#     except IndexError:
#         return board
#
#     player = player_assign[move[0]]
#     x_coord, y_coord = letter_coord_id[move[2]], letter_coord_id[move[3]]
#
#     board[y_coord][x_coord] += player
#
#     return board


if __name__ == '__main__':
    import doctest
    doctest.testmod()