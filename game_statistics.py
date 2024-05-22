# Description: This file contains the Statistics class which is responsible for keeping track of the statistics of the game.

import json
import numpy as np
from env.constants import *

class GameStatistics:

    def __init__(self, players):
        self.players = players
        self.score = [0, 0]
        self.truncated = False
        self.ball_touches = {player: 0 for player in players}
        self.goals = {player: 0 for player in players}
        self.own_goals = {player: 0 for player in players}
        self.saves = {player: 0 for player in players}
        self.blocked_shots = {player: 0 for player in players}
        self.assists = {player: 0 for player in players}
        self.shots = {player: 0 for player in players}
        self.direct_shots = {player: 0 for player in players}
        self.passes = {player: 0 for player in players}
        self.heat_map = {player: np.zeros((6, 8), dtype=int) for player in players}

    # Template method to update the statistics
    def update_stat(self, stat_dict, player):
        if player in stat_dict:
            stat_dict[player] += 1

    def update_ball_touches(self, player):
        self.update_stat(self.ball_touches, player)

    def update_goals(self, player):
        self.update_stat(self.goals, player)

    def update_own_goals(self, player):
        self.update_stat(self.own_goals, player)

    def update_saves(self, player):
        self.update_stat(self.saves, player)

    def update_blocked_shots(self, player):
        self.update_stat(self.blocked_shots, player)

    def update_assists(self, player):
        self.update_stat(self.assists, player)

    def update_shots(self, player):
        self.update_stat(self.shots, player)

    def update_direct_shots(self, player):
        self.update_stat(self.direct_shots, player)

    def update_passes(self, player):
        self.update_stat(self.passes, player)

    def update_heat_map(self, player, x, y):
        # map coordinates to the heat map where x is between 0 and 800 and y is between 0 and 600
        x = int(x / SCREEN_WIDTH * self.heat_map[player].shape[1])
        y = int(y / SCREEN_HEIGHT * self.heat_map[player].shape[0])
        self.heat_map[player][y][x] += 1

    def print_heat_map(self):
        for player in self.players:
            print(f"Heat map for player {player}:")
            print(self.heat_map[player])

    def update_score(self, team):
        self.score[team] += 1

    def update_truncated(self):
        self.truncated = True

    def print_statistics(self):
        print(self)

    def __str__(self) -> str:
        players = "\t\t"
        ball_t = "Ball touches:\t"
        goals = "Goals:\t\t"
        own_goals = "Own goals:\t"
        saves = "Saves:\t\t"
        blocked_shots = "Blocked shots:\t"
        assists = "Assists:\t"
        shots = "Shots:\t\t"
        direct_shots = "Direct shots:\t"
        passes = "Passes:\t\t"

        for player in self.players:
            players += f"{player}\t"
            ball_t += f"{self.ball_touches[player]}\t"
            goals += f"{self.goals[player]}\t"
            own_goals += f"{self.own_goals[player]}\t"
            saves += f"{self.saves[player]}\t"
            blocked_shots += f"{self.blocked_shots[player]}\t"
            assists += f"{self.assists[player]}\t"
            shots += f"{self.shots[player]}\t"
            direct_shots += f"{self.direct_shots[player]}\t"
            passes += f"{self.passes[player]}\t"

        return f"{players}\n{ball_t}\n{goals}\n{own_goals}\n{saves}\n{blocked_shots}\n{shots}\n{direct_shots}\n{assists}\n{passes}\nScore: {self.score}\nTruncated: {self.truncated}\n{self.print_heat_map()}"

    def save(self):
        with open("statistics.json", "w") as f:
            json.dump(self.__dict__, f, default=lambda x: x.tolist())

    def get_dict(self):
        dict = {
            "score": self.score,
            "truncated": self.truncated
        }
        for player in self.players:
            dict[player] = {
                "ball_touches": self.ball_touches[player],
                "goals": self.goals[player],
                "own_goals": self.own_goals[player],
                "saves": self.saves[player],
                "blocked_shots": self.blocked_shots[player],
                "assists": self.assists[player],
                "shots": self.shots[player],
                "direct_shots": self.direct_shots[player],
                "passes": self.passes[player],
                "heat_map": self.heat_map[player].tolist()
            }
        return dict
