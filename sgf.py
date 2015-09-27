"""All sgf related transformations.

SGF = Smart Game Format - http://senseis.xmp.net/?SmartGameFormat
An SGF string is formatted as described at the website.
"""

import ast
import re
from string import ascii_letters
import h5py
import numpy as np
import util.directory_tools as dt

from go_objects import GoMove

sgfdir = u'C:/AllProgrammingProjects/GoFamiliar/sgf_store'

# regex pattern found at at http://www.nncron.ru/help/EN/add_info/regexp.htm Operators section
sgf_move_patt = re.compile(r'[BW]\[[a-s][a-s]\]')
sgf_info_patt = re.compile(r'([A-Z][A-Z]?)\[(.+?)\]')

def sgf_parser(sgf_str):
    """Return a recursive list of lists representing an SGF string.

    Branches, which are represented as subgames in SGF, are stored as sublists in the output.

    Using regex and replace, remake the SGF string for ast.literal_eval to create the list structure.
    Regex pattern found at at http://www.nncron.ru/help/EN/add_info/regexp.htm Operators section
    Regex replacement format found at https://docs.python.org/2/howto/regex.html#modifying-strings

    Square braces are replaced with angled so that they do not interact with the literal_eval.
    KM[6.5]  ->     r"KM[6.5]",
    B[de]    ->     r"B[de]",
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
    >>> basic_branching2 = '(;SZ[19];B[jj];W[kl](;B[dd](;W[gh])   (;W[sa]))(;B[cd]))'
    >>> sgf_parser(basic_branching2)
    ['SZ[19]', 'B[jj]', 'W[kl]', ['B[dd]', ['W[gh]'], ['W[sa]']], ['B[cd]']]
    >>> complex_branching = ('(;RU[Japanese]SZ[19]KM[6.50];B[jj];W[kl]'
    ...                 '(;B[pd](;W[pp]) (;W[dc](;B[de])(;B[dp])))'
    ...                 '(;B[cd];W[dp])'
    ...                 '(;B[cq](;W[pq])  (;W[pd]))'
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
    """
    bad_chars = [('\n', '')         # get rid of newline
                 , ('][', ' ')      # combine sequence (AB, AW, LB) info into one item
                 , ('"', '')        # double quotes used below
                ]
    for bad, fix in bad_chars:      # clear all round braces in sgf info nodes
        sgf_str = sgf_str.replace(bad, fix)

    # regex replacement format found at https://docs.python.org/2/howto/regex.html#modifying-strings
    sgf_str = sgf_info_patt.sub(r'r"\1[\2]",', sgf_str)     # add double quotes and raw string r

    new_chars = [(';', ''),         # get rid of colons
                 ('(', '['),        # change tuple braces to list braces
                 (')', ']'),
                 ]

    for char, new in new_chars:
        sgf_str = sgf_str.replace(char, new)

    sgf_str = re.sub(r'(\]) *(\[)', r'\1, \2', sgf_str)  # add comma between branches

    try:
        return ast.literal_eval(sgf_str)
    except Exception as err:
        message = str(err) + '\n' + sgf_str
        raise SGFError(message)


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
    ... except ValueError as err:
    ...     print(err)
    "error" is not a sgf move formatted node

    :param node: SGF Node eg B[ah]
    :return: GoMove
    """
    size = 19
    letter_coord_id = {letter: coord for letter, coord in zip(ascii_letters, range(1, size + 1))}
    player_assign = {'B': 1, 'W': -1}
    # found regex patterns at http://www.nncron.ru/help/EN/add_info/regexp.htm Operators section

    try:
        move = re.findall(sgf_move_patt, node)[0]
    except IndexError:
        raise ValueError('"' + node + '" is not a sgf move formatted node')

    player = player_assign[move[0]]
    x_coord, y_coord = letter_coord_id[move[2]], letter_coord_id[move[3]]

    return GoMove(player, x_coord, y_coord)


def sgf_info(attribute):
    """Return the sgf attribute name and value.

    >>> sgf_info('SZ[19]')
    ('SZ', '19')

    :param attribute: string
    :return: string, string
    """
    try:
        name, value = re.findall(sgf_info_patt, attribute)[0]
    except BaseException as err:
        message = '"' + attribute + '" ' + 'is not a sgf info formatted node.'
        raise ValueError(message)
    return name, value


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


def sgf_store(dir=sgfdir):
    """Yield all raw strings from size 19 sgfs in sgf_store

    >>> sum(1 for game in sgf_store()) > 45000
    True

    :param dir: string
    :yield: string
    """
    files_found = dt.search_tree(directory=dir, file_sig='*.sgf')

    for file in files_found:
        with open(file, errors='ignore', encoding='utf-8') as sgf_file:
            try:
                string = sgf_file.read()
            except Exception as err:
                message = str(err) + '\n' + file + '\n' + string + '\n'*2
                raise SGFError(message)

            yield string

def sgf_store_parser(dir=sgfdir):
    """Generator of parsed main branches of all sgf files in sgf_store

    >>> for _ in sgf_store_parser():
    ...     pass

    :param dir: string
    :yield: list
    """
    bad_files = []
    for sgf_str in sgf_store(dir):
        try:
            yield sgf_main_branch(sgf_parser(sgf_str))
        except Exception as err:
            message = str(err).encode('utf-8', errors='ignore').decode(encoding='ascii', errors='ignore')
            bad_files.append(message)

    for msg in bad_files:
        print(msg)


class SGFError(Exception):
    pass


def create_sgf_csv(file='pro_collection.csv', dir='sgf_store/', limit=None):
    """Create csv file of sgf_store

    Add sgf strings from files in sgf_store folder as single lines in the csv file.
    Limit caps the number of iterations to that integer for testing.
    >>> create_sgf_csv(file='sgfcsv_doctest.csv', limit=100)

    :param file: string
    :param dir: string
    :param limit: int
    :return: None
    """
    with open(dir + file, 'w', encoding='utf-8') as csv_file:
        for sgf_id, sgf_str in enumerate(sgf_store()):
            if limit and sgf_id > abs(limit):
                break
            csv_file.writelines(str(sgf_id) + ', ' + sgf_str.replace('\n', '') + '\n')





def create_sgf_hdf5(file='pro_collection.hdf5', dir='sgf_store/', limit=None):
    """Create hdf5 file of sgf_store

    :param file: string
    :param dir: string
    :return: None
    """
    pro_games = h5py.File(dir + file, 'w')

    for game_id, sgf_nodes in enumerate(sgf_store()):
        curr_game = 'Game' + str(game_id)
        pro_games.create_group(curr_game)

        move_list = []
        for node in sgf_nodes:
            try:
                move_list.append(node_to_move(node))
            except ValueError:
                name, value = sgf_info(node)
                if value == '' or value == ' ':     # don't record blank info
                    continue
                if name == 'C':
                    name += str(len(move_list))     # associated comment to specific move
                pro_games[curr_game].attrs[name] = value

        pro_games[curr_game].create_dataset('moves', data=np.array(move_list))


if __name__ == '__main__':
    create_sgf_hdf5()