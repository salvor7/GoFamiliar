"""All sgf related transformations.

SGF = Smart Game Format - http://senseis.xmp.net/?SmartGameFormat
An SGF string is formatted as described at the website.
"""

import ast
from os import path
import re
import pathlib
from collections import namedtuple
from string import ascii_letters

import h5py
import numpy as np
from thick_goban import go

import util.directory_tools as dt


DATA_DIR = path.join(str(pathlib.Path(__file__).parents[2]), 'data')
SGF_DIR = path.join(DATA_DIR, 'sgf_store')
SGF_CSV = path.join(DATA_DIR, 'pro_sgf.csv')
SGF_H5 = path.join(DATA_DIR, 'pro_sgf.h5')

TEST_DIR = path.join(DATA_DIR, 'test_sets')
TEST_H5 = path.join(TEST_DIR, 'tests_sgf.h5')
TEST_CSV = path.join(TEST_DIR, 'tests_sgf.csv')


# regex pattern found at at http://www.nncron.ru/help/EN/add_info/regexp.htm Operators section
sgf_move_patt = re.compile(r'[BW]\[[a-s][a-s]\]')
sgf_info_patt = re.compile(r'([A-Z][A-Z]?)\[(.+?)\]')


def parser(sgf_str):
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
    >>> parser(linear_sgf)
    ['KM[2.75]', 'SZ[19]', 'B[qd]', 'W[dd]', 'B[oc]', 'W[pp]', 'B[do]', 'W[dq]']
    >>> basic_branching1 = '(;SZ[19](;B[qd];W[dd];B[oc])(;B[do];W[dq]))'
    >>> parser(basic_branching1)
    ['SZ[19]', ['B[qd]', 'W[dd]', 'B[oc]'], ['B[do]', 'W[dq]']]
    """
    bad_chars = [('\n', '')  # get rid of newline
        , ('][', ' ')  # combine sequence (AB, AW, LB) info into one item
        , ('"', '')  # double quotes used below
                 ]
    for bad, fix in bad_chars:  # clear all round braces in sgf info nodes
        sgf_str = sgf_str.replace(bad, fix)

    # regex replacement format found at
    # https://docs.python.org/2/howto/regex.html#modifying-strings
    sgf_str = sgf_info_patt.sub(r'r"\1[\2]",',
                                sgf_str)  # add double quotes and raw string r

    new_chars = [(';', ''),  # get rid of colons
                 ('(', '['),  # change tuple braces to list braces
                 (')', ']'), ]

    for char, new in new_chars:
        sgf_str = sgf_str.replace(char, new)

    sgf_str = re.sub(r'(\]) *(\[)', r'\1, \2', sgf_str)  # add comma between branches

    try:
        return ast.literal_eval(sgf_str)
    except Exception as err:
        message = str(err) + '\n' + sgf_str
        raise SGFError(message)


def main_branch(sgf_list):
    """Yield the nodes of the main branch of an sgf string.

    :param sgf_list: list       parser parsed sgf
    :yield: str                 string representing the sgf node

    Searches every branch of the sgf list, and returns each first subbranch.
    >>> basic_branching1 = '(;SZ[19](;B[qd];W[dd];B[oc])(;B[do];W[dq]))'
    >>> [node for node in main_branch(parser(basic_branching1))]
    ['SZ[19]', 'B[qd]', 'W[dd]', 'B[oc]']
    """
    for node in sgf_list:
        if type(node) == list:
            for node in main_branch(node):
                yield node
            break
        else:
            yield node


def node_to_gomove(node):
    """Return the GoMove for an SGF move node.

    :param node: SGF Node eg B[ah]
    :return: GoMove

    This function will also work with the alternative SGF move notation used in sgf_parser.

    >>> node_to_gomove('B[dc]')
    GoMove(player=1, x=4, y=3)
    >>> node_to_gomove('W[pq]')
    GoMove(player=-1, x=16, y=17)
    """
    size = 19
    letter_coord_id = {letter: coord for letter, coord in
                       zip(ascii_letters, range(1, size + 1))}
    player_assign = {'B': 1, 'W': -1}

    # found regex patterns at http://www.nncron.ru/help/EN/add_info/regexp.htm Operators section
    try:
        move = re.findall(sgf_move_patt, node)[0]
    except IndexError:
        raise ValueError('"' + node + '" is not an sgf move formatted node')

    player = player_assign[move[0]]
    x_coord, y_coord = letter_coord_id[move[2]], letter_coord_id[move[3]]

    return GoMove(player, x_coord, y_coord)


def intmove(gomove, size=19):
    """Return integer position of a GoMove

    :param gomove: GoMove
    :param size: int
    :return: int
    >>> intmove(GoMove(player=-1, x=16, y=17))
    319
    """
    return gomove.x - 1 + (gomove.y - 1)*size


def info(attribute):
    """Return the sgf attribute name and data.

    :param attribute: string
    :return: string, string
    >>> info('SZ[19]')
    ('SZ', '19')
    """
    try:
        name, value = re.findall(sgf_info_patt, attribute)[0]
    except:
        message = '"' + attribute + '" ' + 'is not a sgf info formatted node.'
        raise ValueError(message)
    return name, value


def store(sgf_direc=SGF_DIR):
    """Yield all raw sgf strings from sgfs in store

    :param sgf_direc: string    path string
    :yield: string              sgf game string
    >>> sum([len(game) for file_path, game in store(sgf_direc=TEST_DIR)])
    166473
    """
    files_found = dt.search_tree(directory=sgf_direc, file_sig='*.sgf')

    for file_path in files_found:
        with open(file_path, errors='ignore', encoding='utf-8') as sgf_file:
            try:
                sgf_str = sgf_file.read()
            except Exception as err:
                message = str(err) + '\n' + file_path
                raise SGFError(message)

            yield file_path, sgf_str


def store_parser(sgf_direc=SGF_DIR):
    """Generator of parsed main branches of all sgf files in store

    :param direc: string
    :yield: generator of sgf nodes
    >>> first_nodes = set([next(game).split('[')[0] for file_path, game in store_parser(sgf_direc=TEST_DIR)])
    >>> first_nodes = list(first_nodes)
    >>> first_nodes.sort()
    >>> first_nodes
    ['AB', 'AP', 'FF', 'GM', 'OM', 'PW', 'SZ']
    """
    bad_files = []
    for file_path, sgf_str in store(sgf_direc):
        try:
            yield file_path, main_branch(parser(sgf_str))
        except Exception as err:
            message = str(err).encode('utf-8', errors='ignore').decode(encoding='ascii', errors='ignore')
            bad_files.append(message)

    for msg in bad_files:
        print(msg)


class SGFError(Exception):
    pass


def create_pro_csv(file=SGF_CSV, direc=DATA_DIR, limit=None):
    """Create csv file of data

    :param file: string
    :param direc: string
    :param limit: int
    :return: None

    Add sgf strings from files in data folder as single lines in the csv file.
    Limit caps the number of iterations to that integer for testing.
    >>> create_pro_csv(file=TEST_CSV, direc=TEST_DIR)
    """
    with open(path.join(direc, file), 'w', encoding='utf-8') as csv_file:
        for sgf_id, (sgf_path, sgf_str) in enumerate(store(sgf_direc=direc)):
            if limit and sgf_id > abs(limit):
                break
            csv_file.writelines(sgf_path + ', ' + sgf_str.replace('\n', '') + '\n')


def create_pro_hdf5(file=SGF_H5, direc=DATA_DIR, sgf_direc=SGF_DIR, limit=np.inf):
    """Create hdf5 file of data

    :param file: string
    :param direc: string
    :param sgf_direc: string
    :return: None

    Add sgf details from sgf files in data to a hdf5 binary.
    Each game is added as a group.
    Each sgf piece of info is added as an attribute of the group.
    All the moves are added as a data set under the group.
    Limit caps the number of iterations to that integer for testing.
    >>> create_pro_hdf5(file=TEST_H5, direc=TEST_DIR, sgf_direc=TEST_DIR)
    """
    with h5py.File(path.join(direc, file), 'w') as pro_games:

        for game_id, (sgf_path, node_gen) in enumerate(store_parser(sgf_direc=sgf_direc)):
            if game_id > abs(limit):
                break

            game_attrs = {}
            move_list = []
            for node in node_gen:
                try:
                    move_list.append(intmove(gomove=node_to_gomove(node), size=19))
                except ValueError:
                    name, value = info(node)
                    if value == '' or value == ' ':  # don't record blank info
                        continue
                    if name == 'C':
                        name += str(len(move_list))  # associate game comment to specific move
                    game_attrs[name] = value

            sgf_year, sgf_month, sgf_file = sgf_path.split('\\')[-3:]
            sgf_name = sgf_file.replace('.sgf', '')
            if 'DT' not in game_attrs:
                game_attrs['DT'] = ' '.join(['Year:', sgf_year, 'Month:', sgf_month])
            pro_games.create_dataset(sgf_name, data=np.array(move_list))

            for name in game_attrs:
                pro_games[sgf_name].attrs[name] = game_attrs[name]


class GoMove(namedtuple('GoMove', 'player x y')):
    """GoMove namedtuple object

    >>> black_tengen = GoMove(player=1, x=10, y=10)
    >>> black_tengen
    GoMove(player=1, x=10, y=10)
    >>> white_komoku = GoMove(-1,3,4)
    >>> white_komoku
    GoMove(player=-1, x=3, y=4)
    """
    pass


def parse_to_thick_goban(sgf_file_name):
    """Parse an sgf file into a Position object

    :param sgf_file_name: string of the file location
    :return: thick_goban.Position
    """
    with open(sgf_file_name, 'r') as sgf_file:
        sgf_node_gen = main_branch(parser(sgf_file.read()))
    game_attrs = {}
    move_list = []
    for node in sgf_node_gen:
        try:
            size = int(game_attrs['SZ'])
        except KeyError:
            size = 19
        try:
            move_list.append(intmove(gomove=node_to_gomove(node), size=size))
        except ValueError:
            name, value = info(node)
            if value == '' or value == ' ':  # don't record blank info
                continue
            if name == 'C':
                name += str(
                    len(move_list))  # associated game comment to specific move
            game_attrs[name] = value

    try:
        size = int(game_attrs['SZ'])
    except KeyError:
        raise KeyError('SGF has no size attribute')
    try:
        komi = float(game_attrs['KM'])
    except KeyError:
        komi = 6.5

    return go.Position(moves=move_list, size=size, komi=komi)
