import env.footpong
from env.constants import *
from time import sleep
from sys import argv
import torch
import matplotlib
import matplotlib.pyplot as plt
from dqn import DQN
import pygame
from plotter import plot
import os
import signal

is_ipython = 'inline' in matplotlib.get_backend()
if is_ipython:
    from IPython import display
plt.ion()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

# trap sigint
def signal_handler(sig, frame):
    print("Exiting...")
    pygame.quit()
    exit(0)

if __name__ == "__main__":
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100,100)
    signal.signal(signal.SIGINT, signal_handler)
    env = env.footpong.footpong(render_mode="human")
    env.render()
    n_agents = env.game.n_players
    dqns = [DQN(f"player{i}", len_observation_space=(n_agents + 1)*2, device=device) for i in range(1, n_agents + 1)]
    user_mode = NO_USER
    if len(argv) == 2 and argv[1] in ['1', '2', '3', '4']:
        print(f"User mode on!\nUse arrow keys to move player {argv[1]}")
        user_mode = ONE_USER

    if len(argv) == 3 and argv[1] != argv[2] and argv[1] in ['1', '2', '3', '4'] and argv[2] in ['1', '2', '3', '4']:
        print(f"User mode on!\nUse arrow keys to move player {argv[1]}")
        print(f"Use WASD keys to move player {argv[2]}")
        user_mode = TWO_USER

    clock = pygame.time.Clock()
    while env.agents:
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
    env.close()
