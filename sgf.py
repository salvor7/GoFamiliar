"""All sgf related transformations.

SGF = Smart Game Format - http://senseis.xmp.net/?SmartGameFormat
An SGF string is formatted as described at the website.
"""

import ast
import re
from string import ascii_letters
import numpy as np
import util.directory_tools as dt

from go_objects import GoMove

# regex pattern found at at http://www.nncron.ru/help/EN/add_info/regexp.htm Operators section
sgf_info_patt = re.compile(r'([A-Z][A-Z]?)\[(.+?)\]')

def sgf_parser(sgf_str):
    """Return a recursive list of lists representing an SGF string.

    Branches, which are represented as subgames in SGF, are stored as sublists in the output.

    Using regex and replace, remake the SGF string for ast.literal_eval to create the list structure.
    Regex pattern found at at http://www.nncron.ru/help/EN/add_info/regexp.htm Operators section
    Regex replacement format found at https://docs.python.org/2/howto/regex.html#modifying-strings

    Square braces are replaced with angled so that they do not interact with the literal_eval.
    KM[6.5]  ->     "KM[6.5]",
    B[de]    ->     "B[de]",
    The remaining replacements in new_chars were discovered by investigating smart game formatting
    and trial and error.

    :param sgf_str: SGF string
    :return: list of strings and lists

    >>> linear_sgf = '(;KM[2.75]SZ[19];B[qd];W[dd];B[oc];W[pp];B[do];W[dq])'
    >>> sgf_parser(linear_sgf)
    ['KM[2.75]', 'SZ[19]', 'B[qd]', 'W[dd]', 'B[oc]', 'W[pp]', 'B[do]', 'W[dq]']
    >>> basic_branching1 = '(;SZ[19](;B[qd];W[dd];B[oc])(;B[do];W[dq]))'
    >>> sgf_parser(basic_branching1)
    ['SZ[19]', ['B[qd]', 'W[dd]', 'B[oc]'], ['B[do]', 'W[dq]']]
    >>> basic_branching2 = '(;SZ[19];B[jj];W[kl](;B[dd](;W[gh])(;W[sa]))(;B[cd]))'
    >>> sgf_parser(basic_branching2)
    ['SZ[19]', 'B[jj]', 'W[kl]', ['B[dd]', ['W[gh]'], ['W[sa]']], ['B[cd]']]
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
    ['B[pd]', ['W[pp]'], ['W[dc]', ['B[de]'], ['B[dp]']]]
    ['B[cd]', 'W[dp]']
    ['B[cq]', ['W[pq]'], ['W[pd]']]
    ['B[oq]', 'W[dd]']
    >>> branchy_sgf = open('sgf_store/test_sgfs/branching_test.sgf').read()
    >>> game = sgf_parser(branchy_sgf)

    """

    # regex replacement format found at https://docs.python.org/2/howto/regex.html#modifying-strings
    sgf_str = sgf_info_patt.sub(r'"\1[\2]",',sgf_str)

    new_chars = [('\n', ''),        # get rid of newline
                 (';', ''),         # get rid of colons
                 ('(', '['),        # change tuple braces to list braces
                 (')', ']'),
                 ('][', '], [')     # add comma between branches
                 ]

    for char, new in new_chars:
        sgf_str = sgf_str.replace(char, new)

    return ast.literal_eval(sgf_str)


def sgf_main_branch(sgf_list):
    """Returns the main branch of an sgf string.

    Searches every branch of the sgf list, and returns the first branch at each branch.

    >>> linear_sgf = '(;KM[2.75]SZ[19];B[qd];W[dd];B[oc];W[pp];B[do];W[dq])'
    >>> sgf_parser(linear_sgf) == sgf_main_branch(sgf_parser(linear_sgf))
    True
    >>> basic_branching1 = '(;SZ[19](;B[qd];W[dd];B[oc])(;B[do];W[dq]))'
    >>> sgf_main_branch(sgf_parser(basic_branching1))
    ['SZ[19]', 'B[qd]', 'W[dd]', 'B[oc]']
    >>> complex_branching = ('(;RU[Japanese]SZ[19]KM[6.50];B[jj];W[kl]'
    ...                 '(;B[pd](;W[pp])(;W[dc](;B[de])(;B[dp])))'
    ...                 '(;B[cd];W[dp])'
    ...                 '(;B[cq](;W[pq])(;W[pd]))'
    ...                 '(;B[oq];W[dd]))')
    >>> sgf_main_branch(sgf_parser(complex_branching))
    ['RU[Japanese]', 'SZ[19]', 'KM[6.50]', 'B[jj]', 'W[kl]', 'B[pd]', 'W[pp]']

    :param sgf_str:
    :return:
    """
    main_branch = []
    for node in sgf_list:
        if type(node) == list:
            main_branch += sgf_main_branch(node)
            break
        else:
            main_branch.append(node)

    return main_branch


def node_to_move(node):
    """Return the GoMove for an SGF move node.

    This function will also work with the alternative SGF move notation used in sgf_parser.

    >>> node_to_move('B[dc]')
    GoMove(player=1, x=4, y=3)
    >>> node_to_move('W[pq]')
    GoMove(player=-1, x=16, y=17)
    >>> try:
    ...     node_to_move('error')
    ... except TypeError as err:
    ...     print(err)
    node is not Smart Game formatted


    :param node: SGF Node eg B[ah]
    :return: GoMove
    """
    size = 19
    letter_coord_id = {letter: coord for letter, coord in zip(ascii_letters, range(1, size + 1))}
    player_assign = {'B': 1, 'W': -1}
    # found regex patterns at http://www.nncron.ru/help/EN/add_info/regexp.htm Operators section

    sgf_move_patt = re.compile(r'[BW]\[[a-s][a-s]\]')

    try:
        move = re.findall(sgf_move_patt, node)[0]
    except IndexError:
        raise TypeError('node is not Smart Game formatted')

    player = player_assign[move[0]]
    x_coord, y_coord = letter_coord_id[move[2]], letter_coord_id[move[3]]

    return GoMove(player, x_coord, y_coord)


def sgf_to_final(sgf_str):
    """Return GoPostion object of final game position of sgf_str.

    >>> basic = '(;SZ[3];B[bb];W[ba];B[ab];B[cb])'
    >>> sgf_to_final(basic).board
    [[0 1 0]
     [1 1 -1]
     [0 -1 0]]

    :param sgf_str: SGF string
    :return: GoPostion
    """
    pass


def sgf_to_game(sgf_str):
    """Return GoGame from sgf_str

    :param sgf_str: SGF string
    :return: GoGame
    """
    pass


def sgf_store():
    """Yield all GoGame from sgfs in Sgf_store

    >>> [game for game in sgf_store()]

    :yield: GoGame
    """
    dir = u'C:/AllProgrammingProjects/GoFamiliar/sgf_store/baduk-pro-collection'

    files_found = dt.search_tree(directory=dir, file_sig='*.sgf')
    for file in files_found:
        with open(file, errors='replace', encoding='utf-8') as sgf_file:

            try:
                string = sgf_file.read()
            except:
                print(file)
                raise
            if 'SZ[19]' in string:
                yield sgf_main_branch(string)