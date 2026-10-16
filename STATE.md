# Project State (2026-10-16)

Goal: train an RL agent (DQN) to play "Mensch ärger dich nicht" (Ludo). The old
`dba_gym.py` was broken (reset/step commented out), so nothing could train.

## Files

- `engine.py` (NEW) - pure game logic, no pygame. `Engine` with `positions`
  (per-player list of 4 piece positions: `-1` = home, `0-39` = track, `40-43` =
  goal), `move_options(player, die)`, `apply_move()`, `has_won()`. Faithful to
  original rules incl. forced move (piece on first field must move) and 6 =
  roll again if you moved.
- `dba_gym.py` (REWRITTEN) - `DbaEnv`, a *decision-level* env. It auto-plays
  non-decision rolls and all opponent turns internally (opponents use a
  heuristic: prefer captures, else advance front-most piece). Only exposes a
  decision when the agent has >= 1 legal move.
  - Action: piece id 0-3 (must be in `env.options`).
  - Obs: all pieces (relative frame), die (1-6), current player, 4-entry
    0/1 mask of which of your pieces may move (last 4 entries).
  - Rewards: win +100, capture +15, being captured -15, leave home +5,
    enter goal corridor +10, corridor deepen +1.
- `train_dqn.py` (NEW) - double-DQN, TF/Keras (torch NOT installed; tf 2.15 is).
  Replay buffer, soft target update, option masking, compiled tf.function
  update step, `--update-every 2`. Saves best model to `dqn_model/`.
  CPU only by default (`CUDA_VISIBLE_DEVICES` unset -> "").
- `README.md` - added "Train an AI" section.
- `.gitignore` - added `dqn_model/`, `__pycache__/`.

## Bugs found & fixed

1. **Replay sampling was quadratic**: `rng.sample(list(buf), batch)` copied the
   whole 100k replay buffer every step. Fixed to sample indices
   (`rng.sample(range(len(buf)), batch)`).
2. **Eager training too slow**: compiled the update into a `tf.function`.
   Benchmark: ~470 eps/min (greedy) on CPU.
3. **`reset()` could return a dead state**: if the opponent got a lucky run of
   6s and the agent rolled no usable die, the game could finish inside
   `reset()`'s auto-advance, leaving `options=[]` -> `rng.choice([])` crash.
   Fixed: `reset()` loops until `_advance()` ends on a live agent decision.

## Training results

10k episodes for each config, eval every 1k episodes (300 eval games), 2-player
vs heuristic opponent. Heuristic-first baseline: ~42.80%.

| Config | Best win rate | Notes |
|--------|--------------|-------|
| Default (lr=1e-3, hidden=128, update=2) | 52.67% | Baseline run |
| `--update-every 4` | **55.00%** | Fewer updates, more stable |
| `--hidden 256` | **56.00%** | More capacity helps |
| `--hidden 256 --update-every 4` | 52.67% | No synergy |
| `--lr 3e-4` | 53.67% | Lower LR didn't help |

Best config: `--hidden 256` (~56% win rate). Final model in `dqn_model/` uses
this config (54.67% on final repeat — high variance).

Expected eval noise is ~±3% (300 games), so differences near threshold are not
conclusive. The agent clearly beats the heuristic baseline, but further gains
likely need self-play or more episodes.

## How to run

```
python train_dqn.py --episodes 10000 --eval-every 1000 --eval-games 300      # default 2-player
python train_dqn.py --players 4                                               # 4-player
python train_dqn.py --episodes 10000 --eval-every 1000 --eval-games 300 --hidden 256   # best known config
```

## Next steps (to continue)

1. ~~Stress-test env after empty-options fix~~ (done: 100k eps, 0 errors).
2. ~~Run a full ~10k-episode training~~ (done, plus tuning sweeps).
3. **Self-play** — train against itself instead of a fixed heuristic to get
   a stronger opponent as the agent improves.
4. **More episodes** — 50k+ episodes may still improve with the --hidden 256
   config.
5. **Reward tuning** — higher capture bonuses or win bonuses may shape behaviour.
6. **4-player** — run with `--players 4` to handle the full game.
7. Delete `/tmp/opencode/` temp files when done.