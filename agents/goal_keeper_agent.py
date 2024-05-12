from agents.agent import Agent
from env.constants import *

class GoalKeeperAgent(Agent):
    def __init__(self, name, agent_id):
        super().__init__(name, agent_id)

    def act(self, observation):
        ball = observation[-2:]
        player = observation[(self.agent_id-1)*2:(self.agent_id-1)*2+2]
        
        # move close to the goal
        if player[1] + PLAYER_HEIGHT > GOAL_BOTTOM:
            return MOVE_UP
        if player[1] < GOAL_TOP:
            return MOVE_DOWN
        
        if self.agent_id == 2 or self.agent_id == 4:
            if player[0] < SCREEN_WIDTH - SCREEN_WIDTH/6:
                return MOVE_RIGHT
            
            if player[0] < ball[0]:
                return MOVE_RIGHT
            if player[0] > ball[0] and player[1] + PLAYER_HEIGHT > ball[1] and player[1] < ball[1]:
                return MOVE_LEFT     
            if player[1] + PLAYER_HEIGHT > ball[1]:
                return MOVE_UP
            if player[1] < ball[1]:
                return MOVE_DOWN
            
            
            return DONT_MOVE
        
        if self.agent_id == 1 or self.agent_id == 3:
            if player[0] + PLAYER_WIDTH > SCREEN_WIDTH/6:
                return MOVE_LEFT
            
            if player[0] + PLAYER_WIDTH > ball[0]:
                return MOVE_LEFT
            if player[0] + PLAYER_WIDTH < ball[0] and player[1] + PLAYER_HEIGHT > ball[1] and player[1] < ball[1]:
                return MOVE_RIGHT
            if player[1] + PLAYER_HEIGHT > ball[1]:
                return MOVE_UP
            if player[1] < ball[1]:
                return MOVE_DOWN
            
            
            return DONT_MOVE
            