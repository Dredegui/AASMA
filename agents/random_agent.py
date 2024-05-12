from agents.agent import Agent
from env.constants import *
import random as r

class RandomAgent(Agent):
    def __init__(self, name, agent_id):
        super().__init__(name, agent_id)

    def act(self, observation):
        return r.choice([MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT, DONT_MOVE])