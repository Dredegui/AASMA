from env.footpong import footpong
from time import sleep
from sys import argv
import random as r
import pygame

if __name__ == "__main__":
    env = footpong()
    env.reset()
    env.render()

    user_mode = False
    if len(argv) == 2 and argv[1] in ['1', '2', '3', '4']:
        print(f"User mode on!\nUse arrow keys to move player {argv[1]}")
        user_mode = True

    done = False
    while not done:
        if user_mode:
            actions = {}
            for agent in env.agents:
                if agent == f"player{argv[1]}":
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LEFT]:
                        actions[agent] = 2
                    elif keys[pygame.K_RIGHT]:
                        actions[agent] = 3
                    elif keys[pygame.K_UP]:
                        actions[agent] = 0
                    elif keys[pygame.K_DOWN]:
                        actions[agent] = 1
                    else:
                        actions[agent] = 4
                else:
                    actions[agent] = 4
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
