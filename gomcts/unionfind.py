import numpy as np

class UnionFind():
    def __init__(self, size_limit=0):
        self._pointers = np.array(range(size_limit), dtype=np.int32)
    def __init__(self, size_limit=np.infty):
        self.size_limit = size_limit
        if size_limit is np.infty:
            limit = 0
        else:
            limit = size_limit
        self._pointers = np.array(range(limit), dtype=np.int32)


    def __getitem__(self, elem):
        try:
            self._pointers[elem]
        except KeyError:
            if elem > self.size_limit:
                raise KeyError(str(elem) + ' is not in range')
            new_points = range(len(self), elem + 1)
            np.append(self._pointers, new_points)
        if self._pointers[elem] == elem:
            repre = elem
        else:
            repre = self.__getitem__(self._pointers[elem])
            self._pointers[elem] = repre #update step
        return repre

    def __iter__(self):
        return iter(self._pointers)

    def __len__(self):
        return len(self._pointers)

    def __setitem__(self, elements, target):
        """Union of target and all elements together

        This implements the union function of Union Find data structure.
        It also exploits some of numpy.arrays advanced slicing to allow for multi unioning.
        :param elements: [ints]
        :param target: int

        >>> uf = UnionFind()
        >>> uf[6] = 100
        >>> uf[6]
        100

        It also exploits some of numpy.arrays advanced slicing to allow for multi unioning.
        >>> uf[[1,2,100]] = 101
        >>> uf[1,2,6,100]
        [101, 101, 101, 101]
        """
        element_repres = [self[elem] for elem in elements]
        target_repre = self[target]
        self._pointers.__setitem__(element_repres, target_repre)


