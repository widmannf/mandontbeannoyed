import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from colors import Color

class Field():
    def __init__(self, x, y, color_id, id, cell_size=50, piece_size=40, border=10):
        self.x = x
        self.y = y
        self.color = Color(int(color_id)).color
        self.id = id
        self.cell_size = cell_size
        self.piece_size = piece_size
        self.border = border

    def draw_field(self, screen):
        x = self.x * self.cell_size + self.cell_size//2 + self.border
        y = self.y * self.cell_size + self.cell_size//2 + self.border
        pygame.draw.circle(screen, self.color, (x, y), self.cell_size//2-2, width=0)
        pygame.draw.circle(screen, 'black', (x, y), self.cell_size//2-2, width=2)

    def draw_piece(self, screen, color):
        x = self.x * self.cell_size + self.cell_size//2 + self.border
        y = self.y * self.cell_size + self.cell_size//2 + self.border
        pygame.draw.circle(screen, color, (x, y), self.piece_size//2-2, width=0)
        pygame.draw.circle(screen, 'black', (x, y), self.piece_size//2-2, width=7)

    def draw_movable_piece(self, screen, color):
        x = self.x * self.cell_size + self.cell_size//2 + self.border
        y = self.y * self.cell_size + self.cell_size//2 + self.border
        pygame.draw.circle(screen, color, (x, y), self.piece_size//2-2, width=0)
        pygame.draw.circle(screen, 'red', (x, y), self.piece_size//2+2, width=7)
