"""All these functions and objects will be moved in to a one off utility package. I am not yet sure how to handle these
 types of utility functions or objects.
"""

from os import walk, path
import fnmatch
from collections import namedtuple

def search_dir_tree(directory='.', file_sig='*.*'):
    """Find all files in a directory tree. Code snippet found at
        http://stackoverflow.com/questions/2186525/use-a-glob-to-find-files-recursively-in-python

    >>> search_dir_tree(file_sig='*.gitignore')
    ['.\\\\.gitignore']

    :param directory: string = root directory of search (default to working directory)
    :param file_sig: string = signature of files being sought
    :return: list = absolute linear locations of all found files
    """

    matches = []
    for root, dirnames, filenames in walk(directory):
        for filename in fnmatch.filter(filenames, file_sig):
            matches.append(path.join(root, filename))

    return matches

class Node:
    """Construct can be found at http://cbio.ufs.ac.za/live_docs/nbn_tut/trees.html

    >>> tree = Node('grandmother', [
    ...                             Node('daughter', [ Node('granddaughter'), Node('grandson')]),
    ...                             Node('son', [ Node('granddaughter'), Node('grandson')])
    ...                             ])
    >>> tree.value
    'grandmother'
    >>> tree.children[0].value
    'daughter'
    >>> tree.children[0].children[0].value
    'granddaughter'

    """
    def __init__(self, value, children = None):
        """Construct a Node.

        :param value: Node value
        :param children: [Nodes]
        """
        self.value = value
        self.children = children

if __name__ == '__main__':
    import doctest
    doctest.testmod()