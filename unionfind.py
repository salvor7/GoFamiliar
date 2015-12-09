import numpy as np

class UnionFind():
    def __init__(self, size=None):
        self.pointers = np.array([range(size)])
        
    def __getitem__(self, elem):
        if self.pointers[elem] == elem:
            return elem
        else:
            repre = self.__getitem__(self.pointers[elem])
            self.pointers[elem] = repre
            return repre
            
     def __iter__(self):
         return iter(self.pointers)
     
     def union(self, repre1, repre2):
         self.pointers[repre2] = repre1
         
     def multi_union(self, repre_iter):
         repre1 = next(repre_iter)
         for repre_n in repre_iter:
             self.union(repre1, repre_n)