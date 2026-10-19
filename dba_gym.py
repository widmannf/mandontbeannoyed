import random

from engine import Engine

WIN_REWARD = 100
CAPTURE_REWARD = 5
BE_CAPTURED_REWARD = -5
EXIT_REWARD = 3
GOAL_REWARD = 10
DEEPEN_REWARD = 1


class DbaEnv:
    def __init__(self, num_players=2, seed=None, max_steps=2000, opponent_policy=None):
        self.agent = 0
        self.num_players = num_players
        self.engine = Engine(num_players, seed=seed)
        self.max_steps = max_steps
        self.opponent_policy = opponent_policy
        self.options = []
        self.die = 0
        self.step_count = 0
        self.obs_size = num_players * 4 + 2 + 4

    def reset(self):
        while True:
            self.engine.reset()
            self.engine.current = self.agent
            self.step_count = 0
            self.options = []
            self.die = 0
            done, _ = self._advance()
            if not done:
                break
        return self._obs()

    def _advance(self):
        penalized = 0
        while self.engine.winner is None:
            if self.step_count >= self.max_steps:
                return True, penalized
            die = self.engine.roll()
            opts = self.engine.move_options(self.engine.current, die)
            if not opts:
                self.engine.next_player()
                continue
            if self.engine.current == self.agent:
                self.die = die
                self.options = opts
                return False, penalized
            action = self._opponent_choice(self.engine.current, opts, die)
            _, _, hits = self.engine.apply_move(self.engine.current, action, die)
            for opp, _ in hits:
                if opp == self.agent:
                    penalized += 1
            if die == 6:
                continue
            self.engine.next_player()
        return True, penalized

    def step(self, action):
        if action not in self.options:
            raise ValueError(f"invalid action {action} for options {self.options}")
        self.step_count += 1
        die = self.die
        prev, new, hits = self.engine.apply_move(self.agent, action, die)
        reward = CAPTURE_REWARD * len(hits)
        if prev == -1:
            reward += EXIT_REWARD
        if new >= 40:
            if prev < 40:
                reward += GOAL_REWARD
            elif new > prev:
                reward += DEEPEN_REWARD
        if self.engine.winner is not None:
            self.die = 0
            self.options = []
            return self._obs(), reward + WIN_REWARD, True, {}
        if die != 6:
            self.engine.next_player()
        done, penalized = self._advance()
        reward += BE_CAPTURED_REWARD * penalized
        if done:
            self.die = 0
            self.options = []
            if self.engine.winner == self.agent:
                reward += WIN_REWARD
            return self._obs(), reward, True, {}
        return self._obs(), reward, False, {}

    def _encode(self, owner, pos, relative_to=None):
        if relative_to is None:
            relative_to = self.agent
        if pos == -1:
            return -1
        if pos >= 40:
            return 44
        return (pos + self.engine.offsets[owner] - self.engine.offsets[relative_to]) % 40

    def _obs(self, player=None, die=None):
        if player is None:
            player = self.agent
        if die is None:
            die = self.die
        obs = []
        for owner in range(self.num_players):
            for pos in self.engine.positions[owner]:
                obs.append(self._encode(owner, pos, relative_to=player))
        obs.append(die)
        obs.append(self.engine.current)
        opts = self.engine.move_options(player, die) if player == self.engine.current else []
        for i in range(4):
            obs.append(1 if i in opts else 0)
        return obs

    def _opponent_choice(self, player, opts, die):
        if self.opponent_policy is not None:
            obs = self._obs(player=player, die=die)
            return self.opponent_policy(obs, opts)
        def score(pi):
            old = self.engine.positions[player][pi]
            nxt = 0 if old == -1 else old + die
            cap = 0
            if nxt < 40:
                tgt = (nxt + self.engine.offsets[player]) % 40
                for other in range(self.num_players):
                    if other == player:
                        continue
                    for pos in self.engine.positions[other]:
                        if pos != -1 and pos < 40 and (pos + self.engine.offsets[other]) % 40 == tgt:
                            cap = 1
            return cap, nxt, -pi

        return max(opts, key=score)