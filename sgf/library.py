import os
import h5py
import numpy as np

import godata
import sgf.read

doctest_dir = r'sgf_store\hikaru_sgfs'
doctest_file = 'sgfhdf5_doctest.hdf5'

class Library():
    """SGF Library object

    >>> Library(doctest_dir, doctest_file)['chap075.sgf'][:10]
    array([ 72, 288, 300,  42,  59,  97,  61,  62,  80,  41])
    """
    def __init__(self, direc, file):
        while True:
            try:
                self._library_file = h5py.File(os.path.join(direc, file), 'r')
                break
            except OSError:
                sgf.read.create_pro_hdf5(direc=direc, file=file)

    def __getitem__(self, sgf_name):
        """Return the sgf dataset

        :param item: str
        :return: h5py.dataset
        >>> Library(doctest_dir, doctest_file)['chap116.sgf']
        <HDF5 dataset "chap116.sgf": shape (262,), type "<i4">
        """
        return self._library_file[sgf_name]

    def __len__(self):
        """Return number of stored sgfs

        :return: int
        >>> len(Library(doctest_dir, doctest_file))
        3
        """
        return len(self._library_file)

    def __iter__(self):
        """Return iterator over stored go games

        :return: iter
        >>> for sgf_name in Library(doctest_dir, doctest_file):
        ...     print(sgf_name)
        chap075.sgf
        chap116.sgf
        chap170a.sgf
        """
        return iter(self._library_file)

    def sgf_attributes(self, sgf_name):
        """Return the dictionary of sgf attributes

        :param sgf_name: str
        :return: h5py.attributes
        >>> l = Library(doctest_dir, doctest_file).sgf_attributes('chap116.sgf')
        >>> l['EV'], l['PB'], l['PW'], l['SZ'], l['KM'], l['RE']
        ('22nd Meijin League', 'Rin Kaiho', 'Yoda Norimoto', '19', '5.50', 'W+0.50')
        """
        return self[sgf_name].attrs

    def sgf_position(self, sgf_name):
        """Return a Position object of sgf

        The returned position is the final state of the sgf.
        :param sgf_name: str
        :return: godata.Position
        >>> type(Library(doctest_dir, doctest_file).sgf_position('chap075.sgf'))
        <class 'godata.Position'>
        """
        sgf_data = self[sgf_name]
        try:
            size = int(sgf_data.attrs['SZ'])
        except KeyError:
            size = 19
        try:
            komi = float(sgf_data.attrs['KM'])
        except KeyError:
            komi = 6.5

        return godata.Position(moves=sgf_data, size=size, komi=komi)