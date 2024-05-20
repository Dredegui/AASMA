# Description: This file contains the Statistics class which is responsible for keeping track of the statistics of the game.

import json


class GameStatistics:

    def __init__(self, players):
        self.players = players
        self.ball_touches = {player: 0 for player in players}
        self.goals = {player: 0 for player in players}
        self.saves = {player: 0 for player in players}
        self.assists = {player: 0 for player in players}
        self.direct_shots = {player: 0 for player in players}
        self.passes = {player: 0 for player in players}
        #self.heat_map = {}

    # Template method to update the statistics
    def update_stat(self, stat_dict, player):
        if player in stat_dict:
            stat_dict[player] += 1

    def update_ball_touches(self, player):
        self.update_stat(self.ball_touches, player)

    def update_goals(self, player):
        self.update_stat(self.goals, player)

    def update_saves(self, player):
        self.update_stat(self.saves, player)

    def update_assists(self, player):
        self.update_stat(self.assists, player)

    def update_direct_shots(self, player):
        self.update_stat(self.direct_shots, player)

    def update_passes(self, player):
        self.update_stat(self.passes, player)

    # Getters are not necessary

    def print_statistics(self):
        print(self)

    def __str__(self) -> str:
        players = "\t\t"
        ball_t = "Ball touches:\t"
        goals = "Goals:\t\t"
        saves = "Saves:\t\t"
        assists = "Assists:\t"
        direct_shots = "Direct shots:\t"
        passes = "Passes:\t\t"

        for player in self.players:
            players += f"{player}\t"
            ball_t += f"{self.ball_touches[player]}\t"
            goals += f"{self.goals[player]}\t"
            saves += f"{self.saves[player]}\t"
            assists += f"{self.assists[player]}\t"
            direct_shots += f"{self.direct_shots[player]}\t"
            passes += f"{self.passes[player]}\t"

        return f"{players}\n{ball_t}\n{goals}\n{saves}\n{assists}\n{direct_shots}\n{passes}"

    def save(self):
        with open("statistics.json", "w") as f:
            json.dump(self.__dict__, f, indent=4)
