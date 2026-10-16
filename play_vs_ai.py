import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ.setdefault('CUDA_VISIBLE_DEVICES', '')

import argparse
from pathlib import Path
import time
import numpy as np
import pygame
import tensorflow as tf

from engine import Engine
from board import Board
from player import Player as GPlayer


def make_display_players(engine):
    if engine.num_players == 2:
        ids = [1, 3]
    else:
        ids = list(range(1, engine.num_players + 1))
    return [GPlayer(i) for i in ids]


def sync_display(display_players, engine):
    for i, p in enumerate(display_players):
        for j, piece in enumerate(p.pieces):
            piece.position = engine.positions[i][j]


def build_obs(engine, agent, die, opts):
    obs = []
    for owner in range(engine.num_players):
        for pos in engine.positions[owner]:
            if pos == -1:
                obs.append(-1.0)
            elif pos >= 40:
                obs.append(44.0)
            else:
                obs.append(float((pos + engine.offsets[owner] - engine.offsets[agent]) % 40))
    obs.append(float(die))
    obs.append(float(engine.current))
    for i in range(4):
        obs.append(1.0 if i in opts else 0.0)
    return np.array(obs, dtype=np.float32)


def main():
    parser = argparse.ArgumentParser(description='Play against a trained DQN agent.')
    parser.add_argument('--model', default=str(Path(__file__).parent / 'dqn_model'), help='Path to saved Keras model')
    parser.add_argument('--ai-first', action='store_true', help='AI goes first')
    args = parser.parse_args()

    print('Loading DQN model...')
    model = tf.keras.models.load_model(args.model)

    agent = 1 if args.ai_first else 0
    ai = 1 - agent

    engine = Engine(2)
    display_players = make_display_players(engine)

    pygame.init()
    board = Board(display_players, panel_height=70)
    board.player_labels = ['You', 'AI']
    board.init_board()

    engine.reset()
    engine.current = agent
    sync_display(display_players, engine)
    board.current_player(engine.current)
    board.refresh_board()

    running = True
    while running:
        sync_display(display_players, engine)
        board.current_player(engine.current)
        board.refresh_board()

        if engine.current == agent:
            board.steps = 0
            board.status_message = 'Click or press any key to roll the die'
            board.refresh_board()

            print()
            print('=== Your turn ===')

            ev = pygame.event.wait()
            if ev.type == pygame.QUIT:
                break

            die = engine.roll()
            board.steps = die
            board.refresh_board()

            opts = engine.move_options(engine.current, die)
            if not opts:
                print(f'  Rolled {die}. No moves available.')
                board.status_message = 'No moves available'
                board.refresh_board()
                time.sleep(0.8)
                engine.next_player()
                continue

            sync_display(display_players, engine)
            moveable = [display_players[engine.current].pieces[i] for i in opts]
            for p in moveable:
                p.movable = True

            hint = f'Rolled {die}. Pick piece: click it or press 1-4'
            board.status_message = hint
            board.refresh_board()
            print(f'  Rolled {die}. Your moveable pieces: {[i + 1 for i in opts]}')

            chosen = None
            while chosen is None and running:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        running = False
                        chosen = -1
                    elif ev.type == pygame.KEYDOWN:
                        if ev.unicode in ('1', '2', '3', '4'):
                            idx = int(ev.unicode) - 1
                            if idx in opts:
                                chosen = idx
                    elif ev.type == pygame.MOUSEBUTTONDOWN:
                        mp = [(p - 10) / 50 - 0.5 for p in ev.pos]
                        best = min(moveable, key=lambda p: (mp[0] - p.x) ** 2 + (mp[1] - p.y) ** 2)
                        if best.piece_id in opts:
                            chosen = best.piece_id
            if not running:
                break

            for p in moveable:
                p.movable = False

            _, _, hits = engine.apply_move(engine.current, chosen, die)
            sync_display(display_players, engine)
            if hits:
                board.status_message = 'Hit! Opponent piece sent home!'
            else:
                board.status_message = ''
            board.refresh_board()

            if hits:
                print('  Hit! Opponent piece sent home!')
                time.sleep(0.6)
        else:
            die = engine.roll()
            board.steps = die
            board.status_message = "AI's turn..."
            sync_display(display_players, engine)
            board.refresh_board()
            time.sleep(0.5)

            opts = engine.move_options(engine.current, die)
            if not opts:
                board.status_message = 'AI has no moves'
                board.refresh_board()
                time.sleep(0.5)
                engine.next_player()
                continue

            obs = build_obs(engine, agent, die, opts)
            q = model(obs[np.newaxis], training=False).numpy()[0]
            masked = np.full(4, -1e9)
            masked[opts] = q[opts]
            action = int(np.argmax(masked))
            print(f'  AI rolled {die}, moves piece {action + 1}.')

            _, _, hits = engine.apply_move(engine.current, action, die)
            sync_display(display_players, engine)
            if hits:
                board.status_message = 'AI hit one of your pieces!'
            else:
                board.status_message = ''
            board.refresh_board()
            time.sleep(0.8)

        if engine.winner is not None:
            sync_display(display_players, engine)
            board.current_player(engine.winner)
            board.status_message = ''
            board.show_winner()
            if engine.winner == agent:
                print()
                print('You win!')
            else:
                print()
                print('AI wins! Better luck next time.')
            time.sleep(4)
            break

        if die != 6:
            engine.next_player()

    pygame.quit()


if __name__ == '__main__':
    main()