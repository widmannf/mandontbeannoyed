import argparse
import os
import random
from collections import deque

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
import numpy as np
import tensorflow as tf

from dba_gym import DbaEnv

rng = random.Random()


def make_model(obs_size, n_actions=4, hidden=128):
    inp = tf.keras.layers.Input(shape=(obs_size,))
    x = tf.keras.layers.Dense(hidden, activation="relu")(inp)
    x = tf.keras.layers.Dense(hidden, activation="relu")(x)
    out = tf.keras.layers.Dense(n_actions)(x)
    model = tf.keras.Model(inp, out)
    return model


def compile_step(model, target, optimizer, loss_fn, gamma, tau):
    @tf.function
    def step(ob, act, rew, n_ob, d):
        with tf.GradientTape() as tape:
            q = model(ob, training=True)
            gathered = tf.reduce_sum(q * tf.one_hot(act, 4), axis=1)
            n_mask = n_ob[:, -4:] > 0.5
            q_next = model(n_ob, training=False)
            q_next = tf.where(n_mask, q_next, -1e9 + tf.zeros_like(q_next))
            best = tf.argmax(q_next, axis=1)
            q_t = target(n_ob, training=False)
            q_t = tf.reduce_sum(q_t * tf.one_hot(best, 4), axis=1)
            target_q = rew + gamma * q_t * (1.0 - d)
            loss = loss_fn(target_q, gathered)
        grads = tape.gradient(loss, model.trainable_variables)
        optimizer.apply_gradients(zip(grads, model.trainable_variables))
        for var, tvar in zip(model.trainable_variables, target.trainable_variables):
            tvar.assign_sub(tau * (tvar - var))
        return loss

    return step


def select_action(model, obs, valid, eps, obs_size):
    if not valid:
        return 0
    if rng.random() < eps:
        return int(rng.choice(valid))
    q = model(np.asarray([obs], dtype=np.float32), training=False).numpy()[0]
    masked_q = np.full(4, -1e9)
    masked_q[valid] = q[valid]
    return int(np.argmax(masked_q))


def evaluate(model, num_players, games, seed, obs_size):
    wins = 0
    for g in range(games):
        env = DbaEnv(num_players=num_players, seed=(seed + g) if seed else None)
        obs = env.reset()
        done = False
        while not done:
            valid = env.options
            action = select_action(model, obs, valid, 0.0, obs_size)
            obs, _, done, _ = env.step(action)
        if env.engine.winner == env.agent:
            wins += 1
    return wins / games


def simulate_heuristic_wins(num_players, games, seed=0):
    wins = [0] * num_players
    for g in range(games):
        env = DbaEnv(num_players=num_players, seed=(seed + g))
        env.reset()
        while env.engine.winner is None:
            p = env.engine.current
            die = env.engine.roll()
            opts = env.engine.move_options(p, die)
            if not opts:
                env.engine.next_player()
                continue
            action = env._opponent_choice(p, opts, die)
            env.engine.apply_move(p, action, die)
            if die != 6:
                env.engine.next_player()
        wins[env.engine.winner] += 1
    return wins


def train(args):
    env = DbaEnv(num_players=args.players, seed=args.seed)
    obs_size = env.obs_size
    model = make_model(obs_size, hidden=args.hidden)
    target = make_model(obs_size, hidden=args.hidden)
    target.set_weights(model.get_weights())
    optimizer = tf.keras.optimizers.Adam(learning_rate=args.lr)
    loss_fn = tf.keras.losses.Huber()

    if args.self_play:
        opp_model = make_model(obs_size, hidden=args.hidden)
        def opp_policy(obs, valid):
            q = opp_model(np.asarray([obs], dtype=np.float32), training=False).numpy()
            masked_q = np.full((1, 4), -1e9)
            masked_q[0, valid] = q[0, valid]
            return int(np.argmax(masked_q[0]))
        env = DbaEnv(num_players=args.players, seed=args.seed, opponent_policy=opp_policy)

    buf = deque(maxlen=args.replay)
    step_fn = compile_step(model, target, optimizer=optimizer, loss_fn=loss_fn,
                           gamma=args.gamma, tau=args.tau)

    def sample_batch(n):
        idx = rng.sample(range(len(buf)), n)
        b = [buf[i] for i in idx]
        return (
            np.asarray([t[0] for t in b], dtype=np.float32),
            np.asarray([t[1] for t in b], dtype=np.int32),
            np.asarray([t[2] for t in b], dtype=np.float32),
            np.asarray([t[3] for t in b], dtype=np.float32),
            np.asarray([t[4] for t in b], dtype=np.float32),
        )

    eps = args.eps_start
    step = 0
    best = -1.0
    returns = deque(maxlen=200)

    for episode in range(1, args.episodes + 1):
        eps = max(args.eps_min, args.eps_start - (args.eps_start - args.eps_min) * episode / (args.episodes * 0.8))
        obs = env.reset()
        done = False
        ep_ret = 0.0
        while not done:
            valid = env.options
            if not valid:
                break
            action = select_action(model, obs, valid, eps, obs_size)
            n_obs, reward, done, _ = env.step(action)
            ep_ret += reward
            buf.append((obs, action, reward, n_obs, done))
            obs = n_obs
            step += 1
            if len(buf) >= args.batch and step % args.update_every == 0:
                step_fn(*sample_batch(args.batch))
        returns.append(ep_ret)

        if args.self_play and episode % args.opponent_update == 0:
            opp_model.set_weights(model.get_weights())

        if episode % args.eval_every == 0:
            win_rate = evaluate(model, args.players, args.eval_games, args.seed or episode, obs_size)
            line = (f"ep {episode:6d} | eps {eps:.3f} | avg_ret {np.mean(returns):8.2f} "
                    f"| win_rate {win_rate:6.2%}")
            if episode == args.eval_every:
                heur = simulate_heuristic_wins(args.players, args.games // 2, seed=args.seed or 1)
                line += f" | heuristic_first {heur[env.agent] / sum(heur):6.2%}"
            print(line, flush=True)
            if win_rate > best:
                best = win_rate
                model.save(args.save)
                print(f"  saved best model ({win_rate:.2%}) to {args.save}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--players", type=int, default=2, choices=[2, 3, 4])
    parser.add_argument("--episodes", type=int, default=10000)
    parser.add_argument("--update-every", type=int, default=2)
    parser.add_argument("--eval-every", type=int, default=2000)
    parser.add_argument("--eval-games", type=int, default=200)
    parser.add_argument("--games", type=int, default=1000)
    parser.add_argument("--batch", type=int, default=256)
    parser.add_argument("--replay", type=int, default=100000)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--tau", type=float, default=0.005)
    parser.add_argument("--hidden", type=int, default=128)
    parser.add_argument("--eps-start", type=float, default=1.0)
    parser.add_argument("--eps-min", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--save", type=str, default="dqn_model")
    parser.add_argument("--self-play", action="store_true")
    parser.add_argument("--opponent-update", type=int, default=5000)
    args = parser.parse_args()
    train(args)