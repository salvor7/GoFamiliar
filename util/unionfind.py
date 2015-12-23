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
    >>> uf.union(100, 101)
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
        else:
            limit = size_limit
        self._pointers = np.array(range(limit), dtype=np.int32)


    def __getitem__(self, elem):
        """Find elem group

        :param elem: int
        :return: int

        This is the implementation of the find function of the Union Find data structure.
        Recursively follows pointers till finding an element pointing to itself, which is
        the union representative.
        A chain of pointers is updated to point directly to the representative.
        If elem is past the end of the underlying list and there is no size_limit,
        the list is extended with elements pointing to themselves.

        The find function is implemented as Pythonic object indexing.
        >>> uf = UnionFind()
        >>> uf[100]
        100

        Getitem also supports some numpy.array slicing.
        >>> uf[[1,10,100, 1000]]
        [1,10, 100, 1000]
        """
        try:
            points_to_self = self._pointers[elem] == elem
        except IndexError:
            if elem > self.size_limit:
                raise KeyError(str(elem) + ' is not in range')
            new_points = range(len(self), elem + 1)
            self._pointers = np.append(self._pointers, new_points)
            points_to_self = (self._pointers[elem] == elem)
        if points_to_self:
            repre = elem
        else:
            repre = self.__getitem__(self._pointers[elem])
            self._pointers[elem] = repre #update pointers
        return repre

    def __iter__(self):
        """Iterator over the underlying pointer list

        :return: iter

        >>> for elem in UnionFind(size_limit=100):
        ...     pass
        """
        return iter(self._pointers)

    def __len__(self):
        """Returns len of underlying pointer list

        :return: int

        >>> len(UnionFind(size_limit=100))
        100
        """
        return len(self._pointers)

    def __setitem__(self, elements, target):
        """Union of target and all elements together

        :param elements: [ints]
        :param target: int

        This implements the union function of Union Find data structure.
        Setting the element determines the group.
        >>> uf = UnionFind()
        >>> uf[6] = 100
        >>> uf[6]
        100

        numpy.arrays advanced slicing allows for multiple unions at once.
        >>> uf[[1,2,100]] = 101
        >>> uf[1,2,6,100]
        [101, 101, 101, 101]
        """
        element_repres = [self[elem] for elem in elements]
        target_repre = self[target]
        self._pointers.__setitem__(element_repres, target_repre)


