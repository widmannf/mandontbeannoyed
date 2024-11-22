import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import numpy as np
import time

from board import Board
from player import Player

class Game:
    def __init__(self, nplayer, fast, autoroll):
        self.nplayer = nplayer
        self.current_player_id = 0
        self.steps = 0
        self.fast = fast
        self.autoroll = autoroll
        self.init_players()

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
    
    def undisplay_movable(self, board, pieces):
        for piece in pieces:
            piece.movable = False
        board.refresh_board()

    def display_movable(self, board, pieces):
        for piece in pieces:
            piece.movable = True
        board.refresh_board()

    def find_moveable_pieces(self):
        if self.steps == 0:
            self.moveable_pieces = []
        else:
            self.moveable_pieces = self.current_player().find_moveable_pieces(self.steps)
        self.move_pieces_id = sorted([piece.piece_id for piece in self.moveable_pieces])

    def move_roll_dice(self, board):
        if self.fast or self.autoroll:
            self.steps = self.roll_dice()
            board.steps = self.steps
            board.refresh_board()
            if self.autoroll:
                time.sleep(0.5)
            return True
        else:
            while True:
                event = pygame.event.wait()
                if event.type == pygame.QUIT:
                    return False
                elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN] and not self.fast:
                    self.steps = self.roll_dice()
                    board.steps = self.steps
                    board.refresh_board()
                    time.sleep(0.3)
                    return True
                
    def move_select_piece(self):
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                return -1
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return self.find_clicked_piece(pygame.mouse.get_pos(), self.moveable_pieces)
            
    def check_hit_opponent(self):
        new_pos_abs = (self.current_player().offset + self.new_pos) % 40
        for player in self.players:
            if player.player_id == self.current_player().player_id:
                continue
            for piece in player.pieces:
                if self.new_pos < 40 and piece.position < 40 and (piece.position + player.offset) % 40 == new_pos_abs:
                    piece.return_home()
                    break

    def move_piece(self, board):
        if self.fast:
            self.moveable_pieces = self.moveable_pieces[:1]
        moved = False

        # no moveable pieces
        if len(self.moveable_pieces) == 0:
            if not self.fast: time.sleep(1)
        
        # only one moveable piece
        elif len(self.moveable_pieces) == 1:
            if not self.fast: time.sleep(0.3)
            self.new_pos = self.moveable_pieces[0].move_piece(self.steps)
            moved = True

        # all moveable pieces are home
        elif all(p == -1 for p in [p.position for p in self.moveable_pieces]):
            if not self.fast: time.sleep(0.3)
            self.new_pos = self.moveable_pieces[-1].move_piece(self.steps)
            moved = True

        # multiple moveable pieces
        else:
            self.display_movable(board, self.moveable_pieces)
            piece = self.move_select_piece()
            if piece == -1:
                return False
            self.new_pos = piece.move_piece(self.steps)
            moved = True
            self.undisplay_movable(board, self.moveable_pieces)
        return moved


    # For the game to be compatible with OpenAI Gym, we need to define the following:
    """
    States: Board representation, dice roll, current player, etc.
    Actions: Choosing which piece to move (discrete actions: [0, 1, 2, 3]).
    Rewards: Based on game progress (e.g., advancing to home, capturing opponent pieces).
    Step Function: Executes an action, updates the board, checks for terminal conditions, and returns the new state and reward.
    Reset Function: Resets the board for a new game.
    """
    def get_state(self):
        pos = [[piece.position for piece in player.pieces] for player in self.players]
        cur_player = self.current_player().player_id
        die = self.steps
        self.find_moveable_pieces()
        return pos, cur_player, die, self.move_pieces_id, self.winner

    def run_game(self):
        pygame.init()
        board = Board(self.players)
        board.init_board()

        running = True
        self.winner = 0
        while running:
            board.current_player(self.current_player_id)
            board.refresh_board()

            print(f'Roll dice, state: {self.get_state()}')
            if not self.move_roll_dice(board):
                running = False

            self.find_moveable_pieces()

            print(f'Move piece, state: {self.get_state()}')
            moved = self.move_piece(board)
            if moved:
                self.check_hit_opponent()
                board.refresh_board()

            if not self.current_player().won_game():
                if self.steps != 6 or not moved:
                    self.next_player(board)
                else:
                    self.steps = 0
            board.refresh_board()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if self.current_player().won_game():
                self.winner = self.current_player().player_id
                running = False

        if self.winner != 0:
            board.show_winner()
            game_over = True
            while game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_over = False
            pygame.quit()

    pygame.quit()

