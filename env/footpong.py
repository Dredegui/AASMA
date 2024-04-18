from .game import Game
from .ball import Ball
from .player import Player

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
 

    def reset(self, seed=None, options=None):
        pass
        
    def step(self, actions):
        pass

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
        return gymnasium.spaces.Dict({
            "self": gymnasium.space.MultiDiscrete([800, 600]),
            "opponents": gymnasium.space.Tuple([gymnasium.space.MultiDiscrete([800, 600]) for _ in range(1)]),
            "ball": gymnasium.space.MultiDiscrete([800, 600])
        })    

    # Action space should be defined here.
    # If your spaces change over time, remove this line (disable caching).
    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return gymnasium.spaces.Discrete(5)  # 5 possible actions: up, down, left, right, None