from agents.agent import Agent
from env.constants import *
import torch

class HardCodedAgent(Agent):
	def __init__(self, name, agent_id, device=None):
		super().__init__(name, agent_id)
		self.device = device

	def _choose_action_left_team(self, observation):
		if observation is None:
			return DONT_MOVE
		ball = observation[-2:]
		player = observation[(self.agent_id-1)*2:(self.agent_id-1)*2+2]
		if player[0] + PLAYER_WIDTH <= ball[0]:
			if abs(player[1]-ball[1]) < BALL_DIAMETER:
				return MOVE_RIGHT
			elif player[1] < ball[1]:
				return MOVE_DOWN
			else:
				return MOVE_UP
		else:
			if abs(player[1]-ball[1]) < BALL_DIAMETER:
				if player[1] < ball[1]:
					return MOVE_UP
				else:
					return MOVE_DOWN
			else:
				return MOVE_LEFT

	def _choose_action_right_team(self, observation):
		if observation is None:
			return DONT_MOVE
		ball = observation[-2:]
		player = observation[(self.agent_id-1)*2:(self.agent_id-1)*2+2]
		if player[0] >= ball[0]:
			if abs(player[1]-ball[1]) < BALL_DIAMETER:
				return MOVE_LEFT
			elif player[1] < ball[1]:
				return MOVE_DOWN
			else:
				return MOVE_UP
		else:
			if abs(player[1]-ball[1]) < BALL_DIAMETER:
				if player[1] < ball[1]:
					return MOVE_UP
				else:
					return MOVE_DOWN
			else:
				return MOVE_RIGHT
	
	def act(self, observation):
		if self.agent_id == 1 or self.agent_id == 3:
			action = self._choose_action_left_team(observation)
			if self.device is not None:
				return torch.tensor(action, dtype=torch.float32, device=self.device)
			return action
		else:
			action = self._choose_action_right_team(observation)
			if self.device is not None:
				return torch.tensor(action, dtype=torch.float32, device=self.device)
			return action
			