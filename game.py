import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import numpy as np
import time

from board import Board
from player import Player

class Game:
    def __init__(self, nplayer):
        self.nplayer = nplayer
        self.current_player_id = 0
        self.steps = 0
        self.init_players()
        self.run_game()

    def init_players(self):
        if self.nplayer == 2:
            self.players = [Player(1), Player(3)]
        else:
            self.players = [Player(i) for i in range(1, self.nplayer+1)]

    def current_player(self):
        return self.players[self.current_player_id]
    
    def next_player(self, board):
        self.steps = 0
        board.steps = self.steps
        self.current_player_id = (self.current_player_id + 1) % len(self.players)
        board.current_player(self.current_player_id)
        board.refresh_board()

    def roll_dice(self):
        return np.random.randint(1, 7)
    
    def calculate_distance(self, mouse_pos, piece_pos):
        dx = mouse_pos[0] - piece_pos[0]
        dy = mouse_pos[1] - piece_pos[1]
        return np.sqrt((dx ** 2 + dy ** 2))
    
    def find_clicked_piece(self, mouse_pos, moveable_pieces):
        mouse_pos = [(pos-10)/50-0.5 for pos in pygame.mouse.get_pos()]
        dist = [self.calculate_distance(mouse_pos, [p.x, p.y]) for p in moveable_pieces]
        piece = moveable_pieces[np.argmin(dist)]
        return piece
    
    def unset_movable(self, board, pieces):
        for piece in pieces:
            piece.movable = False
        board.refresh_board()

    def set_movable(self, board, pieces):
        for piece in pieces:
            piece.movable = True
        board.refresh_board()

    
        
    def next_action(self, board):
        if self.steps == 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                    self.steps = self.roll_dice()
                    board.steps = self.steps
                    board.refresh_board()
                    time.sleep(0.3)
        else:
            moveable_pieces = self.current_player().find_moveable_pieces(self.steps)
            moved = False
            if len(moveable_pieces) == 0:
                time.sleep(1)
            
            elif len(moveable_pieces) == 1:
                time.sleep(0.3)
                new_pos = moveable_pieces[0].move_piece(self.steps)
                moved = True

            elif self.current_player().pieces_home() == 4:
                time.sleep(0.3)
                new_pos = moveable_pieces[-1].move_piece(self.steps)
                moved = True

            else:
                self.set_movable(board, moveable_pieces)
                waiting_for_click = True
                while waiting_for_click:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return False
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            piece = self.find_clicked_piece(pygame.mouse.get_pos(), moveable_pieces)
                            new_pos = piece.move_piece(self.steps)
                            self.unset_movable(board, moveable_pieces)                            
                            waiting_for_click = False
                            moved = True

            if moved:
                new_pos_abs = (self.current_player().offset + new_pos) % 40
                for player in self.players:
                    if player.player_id == self.current_player().player_id:
                        continue
                    for piece in player.pieces:
                        if (piece.position + player.offset) % 40 == new_pos_abs:
                            piece.return_home()
                            board.refresh_board()
                            break

            if self.steps != 6:
                self.next_player(board)
            else:
                self.steps = 0
            board.refresh_board()
        return True

    #TODO: kick other pieces out
    #TODO: win condition
    def run_game(self):
        pygame.init()

        board = Board(self.players)
        board.init_board()
        # board.refresh_board()

        running = True
        while running:
            board.current_player(self.current_player_id)
            board.refresh_board()

            if not self.next_action(board):
                running = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False


        pygame.quit()