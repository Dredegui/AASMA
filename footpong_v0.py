from env.footpong import footpong
from time import sleep
import random as r

if __name__ == "__main__":
    env = footpong()
    env.reset()
    env.render()

    done = False
    while not done:
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
