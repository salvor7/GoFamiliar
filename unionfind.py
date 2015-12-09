import numpy as np

class UnionFind():
    def __init__(self, leadertype, size=None):
        self.pointers = np.array([range(size)])
        
    def __getitem__(self, elem):
        if self.pointers[elem] == elem:
            return elem
        else:
            repre = self[self.pointers[elem]]
            self.point[elem] = repre
            return repre
            
     def __iter__(self):
         return iter(self.pointers)
     
     def union(self, set1, set2):
         