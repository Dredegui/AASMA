from .player import Player
from .ball import Ball
from .constants import Colors

import pygame

class Game:
    def __init__(self):
        self.players = [
            Player("player1", 10, 300, "team1", Colors["red"]),
            Player("player2", 780, 300, "team2", Colors["green"]),
            Player("player3", 10, 10, "team1", Colors["red"]),
            Player("player4", 780, 10, "team2", Colors["green"]),
        ]
        self.ball = Ball(400, 300, 10)
        self.score = [0, 0]
        self.done = False
        self.winner = None
        self.screen = None

    def move(self):
        for player in self.players:
            player.move()
        self.ball.move()

    def render(self):
        if self.screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((800, 600))

        for player in self.players:
            player.render(self.screen)
        self.ball.render(self.screen)

        pygame.display.flip()

        return self.screen
