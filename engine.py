import random

GOAL_FIELDS = frozenset({40, 41, 42, 43})


class Engine:
    def __init__(self, num_players=2, seed=None):
        if num_players not in (2, 3, 4):
            raise ValueError("num_players must be 2, 3 or 4")
        self.num_players = num_players
        self.rng = random.Random(seed)
        if num_players == 2:
            self.offsets = [0, 20]
        else:
            self.offsets = [i * 10 for i in range(num_players)]
        self.reset()

    def reset(self):
        self.positions = [[-1] * 4 for _ in range(self.num_players)]
        self.current = 0
        self.winner = None
        return self

    def roll(self):
        return self.rng.randint(1, 6)

    def move_options(self, player, die):
        own = self.positions[player]
        occupied = {p for p in own if p != -1}
        for pi, p in enumerate(own):
            if p == 0 and (p + die) not in occupied:
                return [pi]
        opts = []
        for pi, p in enumerate(own):
            if p == -1:
                if die == 6:
                    opts.append(pi)
            else:
                nxt = p + die
                if nxt < 44 and nxt not in occupied:
                    opts.append(pi)
        return opts

    def apply_move(self, player, piece, die):
        own = self.positions[player]
        prev = own[piece]
        new = 0 if prev == -1 else prev + die
        own[piece] = new
        hits = []
        if new < 40:
            tgt = (new + self.offsets[player]) % 40
            for opp in range(self.num_players):
                if opp == player:
                    continue
                for oi in range(4):
                    op = self.positions[opp][oi]
                    if op != -1 and op < 40 and (op + self.offsets[opp]) % 40 == tgt:
                        self.positions[opp][oi] = -1
                        hits.append((opp, oi))
        if self.has_won(player):
            self.winner = player
        return prev, new, hits

    def has_won(self, player):
        return GOAL_FIELDS.issubset(self.positions[player])

    def next_player(self):
        self.current = (self.current + 1) % self.num_players