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
READTEST_H5 = path.join(TEST_DIR, 'readtests_sgf.h5')
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
    (319, -1)
    """
    return gomove.x - 1 + (gomove.y - 1)*size, gomove.player


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


def store_parser(sgf_gen=store(SGF_DIR)):
    """Generator of parsed main branches of all sgf files in store

    :param direc: string
    :yield: generator of sgf nodes
    >>> next(store_parser(store(sgf_direc=TEST_DIR)))['name']
    'anime028a'
    """
    bad_files = []
    for file_path, sgf_str in sgf_gen:
        try:
            node_gen = main_branch(parser(sgf_str))
        except Exception as err:
            message = str(err).encode('utf-8', errors='ignore').decode(encoding='ascii', errors='ignore')
            bad_files.append(message)
        else:
            game_details = {'sgfstr': sgf_str,
                            'path': file_path,
                            'name': file_path.split('\\')[-1].replace('.sgf', ''),
                            'moves': [],
                            'setup': [],
                            }
            for node in node_gen:
                try:
                    game_details['moves'].append(intmove(gomove=node_to_gomove(node), size=19))
                except ValueError:
                    name, value = info(node)
                    if value == '' or value == ' ':  # don't record blank info
                        continue
                    elif name in ['AB', 'AW']:
                        for handi in value.split(' '):
                            if handi == 'tt':
                                pass
                            else:
                                handi_pt = intmove(node_to_gomove(name[-1]+'[' + handi + ']'))
                                game_details['setup'].append(handi_pt)
                    elif name == 'C':
                        name += str(len(game_details['moves']))  # associate game comment to specific move

                    game_details[name] = value
            yield game_details

    if bad_files:
        raise ValueError('Unparsed SGFs sgfs\n' + '\n'.join(bad_files))


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
    >>> create_pro_hdf5(file=READTEST_H5, direc=TEST_DIR, sgf_direc=TEST_DIR)
    """
    with h5py.File(path.join(direc, file), 'w') as pro_games:
        failed_sgfs = []
        for game_id, game_details in enumerate(store_parser(store(sgf_direc=sgf_direc))):
            if game_id > abs(limit):
                break

            sgf = game_details['name']
            try:
                pro_games.create_group(sgf)
            except RuntimeError as err:
                raise ValueError('This SGF name already added to H5 file: ' + sgf)

            pro_games[sgf].create_dataset('moves', data=np.array(game_details['moves']))
            pro_games[sgf].create_dataset('setup', data=np.array(game_details['setup']))
            try:
                posi = go.Position.grayscaled_game(moves=game_details['moves'], setup=game_details['setup'])
            except Exception as err:
                failed_sgfs.append(str((sgf, str(err))))
            else:
                pro_games[sgf].create_dataset('gray', data=posi)

            for name in game_details:
                if name not in ['moves', 'setup']:
                    pro_games[sgf].attrs[name] = game_details[name]
    if failed_sgfs:
        raise ValueError('Incorrectly constructed sgfs\n'+'\n'.join(failed_sgfs))


def parse_to_thick_goban(sgf_file_name):
    """Parse an sgf file into a Position object

    :param sgf_file_name: string of the file location
    :return: thick_goban.Position
    """
    with open(sgf_file_name, 'r') as sgf_file:
        sgf_str = sgf_file.read()
    game_details = next(store_parser([(sgf_file_name, sgf_str)]))

    return go.Position(moves=game_details['moves'],
                       setup=game_details['setup'],
                       size=game_details.get('SZ', 19),
                       komi=game_details.get('KM', '6.5'))
