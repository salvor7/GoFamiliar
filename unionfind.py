import numpy as np

class UnionFind():
    def __init__(self):
        self.pointers = np.array([])

    def __getitem__(self, elem):
        try:
            self.pointers[elem]
        except KeyError:
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
        return len(self.piinters)

    def union(self, repre1, repre2):
        self.pointers[repre2] = repre1

    def multi_union(self, repre_iter):
        repre1 = next(repre_iter)
        for repre_n in repre_iter:
            self.union(repre1, repre_n)