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

    def _center(self):
        x = self.x * self.cell_size + self.cell_size // 2 + self.border
        y = self.y * self.cell_size + self.cell_size // 2 + self.border
        return x, y

    def draw_field(self, screen):
        x, y = self._center()
        pygame.draw.circle(screen, self.color, (x, y), self.cell_size // 2 - 2, width=0)
        pygame.draw.circle(screen, (40, 40, 40), (x, y), self.cell_size // 2 - 2, width=2)

    def _draw_with_number(self, screen, color, number, outline_color, outline_width):
        x, y = self._center()
        r = self.piece_size // 2 - 2
        pygame.draw.circle(screen, color, (x, y), r, width=0)
        pygame.draw.circle(screen, outline_color, (x, y), r, width=outline_width)
        if number:
            font = pygame.font.Font(None, 18)
            text = font.render(str(number), True, (255, 255, 255))
            text_rect = text.get_rect(center=(x, y))
            screen.blit(text, text_rect)

    def draw_piece(self, screen, color, number=None):
        self._draw_with_number(screen, color, number, (40, 40, 40), 7)

    def draw_movable_piece(self, screen, color, number=None):
        self._draw_with_number(screen, color, number, 'red', 7)