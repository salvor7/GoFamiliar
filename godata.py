from unionfind import UnionFind

NEIGHBORS = {}

class Position():
    def __init__(self, size=19):
        self.board = UnionFind(size=size**2)
        self.groups = {}
        self.ko = None
        self.size = size
    
    def move(self, pt):
        if self.ko is not None:
            raise MoveError(str(pt) + 'is a ko point')

    def __iter__(self):
        return iter(self.board)