"""Directory tools"""

from os import walk, path
import fnmatch

def search_tree(directory='.', file_sig='*.*'):
    """Find all files in a directory tree.

    This code snippet was found at
    http://stackoverflow.com/questions/2186525/use-a-glob-to-find-files-recursively-in-python

    >>> matching_files = search_tree(file_sig='directory_tools.py')
    >>> matching_files
    ['.\\\\directory_tools.py']
    >>> file_obj = open(matching_files[0])

    :param directory: string = root directory of search (default to working directory)
    :param file_sig: string = signature of files being sought
    :return: list = absolute linear locations of all found files
    """

    matches = []
    for root, dirnames, filenames in walk(directory):
        for filename in fnmatch.filter(filenames, file_sig):
            matches.append(path.join(root, filename))

    return matches