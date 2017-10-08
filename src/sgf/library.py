import os
import h5py

from thick_goban import go
from . import read


class Library():
    """SGF Library object

    >>> Library(file=read.TEST_H5, direc=read.TEST_DIR, sgf_direc=read.TEST_DIR)['chap075'][:10]
    array([ 72, 288, 300,  42,  59,  97,  61,  62,  80,  41])
    """
    def __init__(self, file=read.SGF_H5, direc=read.SGF_DIR,  sgf_direc=read.SGF_DIR):
        while True:
            try:
                self._library_file = h5py.File(os.path.join(direc, file), 'r')
                break
            except OSError:
                read.create_pro_hdf5(file=file, direc=direc, sgf_direc=sgf_direc)

    def __getitem__(self, sgf_name):
        """Return the sgf dataset

        :param item: str
        :return: h5py.dataset
        >>> Library(file=read.TEST_H5, direc=read.TEST_DIR, sgf_direc=read.TEST_DIR)['chap116']
        <HDF5 dataset "chap116": shape (262,), type "<i4">
        """
        return self._library_file[sgf_name]

    def __len__(self):
        """Return number of stored sgfs

        :return: int
        >>> len(Library(file=read.TEST_H5, direc=read.TEST_DIR, sgf_direc=read.TEST_DIR))
        3
        """
        return len(self._library_file)

    def __iter__(self):
        """Return iterator over stored go games

        :return: iter
        >>> for sgf_name in Library(file=read.TEST_H5, direc=read.TEST_DIR, sgf_direc=read.TEST_DIR):
        ...     print(sgf_name)
        chap075
        chap116
        chap170a
        """
        return iter(self._library_file)

    def sgf_attributes(self, sgf_name):
        """Return the dictionary of sgf attributes

        :param sgf_name: str
        :return: h5py.attributes
        >>> l = Library(file=read.TEST_H5, direc=read.TEST_DIR, sgf_direc=read.TEST_DIR).sgf_attributes('chap116')
        >>> l['EV'], l['PB'], l['PW'], l['SZ'], l['KM'], l['RE']
        ('22nd Meijin League', 'Rin Kaiho', 'Yoda Norimoto', '19', '5.50', 'W+0.50')
        >>> l
        """
        return self[sgf_name].attrs

    def sgf_position(self, sgf_name):
        """Return a Position object of sgf

        The returned position is the final state of the sgf.
        :param sgf_name: str
        :return: godata.Position
        >>> type(Library(file=read.TEST_H5, direc=read.TEST_DIR, sgf_direc=read.TEST_DIR).sgf_position('chap075'))
        <class 'go.Position'>
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

        return go.Position(moves=sgf_data, size=size, komi=komi)
