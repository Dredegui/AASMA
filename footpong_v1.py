from env.constants import *
import env.footpong
import json
import pickle

from agents.greedy_agent import GreedyAgent
from agents.random_agent import RandomAgent
from agents.balanced_agent import BalancedAgent
from agents.goal_keeper_agent import GoalKeeperAgent
from agents.role_agent import RoleAgent
from game_statistics import GameStatistics

import time

if __name__ == "__main__":
    env = env.footpong.footpong(render_mode="human")
    env.render()

    statistics = []

    roles = {
        "defender": GoalKeeperAgent,
        "attacker": BalancedAgent,
    }

    agents = [
        RoleAgent("player1", 1, roles),
        RoleAgent("player2", 2, roles),
        RoleAgent("player3", 3, roles),
        RoleAgent("player4", 4, roles),
    ]


    for i in range(50):
        observations, _ = env.reset(seed=42)
        statistics.append(GameStatistics(env.agents))
        env.game.set_statistics(statistics[-1])
        while env.agents:
            actions = {}
            for agent in env.agents:
                actions[agent] = agents[env.agent_name_mapping[agent]].act(observations[agent])

            observations, rewards, terminations, truncations, infos = env.step(actions)
            env.render()
        statistics[-1].print_statistics()
        print(f"Game {i} finished")

    if statistics is not None:
        statistics = [s.get_dict() for s in statistics]
        statistics_dict = {game: statistics[game] for game in range(len(statistics))}
        print(statistics_dict)
        with open("statistics.json", "w") as f:
            json.dump(statistics_dict, f)
        # dump pickle
        with open("statistics.pkl", "wb") as f:
            pickle.dump(statistics_dict, f)
    env.close()
