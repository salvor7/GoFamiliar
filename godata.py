from unionfind import UnionFind


class Board():

    def __init__(self, size):
        self.points = UnionFind()
        self.pounts[size**2 - 1]
        self.groups = {}
        
    def __iter__(self):
        return iter(self.points)
    
    def move(self):
        
    
NEIGHBORS = {}

class Position():
    def __init__(self, size=19):
        self.board = [i for i in range(size**2)]
        self.ko = None
        self.size = size
    
    def move(self, c):
        if self.ko is not None:
            raise MoveError(str(c) + 'is a ko point')
        [NEIGHBORS[c]]