
import os
import h5py
from os import path

from thick_goban import go
from . import read


class Library():
    """SGF Library object

    >>> _doctest_library['chap075']['moves'][:10]
    array([ 72, 288, 300,  42,  59,  97,  61,  62,  80,  41])
    """
    def __init__(self, file=read.SGF_H5, direc=read.SGF_DIR,  sgf_direc=read.SGF_DIR):
        while True:
            try:
                self._library_file = h5py.File(os.path.join(direc, file), 'r')
                break
            except OSError:
                read.create_pro_hdf5(file=file, direc=direc, sgf_direc=sgf_direc)

    def __del__(self):
        """Close the h5 file"""
        self._library_file.close()

    def __getitem__(self, sgf_name):
        """Return the sgf dataset

        :param item: str
        :return: h5py.dataset
        >>> _doctest_library['chap116']
        <HDF5 group "/chap116" (3 members)>
        """
        return self._library_file[sgf_name]

    def __len__(self):
        """Return number of stored sgfs

        :return: int
        >>> len(_doctest_library)
        115
        """
        return len(self._library_file)

    def __iter__(self):
        """Return iterator over stored go games

        :return: iter
        >>> for sgf_name in _doctest_library:
        ...     print(sgf_name); break
        anime028a
        """
        return iter(self._library_file)

    def sgf_attributes(self, sgf_name):
        """Return the dictionary of sgf attributes

        :param sgf_name: str
        :return: h5py.attributes
        >>> l = _doctest_library.sgf_attributes('chap116')
        >>> l['EV'], l['PB'], l['PW'], l['SZ'], l['KM'], l['RE']
        ('22nd Meijin League', 'Rin Kaiho', 'Yoda Norimoto', '19', '5.5', 'W+0.5')
        """
        return self[sgf_name].attrs

    def sgf_position(self, sgf_name):
        """Return a Position object of sgf

        The returned position is the final state of the sgf.
        :param sgf_name: str
        :return: godata.Position
        >>> type(_doctest_library.sgf_position('chap005a'))
        <class 'thick_goban.go.Position'>
        """
        sgf_data = self[sgf_name]
        d = dict(sgf_data.attrs)
        try:
            size = int(d['SZ'])
        except KeyError:
            raise KeyError('SGF ' + sgf_name + ' has no size attribute')
        try:
            komi = float(sgf_data.attrs['KM'])
        except KeyError:
            komi = 6.5

        return go.Position(moves=sgf_data['moves'], setup=sgf_data['setup'], size=size, komi=komi)


_doctest_library = Library(file=path.join(read.TEST_DIR, 'libtests_sgf.h5'),
                           direc=read.TEST_DIR,
                           sgf_direc=read.TEST_DIR)
