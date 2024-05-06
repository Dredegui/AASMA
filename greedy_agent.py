from env.constants import *
import torch

class greedy_agent():
    def __init__(self, device="cpu"):
        self.device = device

    def choose_action_aux(self, observation, player):
        ball = observation[-2:]
        player = observation[player*2:player*2+2]
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
        
    def choose_action(self, observation, player):
        # process tensor to list
        observation = observation.tolist()[0]
        return torch.tensor([self.choose_action_aux(observation, player)], dtype=torch.long, device=self.device).unsqueeze(0)