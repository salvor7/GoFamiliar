"""Implementation of UnionFind data structure.

Created for the GoFamiliar project, this module should be general enough for other uses.
"""
import numpy as np

class UnionFind():
    """Union Find data structure implementation

    Tracks groups and their unions over time as a list of integers acting as pointers to
    positions in the list. A graphical forest results, where each union is a tree.
    https://en.wikipedia.org/wiki/Disjoint-set_data_structure

    Initially, every points is a graph tree pointing to itself:
    >>> uf = UnionFind()
    >>> uf[100]
    100

    A union changes the pointers.
    >>> uf[101] = 100
    >>> uf[100] == uf[101]
    True
    """
    def __init__(self, size_limit=np.infty):
        """Initialize a union find structure

        :param size_limit: int

        If no size_limit is set, the element list is empty, and the element list will grow
        as required adding elements to answer queries.
        Here, items were added to 1000, and they all initially point to themselves.
        >>> UnionFind()[1000]
        1000

        With a size_limit, the pointers list is fully created with size_limit length.
        >>> len(UnionFind(size_limit=10))
        10
        """
        self.size_limit = size_limit
        if size_limit is np.infty:
            limit = 0
            self._pointers = list(range(limit))
        else:
            limit = size_limit

            pow2 = int(np.ceil(np.log2(np.log2(limit))))
            dtypes = [np.uint8,]*4 + [np.uint16, np.uint32, np.uint64]
            self._pointers = list(range(limit)) #np.array(range(limit), dtype=dtypes[pow2]) #

    def __getitem__(self, elem):
        """Find group representative

        :param elem: int
        :return: int

        This is the implementation of the find function of the Union Find data structure.
        Recursively follows pointers till finding an element pointing to itself, which is
        the union representative.

        A chain of pointers is updated to point directly to the representative.
        This flattens the pointer tree to keep the time complexity of Find low.

        If the element is past the end of the underlying list and there is no size_limit,
        the list is extended with elements pointing to themselves.

        The find function is implemented as Pythonic object indexing.
        >>> uf = UnionFind()
        >>> uf[100]
        100
        """
        try:
            points_to_self = (self._pointers[elem] == elem)
        except IndexError:
            if self.size_limit is np.infty and elem > 0:
                new_points = list(range(len(self), elem + 1))
                self._pointers += new_points
                points_to_self = (self._pointers[elem] == elem)
            else:
                raise IndexError(str(elem) + ' is not a point')

        if points_to_self:
            repre = elem
        else:
            repre = self.__getitem__(self._pointers[elem])
            self._pointers[elem] = repre        #update pointers
        return repre

    def __iter__(self):
        """Iterator over the point indices

        :return: iter

        >>> for elem in UnionFind(size_limit=100):
        ...     pass
        """
        return iter(range(len(self)))

    def __len__(self):
        """Returns len of underlying pointer list

        :return: int

        >>> len(UnionFind(size_limit=100))
        100
        """
        return len(self._pointers)

    def __setitem__(self, elem, target):
        """Add elem's union to target's union

        :param elem: int
        :param target: int

        This implements the union function of Union Find data structure.
        Setting the element (eg 6) determines the group (eg 100).
        >>> uf = UnionFind()
        >>> uf[6] = 100
        >>> uf[6]
        100
        """
        old_set_repre = self[elem]
        new_set_repre = self[target]
        self._pointers[old_set_repre] = new_set_repre
