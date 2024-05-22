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

def env(render_mode=None, n_players=4):
    """
    The env function often wraps the environment in wrappers by default.
    You can find full documentation for these methods
    elsewhere in the developer documentation.
    """
    internal_render_mode = render_mode if render_mode in ["rgb_array"] else "human"

    env = raw_env(render_mode=internal_render_mode, n_players=n_players)
    # This wrapper is only for environments which print results to the terminal
    if render_mode == "ansi":
        env = wrappers.CaptureStdoutWrapper(env)
    # this wrapper helps error handling for discrete action spaces
    env = wrappers.AssertOutOfBoundsWrapper(env)
    # Provides a wide vareity of helpful user errors
    # Strongly recommended
    env = wrappers.OrderEnforcingWrapper(env)
    return env

def raw_env(render_mode=None, n_players=4):
    """
    To support the AEC API, the raw_env() function just uses the from_parallel
    function to convert from a ParallelEnv to an AEC env
    """
    env = footpong(render_mode=render_mode, n_players=n_players)
    env = parallel_to_aec(env)
    return env

def check_collision_route_with_goal(game):
    ball = game.ball
    if ball.x_speed < 0:
        # check collision with left goal
        nsteps = int(abs(ball.rect.left / ball.x_speed))
        ypredicted = ball.rect.top + nsteps * ball.y_speed
        if ypredicted > GOAL_TOP and ypredicted < GOAL_BOTTOM:
            return PLAYER_TEAM_LEFT
    elif ball.x_speed > 0:
        # check collision with right goal
        nsteps = int(abs((SCREEN_WIDTH - ball.rect.right) / ball.x_speed))
        ypredicted = ball.rect.top + nsteps * ball.y_speed
        if ypredicted > GOAL_TOP and ypredicted < GOAL_BOTTOM:
            return PLAYER_TEAM_RIGHT
    return None


class footpong(ParallelEnv):
    metadata = {
        "name": "foot_pong_v0",
        "render_modes": ["human", "rgb_array"],
    }

    timestep_limit = 20_000 # 1_000_000 timesteps

    def __init__(self, render_mode=None, n_players=4, learning_mode=False):
        self.game = Game(n_players=n_players, learning_mode=learning_mode)
        self.possible_agents = [p.name for p in self.game.players]
        self.agents = self.possible_agents[:]
        self.agent_name_mapping = {p.name: i for i, p in enumerate(self.game.players)}
        self.observation_spaces = {agent: self.observation_space(agent) for agent in self.agents}
        self.action_spaces = {agent: self.action_space(agent) for agent in self.agents}
        self.timestamp = 0
        self.render_mode = render_mode
        self.steps_stopped_ball = 0
 
    def observe(self, agent):
        players = self.game.players
        players_coords = []
        for p in players:
            players_coords += [p.rect.x, p.rect.y]
        return players_coords + [self.game.ball.rect.x, self.game.ball.rect.y]

    def reset(self, seed=None, options=None, padding=100, statistics=None):
        self.timestamp = 0
        self.agents = self.possible_agents[:]
        self.game = Game(seed=seed, padding=padding, n_players=self.game.n_players, statistics=statistics)
        observations = {agent: self.observe(agent) for agent in self.agents}
        infos = {agent: {} for agent in self.agents}

        return observations, infos
    
    # Custom reward function (not used in the current implementation)
    def custom_reward(self, rewards, observation, actions, old_observation=None, old_score=None):
        """
        if self.game.ball.x_speed == 0 and self.game.ball.y_speed == 0:
            self.steps_stopped_ball += 1
        else:
            self.steps_stopped_ball = 0
        """
        c = 0
        while c < len(self.agents):
            agent = self.agents[c]
            # check if the distance between the ball and the player decreased
            old_distance = np.linalg.norm(np.array(old_observation[agent][-2:]) - np.array(old_observation[agent][2*c:2*(c+1)]))
            new_distance = np.linalg.norm(np.array(observation[agent][-2:]) - np.array(observation[agent][2*c:2*(c+1)]))
            if self.game.last_player_ball_collision[c]:
                rewards[agent] += 20
                will_collide = check_collision_route_with_goal(self.game)
                if will_collide is not None:
                    #print(f"Will collide: {will_collide}")
                    if will_collide == self.game.players[c].team:
                        rewards[agent] -= 50
                    else:
                        rewards[agent] += 50

            # TRAIN THE AGENT TO HIT THE BALL
            if new_distance < old_distance and actions[agent] != DONT_MOVE:
                rewards[agent] += np.exp(-0.5 * new_distance) * 10_000 + 0.1
            else:
                rewards[agent] -= 0.1
            
            #if rewards[agent] > 0.3:
                #print(f"Calculating reward for agent {agent}: {rewards[agent]}")
            """
            if new_distance != 0:
                rewards[agent] += np.exp(-0.5 * new_distance) * 1_000
            # check if the ball is stopped for a long time
            if new_distance < old_distance and actions[agent] != DONT_MOVE:
                # give reward to the player that got closer to the ball
                # decrease the reward according to the epsilon 
                rewards[agent] += 0.1 / max(1, (old_distance - new_distance))
            else:
                rewards[agent] += -0.001 * self.steps_stopped_ball
            # round the rewards to 5 decimal places
            if self.steps_stopped_ball > 1000:
                rewards[agent] += -0.01 
            rewards[agent] = round(rewards[agent], 5)
            """
            c += 1
        return rewards
    


    def check_rewards(self, state, done, truncations):
        rewards = {}
        for i, agent in enumerate(self.agents):
            if state is None:
                rewards[agent] = 0
            elif state == self.game.players[i].team:
                rewards[agent] = 100
            else:
                rewards[agent] = -100
            # if all(truncations.values()):
            #    rewards[agent] = -1
        return rewards
        
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
        old_score = self.game.score[:]
        state = self.game.move()
        if state is not None:
            self.timestamp = 0
        done = self.game.score[0] == MAX_SCORE or self.game.score[1] == MAX_SCORE
        # stop the game after 5 touches
        # done = False
        # if self.game.n_touches > 4:
        #     done = True
        observation = {}
        terminations = {}
        truncations = {}
        infos = {}
        for agent in self.agents:
            observation.update({agent: self.observe(agent)})
            terminations.update({agent: done})
            truncations.update({agent: self.timestamp > self.timestep_limit})
            infos.update({agent: {}})
        rewards = self.check_rewards(state, done, truncations)
        rewards = self.custom_reward(rewards, observation, actions, old_observation, old_score=old_score)
        # When in human mode, check if user closed the window
        if self.render_mode == "human":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    truncations = {agent: True for agent in self.agents}

        self.timestamp += 1
        if any(terminations.values()) or all(truncations.values()):
            self.agents = []
        
        if all(truncations.values()):
            self.game.statistics.update_truncated()
        
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
        return gymnasium.spaces.MultiDiscrete([800, 600]*(self.game.n_players + 1))

    # Action space should be defined here.
    # If your spaces change over time, remove this line (disable caching).
    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return gymnasium.spaces.Discrete(5)  # 5 possible actions: up, down, left, right, None