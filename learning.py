import env.footpong
from env.constants import *
from time import sleep
from sys import argv
import torch
import matplotlib
import matplotlib.pyplot as plt
from dqn import DQN
import random as r
import pygame
from plotter import plot
import time
import os
import signal
from agents.hard_coded_agent import HardCodedAgent

is_ipython = 'inline' in matplotlib.get_backend()
if is_ipython:
    from IPython import display
plt.ion()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

def save_model(dqns):
    for dqn in dqns:
        dqn.save_target()

# trap sigint
def signal_handler(sig, frame):
    print("Exiting...")
    if input("Do you want to save the model? [y/N]").lower() == "y":
        save_model(dqns)
    pygame.quit()
    exit(0)

if __name__ == "__main__":
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100,100)
    signal.signal(signal.SIGINT, signal_handler)
    env = env.footpong.footpong(render_mode="human", n_players=1, learning_mode=True)
    env.render()
    n_agents = env.game.n_players
    dqns = [DQN(f"player{i}", len_observation_space=(n_agents + 1)*2, device=device) for i in range(1, n_agents + 1)]
    clock = pygame.time.Clock()
    episodes = 0
    padding = 200
    old_t = time.time()
    # hagent = HardCodedAgent(device=device)
    while episodes < 100:
        t = time.time()
        print(f"Time: {t - old_t}, episode: {episodes}")
        old_t = t
        episodes += 1
        # generate random seed if not first episode
        seed = None
        if episodes > 1:
            seed = r.randint(0, 1000)
        observations, _ = env.reset(seed=seed)
        observations ={agent: torch.tensor(observations[agent], dtype=torch.float32, device=device).unsqueeze(0) for agent in env.agents}
        for dqn in dqns:
            dqn.decay_epsilon()
        print(dqns[0].epsilon)
        while env.agents:
            actions = {f"player{i}": dqns[i-1].act(observations[f"player{i}"]) for i in range(1, n_agents + 1)}
            # clock.tick(1000)
            next_observations, rewards, terminations, truncations, infos = env.step(actions)
            c = 0
            while c < n_agents: # for agent in env.agents:
                agent = f"player{c+1}"
                rewards[agent] = torch.tensor([rewards[agent]], dtype=torch.float32, device=device)
                if terminations[agent] or truncations[agent]:
                    next_observations[agent] = None
                else:
                    next_observations[agent] = torch.tensor(next_observations[agent], dtype=torch.float32, device=device).unsqueeze(0)
                dqns[c].push(observations[agent], actions[agent], next_observations[agent], rewards[agent])
                dqns[c].learn()
                observations[agent] = next_observations[agent]
                dqns[c].soft_update_target_model()
                c += 1
            env.render()
    save_model(dqns)
    env.close()
