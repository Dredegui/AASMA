from env.constants import *
import torch

class hard_coded_agent():
	def __init__(self, device="cpu"):
		self.device = device

	def choose_action_left_team(self, observation, player):
		if observation is None:
			return DONT_MOVE
		ball = observation[-2:]
		player = observation[player*2:player*2+2]
		if player[0] + PLAYER_WIDTH <= ball[0]: # x_player is to the left of x_ball
			if abs(player[1]-ball[1]) < BALL_DIAMETER: # y_player is close to y_ball
				return MOVE_RIGHT
			elif player[1] < ball[1]: # player is above the ball
				return MOVE_DOWN
			else:
				return MOVE_UP
		else: # x_pkayer is to the right of x_ball
			if abs(player[1]-ball[1]) < BALL_DIAMETER:
				# if player is close to upper wall move down
				if player[1] < ball[1]:
					return MOVE_UP
				else: # else move up
					return MOVE_DOWN
			else:
				return MOVE_LEFT

	# TODO rework this function
	def choose_action_right_team(self, observation, player):
		if observation is None:
			return DONT_MOVE
		ball = observation[-2:]
		player = observation[player*2:player*2+2]
		if player[0] > ball[0]: # x_player is to the right of x_ball
			if player[1]-ball[1] < PLAYER_HEIGHT: # y_player is close to y_ball
				return MOVE_LEFT
			elif player[1] < ball[1]: # player is above the ball
				return MOVE_DOWN
			else:
				return MOVE_UP
		elif player[0] < ball[0]: # x_pkayer is to the left of x_ball
			if player[1]-ball[1] < PLAYER_HEIGHT:
				# if player is close to upper wall move down
				if player[1] < 2* PLAYER_HEIGHT:
					return MOVE_DOWN
				else: # else move up
					return MOVE_UP
			else:
				return MOVE_RIGHT
		return DONT_MOVE
	
	def choose_action(self, observation, player):
		# process tensor to list
		observation = observation.tolist()[0]
		if player == 0 or player == 2:
			return torch.tensor([self.choose_action_left_team(observation, player)], dtype=torch.long, device=self.device).unsqueeze(0)
		else:
			return torch.tensor([self.choose_action_right_team(observation, player)], dtype=torch.long, device=self.device).unsqueeze(0)