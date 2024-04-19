from .game import Game
from .ball import Ball
from .player import Player
from .constants import *
import numpy as np

import functools
from pettingzoo import ParallelEnv
import gymnasium.spaces
import pygame

class footpong(ParallelEnv):
    metadata = {
        "name": "foot_pong_v0",
    }

    def __init__(self):
        self.game = Game()
        self.agents = [p.name for p in self.game.players]
        self.agent_name_mapping = {p.name: i for i, p in enumerate(self.game.players)}
 
    def observe(self, agent):
        player = self.game.players[self.agent_name_mapping[agent]]
        teammate = [p for p in self.game.players if p.team == player.team and p != player][0]
        opponents = [p for p in self.game.players if p.team != player.team]
        player_coords = np.array([player.rect.x, player.rect.y])
        team_coords = np.array([teammate.rect.x, teammate.rect.y])
        opponents_coords = np.array([[p.rect.x, p.rect.y] for p in opponents]).flatten()
        ball_coords = np.array([self.game.ball.rect.x, self.game.ball.rect.y])
        return {
            "self": player_coords,
            "team": team_coords,
            "opponents": opponents_coords,
            "ball": ball_coords,
        }

    def reset(self, seed=None, options=None):
        self.game = Game()
        return {agent: self.observe(agent) for agent in self.agents}
        
    def step(self, actions):
        # for all players do the respective action
        for agent, action in actions.items():
            player = self.game.players[self.agent_name_mapping[agent]]
            if action == 0:
                player.move_up()
            elif action == 1:
                player.move_down()
            elif action == 2:
                player.move_left()
            elif action == 3:
                player.move_right()
            else:
                player.stop()

        state = self.game.move()
        observation = {agent: self.observe(agent) for agent in self.agents}
        rewards = {agent: 1 if state == self.game.players[self.agent_name_mapping[agent]].team else -1 for agent in self.agents}
        done = self.game.score[0] == MAX_SCORE or self.game.score[1] == MAX_SCORE
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        return observation, rewards, done, None

    def close(self):
        pygame.quit()
        
    def render(self):
        self.game.render()

    # Observation space should be defined here.
    # lru_cache allows observation and action spaces to be memoized, reducing clock cycles required to get each agent's space.
    # If your spaces change over time, remove this line (disable caching).
    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        # gymnasium spaces are defined and documented here: https://gymnasium.farama.org/api/spaces/
        # Dict containing team, opponent and ball coordinates (x, y) discrite values
        # Agent coords and other agent coords are in the game class
        return gymnasium.spaces.Dict({
            "self": gymnasium.spaces.Box(low=np.array([0, 0]), high=np.array([800, 600]), dtype=np.float32),
            "team": gymnasium.spaces.Box(low=np.array([0, 0]), high=np.array([800, 600]), dtype=np.float32),
            "opponents": gymnasium.spaces.Box(low=np.array([0, 0, 0, 0]), high=np.array([800, 600, 800, 600]), dtype=np.float32),
            "ball": gymnasium.spaces.Box(low=np.array([0, 0]), high=np.array([800, 600]), dtype=np.float32),
        })

    # Action space should be defined here.
    # If your spaces change over time, remove this line (disable caching).
    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return gymnasium.spaces.Discrete(5)  # 5 possible actions: up, down, left, right, None