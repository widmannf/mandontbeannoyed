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


def build_obs(engine, die, opts, player):
    obs = []
    for owner in range(engine.num_players):
        for pos in engine.positions[owner]:
            if pos == -1:
                obs.append(-1.0)
            elif pos >= 40:
                obs.append(44.0)
            else:
                obs.append(float((pos + engine.offsets[owner] - engine.offsets[player]) % 40))
    obs.append(float(die))
    obs.append(float(engine.current))
    for i in range(4):
        obs.append(1.0 if i in opts else 0.0)
    return np.array(obs, dtype=np.float32)


def _sleep(secs):
    now = time.monotonic()
    end = now + secs
    while now < end:
        pygame.event.pump()
        remaining = end - now
        time.sleep(min(0.05, remaining))
        now = time.monotonic()


def run_vs_ai(ai_first=False, model_path=None, fast=False, autoroll=False, num_players=2):
    if model_path is None:
        model_path = str(Path(__file__).parent / 'dqn_model')
    model = tf.keras.models.load_model(model_path)

    agent = 0
    if ai_first:
        agent = 1 if num_players == 2 else (num_players - 1)

    engine = Engine(num_players)
    display_players = make_display_players(engine)

    pygame.init()
    board = Board(display_players, panel_height=70)
    labels = ['You'] + ['AI'] * (num_players - 1)
    if ai_first:
        labels = ['AI'] + ['You'] + ['AI'] * (num_players - 2)
    if ai_first and num_players == 2:
        labels = ['AI', 'You']
    board.player_labels = labels
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
            if autoroll:
                board.status_message = 'Rolling...'
                board.refresh_board()
                _sleep(0.6)
            else:
                board.status_message = 'Click or press any key to roll the die'
                board.refresh_board()

                while True:
                    ev = pygame.event.wait()
                    if ev.type == pygame.QUIT:
                        running = False
                        break
                    if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                        break
                if not running:
                    break

            die = engine.roll()
            board.steps = die
            board.refresh_board()

            opts = engine.move_options(engine.current, die)
            if not opts:
                board.status_message = 'No moves available'
                board.refresh_board()
                _sleep(0.8)
                engine.next_player()
                continue

            sync_display(display_players, engine)
            moveable = [display_players[engine.current].pieces[i] for i in opts]
            for p in moveable:
                p.movable = True

            if fast and len(opts) == 1:
                chosen = opts[0]
                for p in moveable:
                    p.movable = False
                board.status_message = f'Rolled {die}, moving piece {chosen + 1}'
                board.refresh_board()
                _sleep(0.4)
            else:
                hint = f'Rolled {die}. Pick piece: click it or press 1-4'
                board.status_message = hint
                board.refresh_board()

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
        else:
            die = engine.roll()
            board.steps = die
            board.status_message = f"{labels[engine.current]}'s turn..."
            sync_display(display_players, engine)
            board.refresh_board()
            _sleep(0.5)

            opts = engine.move_options(engine.current, die)
            if not opts:
                board.status_message = f'{labels[engine.current]} has no moves'
                board.refresh_board()
                _sleep(0.5)
                engine.next_player()
                continue

            obs = build_obs(engine, die, opts, engine.current)
            q = model(obs[np.newaxis], training=False).numpy()[0]
            masked = np.full(4, -1e9)
            masked[opts] = q[opts]
            action = int(np.argmax(masked))

            _, _, hits = engine.apply_move(engine.current, action, die)
            sync_display(display_players, engine)
            if hits:
                board.status_message = f'{labels[engine.current]} hit one of your pieces!'
            else:
                board.status_message = ''
            board.refresh_board()
            _sleep(0.8)

        if engine.winner is not None:
            sync_display(display_players, engine)
            board.current_player(engine.winner)
            board.status_message = ''
            board.show_winner()
            _sleep(4)
            break

        if die != 6:
            engine.next_player()

    pygame.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Play against a trained DQN agent.')
    parser.add_argument('--model', default=None, help='Path to saved Keras model')
    parser.add_argument('--ai-first', action='store_true', help='AI goes first')
    parser.add_argument('--players', type=int, default=2, choices=[2, 3, 4],
                        help='Number of players (you vs N-1 AI opponents)')
    parser.add_argument('--fast', action='store_true', help='Fast AI moves')
    parser.add_argument('--autoroll', action='store_true', help='Auto-roll the die')
    args = parser.parse_args()

    model_path = args.model
    if model_path is None:
        model_path = str(Path(__file__).parent / f'dqn_model_{args.players}p')
        if args.players == 2:
            model_path = str(Path(__file__).parent / 'dqn_model')

    run_vs_ai(ai_first=args.ai_first, model_path=model_path,
              fast=args.fast, autoroll=args.autoroll, num_players=args.players)