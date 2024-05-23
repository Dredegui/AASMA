from agents.agent import Agent
from env.constants import *

class GreedyAgent(Agent):
    def __init__(self, name, agent_id):
        super().__init__(name, agent_id)

    def act(self, observation):
        ball = observation[-2:]
        player = observation[(self.agent_id-1)*2:(self.agent_id-1)*2+2]
        # reach the ball
        distance_x = abs(ball[0] - player[0])
        distance_y = abs(ball[1] - player[1])
        if distance_x >= distance_y:
            if ball[0] > player[0]:
                return MOVE_RIGHT
            else:
                return MOVE_LEFT
        else:
            if ball[1] > player[1]:
                return MOVE_DOWN
            else:
                return MOVE_UP   
