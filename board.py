import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import numpy as np
from field import Field


_DIE_DOTS = {
    1: [(0, 0)],
    2: [(-1, -1), (1, 1)],
    3: [(-1, -1), (0, 0), (1, 1)],
    4: [(-1, -1), (-1, 1), (1, -1), (1, 1)],
    5: [(-1, -1), (-1, 1), (0, 0), (1, -1), (1, 1)],
    6: [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1)],
}

class Board():
    def __init__(self, players, cell_size=50, border=10, panel_height=70):
        self.players = players
        self.ncels = 11
        self.border = border
        self.cell_size = cell_size
        self.panel_height = panel_height
        self.screen_width = self.ncels*cell_size + 2*border
        self.screen_height = self.ncels*cell_size + 2*border + panel_height
        self.bg_color = 'oldlace'
        self.steps = 0
        self.board_fields = {}
        self.player_labels = None
        self.status_message = ''

    def init_board(self):
        pygame.display.set_caption("Man, don't be annoyed vs AI")
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.screen.fill(self.bg_color)

    def add_fields(self):
        grid = [list([] for x in range(0, self.ncels)) for y in range(0, self.ncels)]
        basedir = os.path.dirname(os.path.abspath(__file__))
        colors = np.genfromtxt(os.path.join(basedir, "board_colors.csv"), delimiter=",", dtype=str)
        track = np.genfromtxt(os.path.join(basedir, "board.csv"), delimiter=",", dtype=str)

        for y in range(0, self.ncels):
            for x in range(0, self.ncels):
                if colors[y][x] != '5':
                    grid[x][y] = Field(x, y, colors[y][x], track[y][x], self.cell_size)
                    grid[x][y].draw_field(self.screen)
                    self.board_fields[track[y][x].lstrip()] = grid[x][y]
        return grid

    def get_field(self, field_id):
        return self.board_fields[field_id]

    def show_pieces(self):
        for player in self.players:
            for piece in player.pieces:
                if piece.is_home():
                    field = self.get_field(f'H{player.player_id}{piece.piece_id}')
                elif piece.is_in_goal():
                    field = self.get_field(f'{player.player_id}{piece.position}')
                else:
                    field = self.get_field(f'{(player.offset + piece.position)%40}')
                if piece.movable:
                    field.draw_movable_piece(self.screen, piece.color, piece.piece_id + 1)
                else:
                    field.draw_piece(self.screen, piece.color, piece.piece_id + 1)
                piece.x = field.x
                piece.y = field.y

    def current_player(self, player):
        self.player = player

    def draw_die(self, value, center, size=44):
        x, y = center
        rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
        pygame.draw.rect(self.screen, (250, 250, 250), rect, border_radius=6)
        pygame.draw.rect(self.screen, (40, 40, 40), rect, width=2, border_radius=6)
        r = size // 10
        gap = size // 5
        for dx, dy in _DIE_DOTS.get(value, []):
            pygame.draw.circle(self.screen, (30, 30, 30), (x + dx * gap, y + dy * gap), r)

    def _draw_player_badge(self, cx, cy, player_idx):
        color = self.players[player_idx].color if player_idx < len(self.players) else 'black'
        label = self.player_labels[player_idx] if self.player_labels else f'P{player_idx + 1}'
        badge_r = 14
        pygame.draw.circle(self.screen, color, (cx, cy), badge_r)
        pygame.draw.circle(self.screen, (40, 40, 40), (cx, cy), badge_r, 2)
        font = pygame.font.Font(None, 22)
        text = font.render(label, True, (0, 0, 0))
        text_rect = text.get_rect(midleft=(cx + badge_r + 10, cy))
        self.screen.blit(text, text_rect)

    def show_player(self):
        cx = self.screen_width // 4
        cy = self.screen_height - self.panel_height // 2 - 8
        self._draw_player_badge(cx - 40, cy, self.player)

    def show_status_message(self):
        if not self.status_message:
            return
        font = pygame.font.Font(None, 24)
        text = font.render(self.status_message, True, (80, 80, 80))
        text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height - 12))
        self.screen.blit(text, text_rect)

    def show_roll_die(self):
        cx = 3 * self.screen_width // 4
        cy = self.screen_height - self.panel_height // 2 - 8
        self.draw_die(0, (cx, cy))

    def show_die_result(self):
        cx = 3 * self.screen_width // 4
        cy = self.screen_height - self.panel_height // 2 - 8
        self.draw_die(self.steps, (cx, cy))

    def show_winner(self):
        text_area_rect = pygame.Rect(0, self.screen_height - self.panel_height, self.screen_width, self.panel_height)
        self.screen.fill((self.bg_color), text_area_rect)
        font = pygame.font.Font(None, 40)
        label = self.player_labels[self.player] if self.player_labels else f'Player {self.player + 1}'
        verb = 'win' if label == 'You' else 'wins'
        text = font.render(f'{label} {verb}!', True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height - self.panel_height // 2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()

    def show_next_move(self):
        text_area_rect = pygame.Rect(0, self.screen_height - self.panel_height, self.screen_width, self.panel_height)
        self.screen.fill((self.bg_color), text_area_rect)
        pygame.draw.line(self.screen, (180, 180, 180),
                         (0, self.screen_height - self.panel_height),
                         (self.screen_width, self.screen_height - self.panel_height), 1)
        self.show_player()
        self.show_status_message()
        if self.steps == 0:
            self.show_roll_die()
        else:
            self.show_die_result()

    def refresh_board(self):
        self.add_fields()
        self.show_pieces()
        self.show_next_move()
        pygame.display.flip()