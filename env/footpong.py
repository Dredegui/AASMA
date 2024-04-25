from .game import Game
from .ball import Ball
from .player import Player
from .constants import *
import numpy as np

import functools
from pettingzoo import ParallelEnv
import gymnasium
from pettingzoo.utils import parallel_to_aec, wrappers
import pygame

def env(render_mode=None):
    """
    The env function often wraps the environment in wrappers by default.
    You can find full documentation for these methods
    elsewhere in the developer documentation.
    """
    internal_render_mode = render_mode if render_mode in ["rgb_array"] else "human"

    env = raw_env(render_mode=internal_render_mode)
    # This wrapper is only for environments which print results to the terminal
    if render_mode == "ansi":
        env = wrappers.CaptureStdoutWrapper(env)
    # this wrapper helps error handling for discrete action spaces
    env = wrappers.AssertOutOfBoundsWrapper(env)
    # Provides a wide vareity of helpful user errors
    # Strongly recommended
    env = wrappers.OrderEnforcingWrapper(env)
    return env

def raw_env(render_mode=None):
    """
    To support the AEC API, the raw_env() function just uses the from_parallel
    function to convert from a ParallelEnv to an AEC env
    """
    env = footpong(render_mode=render_mode)
    env = parallel_to_aec(env)
    return env

class footpong(ParallelEnv):
    metadata = {
        "name": "foot_pong_v0",
        "render_modes": ["human", "rgb_array"],
    }

    timestep_limit = 1_000_000

    def __init__(self, render_mode=None):
        self.game = Game()
        self.possible_agents = [p.name for p in self.game.players]
        self.agents = self.possible_agents[:]
        self.agent_name_mapping = {p.name: i for i, p in enumerate(self.game.players)}
        self.observation_spaces = {agent: self.observation_space(agent) for agent in self.agents}
        self.action_spaces = {agent: self.action_space(agent) for agent in self.agents}
        self.timestamp = 0
        self.render_mode = render_mode
 
    def observe(self, agent):
        players = self.game.players
        players_coords = []
        for p in players:
            players_coords += [p.rect.x, p.rect.y]
        return players_coords + [self.game.ball.rect.x, self.game.ball.rect.y]

    def reset(self, seed=None, options=None):
        self.timestamp = 0
        self.agents = self.possible_agents[:]
        self.game = Game()
        observations = {agent: self.observe(agent) for agent in self.agents}
        infos = {agent: {} for agent in self.agents}

        return observations, infos
        
    def step(self, actions):
        # for all players do the respective action
        for agent, action in actions.items():
            player = self.game.players[self.agent_name_mapping[agent]]
            if action == MOVE_UP:
                player.move_up()
            elif action == MOVE_DOWN:
                player.move_down()
            elif action == MOVE_LEFT:
                player.move_left()
            elif action == MOVE_RIGHT:
                player.move_right()
            else:
                player.stop()

        old_observation = {agent: self.observe(agent) for agent in self.agents}
        state = self.game.move()
        observation = {agent: self.observe(agent) for agent in self.agents}
        # check if the distance between the ball and the player decreased
        rewards = {agent: 1 if state == self.game.players[self.agent_name_mapping[agent]].team else -1 for agent in self.agents}
        c = 0
        while c < len(self.agents):
            agent = self.agents[c]
            print("check", old_observation[agent], observation[agent])
            old_distance = np.linalg.norm(np.array(old_observation[agent][-2:]) - np.array(old_observation[agent][2*c:2*(c+1)]))
            new_distance = np.linalg.norm(np.array(observation[agent][-2:]) - np.array(observation[agent][2*c:2*(c+1)]))
            if new_distance < old_distance:
                # give reward to the player that got closer to the ball
                # decrease the reward according to the epsilon 
                rewards[agent] = 0.1 / (1 + self.timestamp)
                if rewards[agent] < 0.001:
                    rewards[agent] = 0
            c += 1
                
        done = self.game.score[0] == MAX_SCORE or self.game.score[1] == MAX_SCORE
        terminations = {agent: done for agent in self.agents}
        truncations = {agent: self.timestamp > self.timestep_limit for agent in self.agents}
        
        # When in human mode, check if user closed the window
        if self.render_mode == "human":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    truncations = {agent: True for agent in self.agents}

        self.timestamp += 1
        infos = {agent: {} for agent in self.agents}

        if any(terminations.values()) or all(truncations.values()):
            self.agents = []
        
        return observation, rewards, terminations, truncations, infos

    def close(self):
        pygame.quit()
        
    def render(self):
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return
        
        return self.game.render(self.render_mode)

    # Observation space should be defined here.
    # lru_cache allows observation and action spaces to be memoized, reducing clock cycles required to get each agent's space.
    # If your spaces change over time, remove this line (disable caching).
    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        # gymnasium spaces are defined and documented here: https://gymnasium.farama.org/api/spaces/
        # Dict containing team, opponent and ball coordinates (x, y) discrite values
        # Agent coords and other agent coords are in the game class
        return gymnasium.spaces.MultiDiscrete([800, 600]*5)

    # Action space should be defined here.
    # If your spaces change over time, remove this line (disable caching).
    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return gymnasium.spaces.Discrete(5)  # 5 possible actions: up, down, left, right, None