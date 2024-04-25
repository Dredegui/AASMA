import env.footpong
from env.constants import *
from time import sleep
from sys import argv
import math
import random
import numpy as np
import torch
import matplotlib
import matplotlib.pyplot as plt
from dqn import DQN
from itertools import count
import random as r
import pygame

is_ipython = 'inline' in matplotlib.get_backend()
if is_ipython:
    from IPython import display
plt.ion()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

if __name__ == "__main__":
    env = env.footpong.footpong(render_mode="human")
    env.reset()
    env.render()
    dqns = [DQN(f"player{i}", device=device) for i in range(1, 5)]
    # models = [q_learning(env, player=f"player{i}") for i in range(1, 5)]

    user_mode = NO_USER
    if len(argv) == 2 and argv[1] in ['1', '2', '3', '4']:
        print(f"User mode on!\nUse arrow keys to move player {argv[1]}")
        user_mode = ONE_USER

    if len(argv) == 3 and argv[1] != argv[2] and argv[1] in ['1', '2', '3', '4'] and argv[2] in ['1', '2', '3', '4']:
        print(f"User mode on!\nUse arrow keys to move player {argv[1]}")
        print(f"Use WASD keys to move player {argv[2]}")
        user_mode = TWO_USER

    clock = pygame.time.Clock()
    episodes = 1000
    while episodes > 0:
        observations, _ = env.reset()
        observations ={agent: torch.tensor(observations[agent], dtype=torch.float32, device=device).unsqueeze(0) for agent in env.agents}
        while env.agents:
            if user_mode:
                actions = {}
                for agent in env.agents:
                    keys = pygame.key.get_pressed()
                    if agent == f"player{argv[1]}":
                        if keys[pygame.K_UP]:
                            actions[agent] = MOVE_UP
                        elif keys[pygame.K_DOWN]:
                            actions[agent] = MOVE_DOWN
                        elif keys[pygame.K_LEFT]:
                            actions[agent] = MOVE_LEFT
                        elif keys[pygame.K_RIGHT]:
                            actions[agent] = MOVE_RIGHT
                        else:
                            actions[agent] = DONT_MOVE
                    elif user_mode == TWO_USER and agent == f"player{argv[2]}":
                        if keys[pygame.K_w]:
                            actions[agent] = MOVE_UP
                        elif keys[pygame.K_s]:
                            actions[agent] = MOVE_DOWN
                        elif keys[pygame.K_a]:
                            actions[agent] = MOVE_LEFT
                        elif keys[pygame.K_d]:
                            actions[agent] = MOVE_RIGHT
                        else:
                            actions[agent] = DONT_MOVE
                    else:
                        actions[agent] = DONT_MOVE
                clock.tick(30)
            else:
                actions = {f"player{i}": dqns[i-1].choose_action(observations[f"player{i}"], env) for i in range(1, 5)}

            next_observations, rewards, terminations, truncations, infos = env.step(actions)
            c = 0
            while c < len(env.agents):
                agent = env.agents[c]
                rewards[agent] = torch.tensor([rewards[agent]], dtype=torch.float32, device=device)
                if terminations[agent]:
                    next_observations[agent] = None
                else:
                    next_observations[agent] = torch.tensor(next_observations[agent], dtype=torch.float32, device=device).unsqueeze(0)
                dqns[c].push(observations[agent], actions[agent], next_observations[agent], rewards[agent])
                dqns[c].learn()
                observations[agent] = next_observations[agent]
                dqns[c].soft_update_target_model()
                dqns[c].decay_epsilon()
                c += 1
            
            env.render()
    
    if user_mode == NO_USER:
        for dqn in dqns:
            dqn.save_target()
    env.close()
