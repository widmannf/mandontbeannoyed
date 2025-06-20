import gym
import numpy as np

from board import Board
from game import Game


class DbaEnv(gym.Env):
    def __init__(self, num_players=4):
        super(DbaEnv, self).__init__()
        
        # Initialize game components
        self.num_players = num_players
        self.game = Game(num_players, fast=False, autoroll=False)
        
        # Define action and observation spaces
        self.action_space = gym.spaces.Discrete(4)
        self.observation_space = gym.spaces.Box(
            low=-1, high=44, shape=(4 * num_players,), dtype=np.int32 
        )
        self.reset()

    def _get_observation(self):
        state = []
        for player in self.game.players:
            for piece in player.pieces:
                state.append(piece.position)
        return np.array(state)
    


        #     def reset(self):
        #     # Reset the game to the initial state
        #     self.board.init_board()
        #     self.current_player_id = 0
        #     return self._get_observation()

        # def step(self, action):
        #     # Apply action (move a piece)
        #     player = self.board.current_player(self.current_player_id)
        #     reward = 0
        #     done = False
        #     info = {}
            
        #     if action in range(4):  # Valid piece index
        #         piece = player.pieces[action]
        #         if piece.movable:
        #             piece.move_piece(player.steps)
        #             reward = self._calculate_reward(piece)
        #         else:
        #             reward = -1  # Penalize invalid move
        #     else:
        #         reward = -1  # Penalize invalid action
            
        #     # Check if the game has ended
        #     if player.won_game():
        #         done = True
        #         reward += 100  # Bonus for winning
            
        #     # Update turn
        #     self.current_player_id = (self.current_player_id + 1) % self.num_players
            
        #     return self._get_observation(), reward, done, info

        # def render(self, mode="human"):
        #     # Optional: Use your existing Pygame code here for visualization
        #     self.board.refresh_board()

        # def _get_observation(self):
        #     # Return the current state of the board as a flattened array
        #     state = []
        #     for player in self.board.players:
        #         for piece in player.pieces:
        #             state.append(piece.position)
        #     return np.array(state)

        # def _calculate_reward(self, piece):
        #     # Define your reward logic
        #     if piece.position == 44:  # Reached home
        #         return 10
        #     elif piece.position > 0:  # Moved forward
        #         return 1
        #     else:
        #         return 0