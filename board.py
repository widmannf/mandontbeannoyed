import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import numpy as np
from field import Field

class Board():
    def __init__(self, players, cell_size=50, border=10):
        self.players = players
        self.ncels = 11
        self.border = border
        self.screen_width = self.ncels*cell_size + 2*border
        self.screen_height = self.ncels*cell_size + 2*border + 50
        self.bg_color = 'oldlace'
        self.steps = 0
        self.board_fields = {}

    def init_board(self):
        pygame.display.set_caption("Man, don't be annoyed")
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.screen.fill(self.bg_color)

    def add_fields(self):
        grid = [list([] for x in range(0, self.ncels)) for y in range(0, self.ncels)]
        colors = np.genfromtxt("board_colors.csv", delimiter=",", dtype=str)
        track = np.genfromtxt("board.csv", delimiter=",", dtype=str)

        for y in range(0, self.ncels):
            for x in range(0, self.ncels):
                if colors[y][x] != '5':
                    grid[x][y] = Field(x, y, colors[y][x], track[y][x])
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
                    if piece.movable:
                        field.draw_movable_piece(self.screen, piece.color)
                    else:
                        field.draw_piece(self.screen, piece.color)
                elif piece.is_in_goal():
                    field = self.get_field(f'{player.player_id}{piece.position}')
                    if piece.movable:
                        field.draw_movable_piece(self.screen, piece.color)
                    else:
                        field.draw_piece(self.screen, piece.color)
                else:
                    field = self.get_field(f'{(player.offset + piece.position)%40}')
                    if piece.movable:
                        field.draw_movable_piece(self.screen, piece.color)
                    else:
                        field.draw_piece(self.screen, piece.color)
                piece.x = field.x
                piece.y = field.y

    def current_player(self, player):
        self.player = player

    def show_player(self):
        font = pygame.font.Font('freesansbold.ttf', 35)
        text = font.render(f'Player {self.player+1}', True, pygame.Color("black"))
        textRect = text.get_rect()
        textRect.center = (self.screen_width//4, self.screen_height-20)
        self.screen.blit(text, textRect)

    def show_roll_die(self):
        font = pygame.font.Font('freesansbold.ttf', 35)
        text = font.render(f'Click to roll die', True, pygame.Color("black"))
        textRect = text.get_rect()
        textRect.center = (self.screen_width//4 + self.screen_width//2, self.screen_height-20)
        self.screen.blit(text, textRect)

    def show_die_result(self):
        font = pygame.font.Font('freesansbold.ttf', 35)
        text = font.render(f'Rolled {self.steps}', True, pygame.Color("black"))
        textRect = text.get_rect()
        textRect.center = (self.screen_width//4 + self.screen_width//2, self.screen_height-20)
        self.screen.blit(text, textRect)

    def show_winner(self):
        text_area_rect = pygame.Rect(0, self.screen_height - 50, self.screen_width, 50)
        self.screen.fill((self.bg_color), text_area_rect)
        font = pygame.font.Font('freesansbold.ttf', 35)
        text = font.render(f'Player {self.player+1} wins!', True, pygame.Color("black"))
        textRect = text.get_rect()
        textRect.center = (self.screen_width//2, self.screen_height//2)
        self.screen.blit(text, textRect)

    def show_next_move(self):
        text_area_rect = pygame.Rect(0, self.screen_height - 50, self.screen_width, 50)
        self.screen.fill((self.bg_color), text_area_rect)
        self.show_player()

        if self.steps == 0:
            self.show_roll_die()
        else:
            self.show_die_result()

    def refresh_board(self):
        self.add_fields()
        self.show_pieces()
        self.show_next_move()
        pygame.display.flip()