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
from hard_coded_agent import hard_coded_agent

is_ipython = 'inline' in matplotlib.get_backend()
if is_ipython:
    from IPython import display
plt.ion()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

if __name__ == "__main__":
    env = env.footpong.footpong(render_mode="human")
    env.render()
    dqns = [DQN(f"player{i}", device=device) for i in range(1, 5)]
    user_mode = NO_USER
    if len(argv) == 2 and argv[1] in ['1', '2', '3', '4']:
        print(f"User mode on!\nUse arrow keys to move player {argv[1]}")
        user_mode = ONE_USER

    if len(argv) == 3 and argv[1] != argv[2] and argv[1] in ['1', '2', '3', '4'] and argv[2] in ['1', '2', '3', '4']:
        print(f"User mode on!\nUse arrow keys to move player {argv[1]}")
        print(f"Use WASD keys to move player {argv[2]}")
        user_mode = TWO_USER

    clock = pygame.time.Clock()
    episodes = 0
    plot_scores = []
    plot_mean_scores = []
    record = 0
    score = 0
    total_score = 0
    padding = 200
    old_t = time.time()
    hagent = hard_coded_agent()
    while episodes < 100:
        t = time.time()
        print(f"Time: {t - old_t}")
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
                # switch player1 actions with hard coded agent
                actions["player1"] = hagent.choose_action(observations["player1"], 0)
                #clock.tick(1000)

            next_observations, rewards, terminations, truncations, infos = env.step(actions)
            if user_mode == NO_USER:
                c = 0
                while c < len(rewards.keys()): # for agent in env.agents:
                    agent = f"player{c+1}"
                    rewards[agent] = torch.tensor([rewards[agent]], dtype=torch.float32, device=device)
                    if terminations[agent] or truncations[agent]:
                        next_observations[agent] = None
                        """
                        if agent == "player1":
                            score = env.game.score[0]
                            if score >= record:
                                record = score
                            total_score += score
                            plot_scores.append(score)
                            mean_score = total_score / episodes
                            plot_mean_scores.append(mean_score)
                            plot(plot_scores, plot_mean_scores)
                        """
                    else:
                        next_observations[agent] = torch.tensor(next_observations[agent], dtype=torch.float32, device=device).unsqueeze(0)
                    dqns[c].push(observations[agent], actions[agent], next_observations[agent], rewards[agent])
                    dqns[c].learn()
                    observations[agent] = next_observations[agent]
                    dqns[c].soft_update_target_model()
                    c += 1
                env.render()
            else:
                env.render()
            
    if user_mode == NO_USER:
        for dqn in dqns:
            dqn.save_target()
    env.close()
