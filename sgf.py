"""This module deals with all sgf related transformations.
"""
import re
from string import ascii_letters

from gomove import GoMove


branch_start = '('
branch_end = ')'
node_marker = ';'
newline = '\n'
# found regex patterns at http://www.nncron.ru/help/EN/add_info/regexp.htm Operators section
sgf_info_patt = re.compile(r'[A-Z][A-Z]?\[.+?\]')
sgf_move_patt = re.compile(r'[BW]\[[a-s][a-s]\]')
player_assign = {'B': 1, 'W': -1}
letter_coord_id = {letter: coord for letter, coord in zip(ascii_letters, range(size))}


def sgf_reader(sgf_file):
    """Read in the sgf meta data, and then recursively read the branch structure of an sgf file into a tree structure.

    >>> import os
    >>> folder = r'sgf_store\test_sgfs'
    >>> linear = 'linear_test.sgf'
    >>> linear_game = sgf_reader(os.path.join(folder, linear))
    >>> '' not in linear_game
    True
    >>> for node in linear_game:
    ...     if not re.match(sgf_info_patt, node)):
    ...         print('something got in to that sgf')

    >>> branchy = 'branching_test.sgf'
    >>> branchy_game = sgf_reader(os.path.join(folder, branchy))
    >>> something

    :param sgf_file: string = linear location and name
    :return: tree of sgf nodes
    """
    with open(sgf_file, encoding="utf8") as file:
        sgfstr = file.read()

    sgfchunks = sgfstr.replace(newline, '').split(branch_start)

    chunk = sgfchunks[0]
    game = []
    if chunk == '':
        game = sgf_reader(sgfchunks[1:])
    else:
        game += chunk.replace(branch_end, '').split(node_marker)
        if sgfchunks[1:]:
            game.append(sgf_reader(sgfchunks[1:]))

    while '' in game:
        game.remove('')

    return game

def node_to_move(node):
    """Return the GoMove for an sgf move node.

    >>> move = sgf.node_to_move(r'B[dc]')
    >>> move.player
    1
    >>> move.x
    4
    >>> move.y
    3

    :param node: sgf node eg B[ah]
    :return: GoMove
    """
    board = np.zeros((size, size), dtype=np.int8)
    try:
        move = re.findall(sgf_info_patt, node)[0]
    except IndexError:
        return board

    player = player_assign[move[0]]
    x_coord, y_coord = letter_coord_id[move[2]], letter_coord_id[move[3]]

    board[y_coord][x_coord] += player

    return board


if __name__ == '__main__':
    import doctest
    doctest.testmod()
