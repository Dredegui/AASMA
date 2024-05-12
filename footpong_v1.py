import env.footpong
from env.constants import *


from agents.greedy_agent import GreedyAgent
from agents.random_agent import RandomAgent
from agents.hard_coded_agent import HardCodedAgent
from agents.goal_keeper_agent import GoalKeeperAgent
from agents.role_agent import RoleAgent

if __name__ == "__main__":
    env = env.footpong.footpong(render_mode="human")
    env.render()
    observations, _ = env.reset(seed=42)

    roles = {
        "defender": GoalKeeperAgent,
        "attacker": HardCodedAgent
    }

    agents = [
        RoleAgent("player1", 1, roles),
        RoleAgent("player2", 2, roles),
        RoleAgent("player3", 3, roles),
        RoleAgent("player4", 4, roles),
    ]

    while env.agents:
        actions = {}
        for agent in env.agents:
            actions[agent] = agents[env.agent_name_mapping[agent]].act(observations[agent])

        observations, rewards, terminations, truncations, infos = env.step(actions)
        env.render()
    
    env.close()