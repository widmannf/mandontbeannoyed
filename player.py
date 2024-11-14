from piece import Piece
from colors import Color

class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.offset = (self.player_id-1) * 10
        self.color = Color(player_id).color
        self.pieces = [Piece(self.color, x) for x in range(0, 4)]

    def pieces_home(self):
        return sum([piece.is_home() for piece in self.pieces])

    def find_moveable_pieces(self, steps):
        occupied = [piece.position for piece in self.pieces if piece.position != -1]
        for piece in self.pieces:
            if piece.position == 0 and piece.position + steps not in occupied:
                return [piece]

        moveable_pieces = [
            piece for piece in self.pieces
            if piece.position != -1
            and (piece.position + steps) not in occupied 
            and (piece.position + steps) < 44 
        ]

        if steps == 6:
            for piece in self.pieces:
                if piece.is_home():
                    moveable_pieces.append(piece)
        return moveable_pieces
    
    def won_game(self):
        piece_positions = [piece.position for piece in self.pieces]
        if {41, 42, 43, 44}.issubset(piece_positions):
            return True
        return False