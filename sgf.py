"""This module deals with all sgf related transformations.
"""
import ast
import re
from string import ascii_letters
import numpy as np

from gomove import GoMove

# regex pattern found at at http://www.nncron.ru/help/EN/add_info/regexp.htm Operators section
sgf_info_patt = re.compile(r'([A-Z][A-Z]?)\[(.+?)\]')


def sgf_parser(sgf_str):
    """Return a recursive list of lists representing an SGF string.

    SGF = Smart Game Format - http://senseis.xmp.net/?SmartGameFormat

    Using regex and replace, remake the SGF string for ast.literal_eval to create the list structure.
    Regex pattern found at at http://www.nncron.ru/help/EN/add_info/regexp.htm Operators section
    regex replacement format found at https://docs.python.org/2/howto/regex.html#modifying-strings

    Square braces are replaced with angled so that they do not interact with the literal_eval.
    KM[6.5]  ->     "KM<6.5>",
    B[de]    ->     "B<de>",
    The remaining replacements in new_chars were discovered by investigating smart game formatting
    and trial and error

    :param sgf_str: string in sgf format
    :return: list containing recursive structure of strings and lists

    >>> linear_sgf = '(;KM[2.75]SZ[19];B[qd];W[dd];B[oc];W[pp];B[do];W[dq])'
    >>> sgf_parser(linear_sgf)
    ['KM<2.75>', 'SZ<19>', 'B<qd>', 'W<dd>', 'B<oc>', 'W<pp>', 'B<do>', 'W<dq>']
    >>> basic_branching1 = '(;SZ[19](;B[qd];W[dd];B[oc])(;B[do];W[dq]))'
    >>> sgf_parser(basic_branching1)
    ['SZ<19>', ['B<qd>', 'W<dd>', 'B<oc>'], ['B<do>', 'W<dq>']]
    >>> basic_branching2 = '(;SZ[19];B[jj];W[kl](;B[dd](;W[gh])(;W[sa]))(;B[cd]))'
    >>> sgf_parser(basic_branching2)
    ['SZ<19>', 'B<jj>', 'W<kl>', ['B<dd>', ['W<gh>'], ['W<sa>']], ['B<cd>']]
    >>> complex_branching = ('(;RU[Japanese]SZ[19]KM[6.50];B[jj];W[kl]'
    ...                 '(;B[pd](;W[pp])(;W[dc](;B[de])(;B[dp])))'
    ...                 '(;B[cd];W[dp])'
    ...                 '(;B[cq](;W[pq])(;W[pd]))'
    ...                 '(;B[oq];W[dd]))')
    >>> for chunk in sgf_parser(complex_branching):
    ...    chunk
    'RU<Japanese>'
    'SZ<19>'
    'KM<6.50>'
    'B<jj>'
    'W<kl>'
    ['B<pd>', ['W<pp>'], ['W<dc>', ['B<de>'], ['B<dp>']]]
    ['B<cd>', 'W<dp>']
    ['B<cq>', ['W<pq>'], ['W<pd>']]
    ['B<oq>', 'W<dd>']
    >>> branchy_sgf = open('sgf_store/test_sgfs/branching_test.sgf').read()
    >>> game = sgf_parser(branchy_sgf)
    """

    # regex replacement format found at https://docs.python.org/2/howto/regex.html#modifying-strings
    sgf_str = sgf_info_patt.sub(r'"\1<\2>",',sgf_str)

    new_chars = [('\n', ''),        # get rid of newline
                 (';', ''),         # get rid of colons
                 ('(', '['),        # change tuple braces to list braces
                 (')', ']'),
                 (',]', ']'),       # get rid of extra end commas
                 ('][', '], [')     # add comma between branches
                 ]

    for char, new in new_chars:
        sgf_str = sgf_str.replace(char, new)

    return ast.literal_eval(sgf_str)



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
    branchy_sgf = open('sgf_store/test_sgfs/branching_test.sgf').read()
    game = sgf_parser(branchy_sgf)
    print(game)