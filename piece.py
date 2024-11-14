class Piece:
    def __init__(self, color, piece_id):
        self.color = color
        self.piece_id = piece_id
        self.position = -1
        self.movable = False
        self.x = 0
        self.y = 0

    def is_home(self):
        return self.position == -1
    
    def move_piece(self, steps):
        if self.is_home():
            if steps == 6:
                self.position = 0
        else:
            self.position += steps
        return self.position

    def return_home(self):
        if not self.is_home():
            self.position = -1