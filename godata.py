NEIGHBORS = {}

class Position():
    def __init__(self, size=19):
        self.board = self.new_board()
        self.ko = None
        self.size = size
        
    def new_board():
        return []
        