from agents.agent import Agent
from env.constants import *
import numpy as np
import random as rnd

class BalancedAgent(Agent):
	def __init__(self, name, agent_id, device=None):
		super().__init__(name, agent_id)
		self.device = device


	def _corner_case(self, observation):
		# check if the ball is in the corner
		ball = observation[-2:]
		player = observation[(self.agent_id-1)*2:(self.agent_id-1)*2+2]
		if self.device is not None:
			ball = ball.cpu()
			player = player.cpu()
		distance = np.linalg.norm(np.array(player) - np.array(ball))			
		max_distance = 4*PLAYER_WIDTH 
		if distance > max_distance:
			return None
		if rnd.random() < 0.5:
			if (ball[0] > SCREEN_WIDTH - max_distance and not(max_distance < ball[1] < SCREEN_HEIGHT - max_distance)):
				return MOVE_LEFT
			if (ball[0] < max_distance and not(max_distance < ball[1] < SCREEN_HEIGHT - max_distance)):
				return MOVE_RIGHT
		return None


	def _stuck_case(self, observation, action):
		ball = observation[-2:]
		player = observation[(self.agent_id-1)*2:(self.agent_id-1)*2+2]
		# check if ball is between player and another player
		if self.device is not None:
			ball = ball.cpu()
			player = player.cpu()
		for i in range(1, 4):
			if i == self.agent_id:
				continue
			other_player = observation[(i-1)*2:(i-1)*2+2]
			if self.device is not None:
				other_player = other_player.cpu()
			other_distance = np.linalg.norm(np.array(other_player) - np.array(ball))
			distance = np.linalg.norm(np.array(player) - np.array(ball))
			if ((other_player[0] < ball[0] < player[0]) or (other_player[0] > ball[0] > player[0])) and (abs(distance) < PLAYER_WIDTH or abs(other_distance) < PLAYER_WIDTH) and abs(distance - other_distance) < PLAYER_WIDTH:
				# return any other random action
				tmp = action
				while tmp == action:
					tmp = rnd.randint(0, 3)
				return tmp
		return None


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
		if player[0] >= ball[0] + BALL_DIAMETER:
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
			tmp = self._corner_case(observation)
			if tmp is not None:
				action = tmp
			else:
				tmp = self._stuck_case(observation, action)
				if tmp is not None:
					action = tmp
			return action
		else:
			action = self._choose_action_right_team(observation)
			tmp = self._corner_case(observation)
			if tmp is not None:
				action = tmp
			return action
			