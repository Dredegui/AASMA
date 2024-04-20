from env.footpong import footpong
from env.constants import *
from time import sleep
from sys import argv
import random as r
import pygame

if __name__ == "__main__":
    env = footpong()
    env.reset()
    env.render()

    user_mode = NO_USER
    if len(argv) == 2 and argv[1] in ['1', '2', '3', '4']:
        print(f"User mode on!\nUse arrow keys to move player {argv[1]}")
        user_mode = ONE_USER

    if len(argv) == 3 and argv[1] != argv[2] and argv[1] in ['1', '2', '3', '4'] and argv[2] in ['1', '2', '3', '4']:
        print(f"User mode on!\nUse arrow keys to move player {argv[1]}")
        print(f"Use WASD keys to move player {argv[2]}")
        user_mode = TWO_USER

    done = False
    while not done:
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
        else:
            # choose random actions for all agents
            actions = {agent: env.action_space(agent).sample() for agent in env.agents}
            # get more actions of 3 for player 1 and 3
            """
            if (r.random() < 0.5):
                actions['player1'] = 3
                actions['player3'] = 3
            # get more actions of 2 for player 2 and 4
            if (r.random() < 0.5):
                actions['player2'] = 2
                actions['player4'] = 2
            """

        #print(actions)
        observations, rewards, done, _ = env.step(actions)
        env.render()
        sleep(0.1)

    env.close()
