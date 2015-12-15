import numpy as np

class UnionFind():
    def __init__(self, size_limit=0):
        self._pointers = np.array(range(size_limit), dtype=np.int32)
        self.size_limit = size_limit

    def __getitem__(self, elem):
        try:
            self._pointers[elem]
        except KeyError:
            if self.size_limit is not 0 and elem > self.size_limit:
                raise KeyError(str(elem) + ' is not in domain of union')
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

    def union(self, pt1, pt2):
        self._pointers[self[pt2]] = self[pt1]

    def multi_union(self, pt_iter):
        pt1 = next(pt_iter)
        for pt_n in pt_iter:
            self.union(pt1, pt_n)

