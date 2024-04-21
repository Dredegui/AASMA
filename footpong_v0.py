import env.footpong
from env.constants import *
from time import sleep
from sys import argv
import random as r
import pygame

if __name__ == "__main__":
    env = env.footpong.footpong(render_mode="human")
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

    clock = pygame.time.Clock()
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
            # choose random actions for all agents
            actions = {agent: env.action_space(agent).sample() for agent in env.agents}
            clock.tick(30)

        observations, rewards, terminations, truncations, infos = env.step(actions)
        env.render()

    env.close()
