import numpy as np

class UnionFind():
    def __init__(self, size_limit=0):
        self.pointers = np.array(range(size_limit), dtype=np.int16)
        self.size_limit = size_limit

    def __getitem__(self, elem):
        try:
            self.pointers[elem]
        except KeyError:
            if self.size_limit is not 0 and elem > self.size_limit:
                raise KeyError(str(elem) + ' is not in domain of union')
            new_points = range(len(self), elem + 1)
            np.append(self.pointers, new_points)
        if self.pointers[elem] == elem:
            repre = elem
        else:
            repre = self.__getitem__(self.pointers[elem])
            self.pointers[elem] = repre
        return repre

    def __iter__(self):
        return iter(self.pointers)

    def __len__(self):
        return len(self.pointers)

    def union(self, repre1, repre2):
        self.pointers[repre2] = repre1

    def multi_union(self, repre_iter):
        repre1 = next(repre_iter)
        for repre_n in repre_iter:
            self.union(repre1, repre_n)

