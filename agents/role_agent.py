from agents.agent import Agent
from env.constants import *

class RoleAgent(Agent):
    def __init__(self, name, agent_id, roles, role_assign_period=20):
        super().__init__(name, agent_id)
        self.roles = roles
        self.role = None
        self.steps = 0
        self.role_assign_period = role_assign_period

    def _calculate_potential(self, player_pos, goal_pos):
        # calculate the distance between the player and the goal
        return abs(player_pos[0] - goal_pos[0]) + abs(player_pos[1] - goal_pos[1])
    
    def _role_assignement(self, observation):
        players = observation[:-2]

        # get the players in the team
        player_idx = (self.agent_id - 1) * 2
        teammate_idx = (player_idx + 4) % len(players)

        players_team = [
            players[player_idx:player_idx+2],
            players[teammate_idx:teammate_idx+2]      
        ]

        potentials = []
        for player_cords in players_team:
            goal = [0, SCREEN_HEIGHT/2] if self.agent_id == 1 or self.agent_id == 3 else [SCREEN_WIDTH, SCREEN_HEIGHT/2]
            potentials.append(self._calculate_potential(player_cords, goal))

        # assign the roles
        if potentials[0] < potentials[1]:
            self.role = self.roles['defender']
        else:
            self.role = self.roles['attacker']
        

    def act(self, observation):
        if self.steps % self.role_assign_period == 0:
            self._role_assignement(observation)
        self.steps += 1

        return self.role(self.name, self.agent_id).act(observation)