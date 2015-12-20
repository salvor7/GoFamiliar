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

    """
    bad_chars = [('\n', '')         # get rid of newline
                 , ('][', ' ')      # combine sequence (AB, AW, LB) info into one item
                 , ('"', '')        # double quotes used below
                ]
    for bad, fix in bad_chars:      # clear all round braces in sgf info nodes
        sgf_str = sgf_str.replace(bad, fix)

    # regex replacement format found at
    # https://docs.python.org/2/howto/regex.html#modifying-strings
    sgf_str = sgf_info_patt.sub(r'r"\1[\2]",', sgf_str)     # add double quotes and raw string r

    new_chars = [(';', ''),         # get rid of colons
                 ('(', '['),        # change tuple braces to list braces
                 (')', ']'),]

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

    :param sgf_list: list
    :yield: str

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


def node_to_move(node):
    """Return the GoMove for an SGF move node.

    :param node: SGF Node eg B[ah]
    :return: GoMove

    This function will also work with the alternative SGF move notation used in sgf_parser.

    >>> node_to_move('B[dc]')
    GoMove(player=1, x=4, y=3)
    >>> node_to_move('W[pq]')
    GoMove(player=-1, x=16, y=17)
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

    :param attribute: string
    :return: string, string
    >>> sgf_info('SZ[19]')
    ('SZ', '19')
    """
    try:
        name, value = re.findall(sgf_info_patt, attribute)[0]
    except:
        message = '"' + attribute + '" ' + 'is not a sgf info formatted node.'
        raise ValueError(message)
    return name, value


def sgf_store(direc=sgfdir):
    """Yield all raw strings from size 19 sgfs in sgf_store

    :param direc: string
    :yield: string
    >>> sum(1 for game in sgf_store()) > 45000
    True
    """
    files_found = dt.search_tree(directory=direc, file_sig='*.sgf')

    for file in files_found:
        with open(file, errors='ignore', encoding='utf-8') as sgf_file:
            try:
                string = sgf_file.read()
            except Exception as err:
                message = str(err) + '\n' + file + '\n' + string + '\n'*2
                raise SGFError(message)

            yield string


def sgf_store_parser(direc=sgfdir):
    """Generator of parsed main branches of all sgf files in sgf_store

    :param direc: string
    :yield: list
    >>> for _ in sgf_store_parser():
    ...     pass
    """
    bad_files = []
    for sgf_str in sgf_store(direc):
        try:
            yield sgf_main_branch(sgf_parser(sgf_str))
        except Exception as err:
            message = str(err).encode('utf-8', errors='ignore').decode(encoding='ascii', errors='ignore')
            bad_files.append(message)

    for msg in bad_files:
        print(msg)


class SGFError(Exception):
    pass


def create_sgf_csv(file='pro_collection.csv', direc='../sgf_store/', limit=None):
    """Create csv file of sgf_store

    :param file: string
    :param direc: string
    :param limit: int
    :return: None

    Add sgf strings from files in sgf_store folder as single lines in the csv file.
    Limit caps the number of iterations to that integer for testing.
    >>> create_sgf_csv(file='sgfcsv_doctest.csv', limit=100)

    """
    with open(direc + file, 'w', encoding='utf-8') as csv_file:
        for sgf_id, sgf_str in enumerate(sgf_store()):
            if limit and sgf_id > abs(limit):
                break
            csv_file.writelines(str(sgf_id) + ', ' + sgf_str.replace('\n', '') + '\n')


def create_sgf_hdf5(file='pro_collection.hdf5', direc='../sgf_store/', limit=None):
    """Create hdf5 file of sgf_store

    :param file: string
    :param direc: string
    :return: None

    Add sgf details from sgf files in sgf_store to a hdf5 binary.
    Each game is added as a group.
    Each sgf piece of info is added as an attribute of the group.
    All the moves are added as a data set under the group.
    Limit caps the number of iterations to that integer for testing.
    >>> create_sgf_hdf5(file='sgfhdf5_doctest.hdf5', limit=100)

    """
    with h5py.File(direc + file, 'w') as pro_games:

        pro_games.create_group('19')
        pro_games.create_group('13')
        pro_games.create_group('9')
        for game_id, sgf_nodes in enumerate(sgf_store_parser()):
            if limit and game_id > abs(limit):
                break

            game_attrs = {}
            move_list = []
            for node in sgf_nodes:
                try:
                    move_list.append(node_to_move(node))
                except ValueError:
                    name, value = sgf_info(node)
                    if value == '' or value == ' ':     # don't record blank info
                        continue
                    if name == 'C':
                        name += str(len(move_list))     # associated game comment to specific move
                    game_attrs[name] = value
            try:
                size = str(game_attrs['SZ'])
            except KeyError:
                size = '19'

            curr_game = str(game_id)
            try:
                pro_games[size].create_dataset(curr_game, data=np.array(move_list))
            except:
                print(size)
                raise
            for name in game_attrs:
                pro_games[size][curr_game].attrs[name] = game_attrs[name]

if __name__ == '__main__':
    create_sgf_hdf5(limit=0)
