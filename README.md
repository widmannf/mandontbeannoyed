# Man, don't be annoyed!

Implementation of the German game "Mensch ärger dich nicht", similar to the english game Ludo.

![image](https://github.com/user-attachments/assets/cd7fdd22-d5f3-46fc-be18-34d09236e07f)


# Rules
- Need a 6 to leave home
- After a 6 you can go again (if there was a possible move)
- If possible piece on own first field must be moved
- If you land on same field as an opponent piece, it gets send home
- Can't send your own pieces home
- Winner is who first fills hist 4 goal fields

# Run
python dontbeannoyed.py

options: -a for autoroll, you don't need to click to roll the die

# Train an AI (RL)

The game logic lives in `engine.py` (no pygame needed) and is wrapped as the
`DbaEnv` reinforcement-learning environment in `dba_gym.py`.

- `DbaEnv` exposes a *decision-level* MDP: it plays out non-decision rolls and
  opponent turns internally, and only asks the agent for a move when it has
  at least one valid option (masked via the last 4 observation entries).
- Action space: `Discrete(4)` (which of your pieces to move). Invalid actions
  are masked.
- Observation: all pieces' positions (relative to the agent), pending die,
  current player, and a 0/1 mask of which of your pieces currently can move.
- Rewards: winning +100, capturing an opponent +15, being captured -15,
  leaving home +5, entering the goal corridor +10, corridor progress +1.

Train a DQN (TensorFlow/Keras):

```
python train_dqn.py                              # 2-player self-play setup vs a heuristic
python train_dqn.py --players 4                  # full 4-player board
python train_dqn.py --episodes 20000 --eval-every 1000
```

The best model is saved to `dqn_model/` whenever evaluation improves. The
printed `win_rate` is against the heuristic opponent; the `heuristic_first`
line is the same heuristic's win rate when opening, i.e. the baseline to beat.

# Why?
Really I want to train an AI to play this game, to more efficiently beat my girlfriend in it. So implementing the game is the first step.
