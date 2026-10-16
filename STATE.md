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

## Status

- Stress test of env (100k episodes, random policy) is passing/verifying the
  empty-options fix (was aborted mid-run by user, no failures up to that point).
- Early smoke run (400 eps vs heuristic): win rate 43% (baseline) -> 49-51%,
  avg return rising 90 -> 102. Learning is happening but noisy.

## How to run

```
python train_dqn.py --episodes 10000 --eval-every 1000 --eval-games 300      # default 2-player
python train_dqn.py --players 4                                               # 4-player
```

Baseline to beat: first-player heuristic win rate ~43% (printed once at first eval).

## Next steps (to continue)

1. Finish stress-test of env after the empty-options fix (`/tmp/opencode/debug*`).
2. Run a full ~10k-episode training and confirm win rate climbs well above 50%.
3. Consider tuning: more hidden units, higher `--update-every`, reward weights
   (capture bonus vs goal bonus), opponent strength.
4. Optionally a real self-play variant or a rule-based baseline comparison.
5. Delete `/tmp/opencode/train*.log`, `/tmp/opencode/debug*`, `dqn_model/`
   when done if not wanted.