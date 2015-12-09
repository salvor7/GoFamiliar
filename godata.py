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