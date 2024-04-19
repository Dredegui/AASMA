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
        self.walls = [pygame.Rect(0, 0, 800, 10), pygame.Rect(0, 0, 10, 600), pygame.Rect(0, 590, 800, 10), pygame.Rect(790, 0, 10, 600)]
        # goals are in the middle of the left and right walls
        self.goals = [pygame.Rect(0, 250, 10, 100), pygame.Rect(790, 250, 10, 100)]
        self.ball = Ball(400, 300, 10)
        self.score = [0, 0]
        self.done = False
        self.winner = None
        self.screen = None

    def check_winner(self):
        # if ball collides with goals, score and reset ball position
        if self.ball.rect.collidelist(self.goals) == 1: # team 1 wins
            print("Goal scored")
            self.score[1] += 1
            self.ball = Ball(400, 300, 10)
            return 1
        elif self.ball.rect.collidelist(self.goals) == 0: # team 2 wins
            print("Goal scored")
            self.score[0] += 1
            self.ball = Ball(400, 300, 10)
            return 2
        else:
            return 0
        
    def check_ball_bounce(self):
        undo_move = False
        if self.ball.rect.collidelist(self.walls) in [1, 2]: # if ball collides with top or bottom walls, reverse y_speed
            print("Ball collision with wall")
            self.ball.undo()
            undo_move = True
            self.ball.y_speed = -self.ball.y_speed
        if self.ball.rect.collidelist(self.walls) in [0, 3]: # if ball collides with left or right walls, reverse x_speed
            print("Ball collision with wall")
            if not undo_move:
                self.ball.undo()
            self.ball.x_speed = -self.ball.x_speed
        if undo_move:
            self.ball.move()

    def move(self):
        # move, check collisions and reverse unvalid moves
        for i in range(len(self.players)):
            # check player collisions with walls and other players
            self.players[i].move()
            if self.players[i].rect.collidelist(self.players[:i] + self.players[i+1:]) != -1 or self.players[i].rect.collidelist(self.walls) != -1:
                print("Player collision")
                self.players[i].undo()
            # check player collisions with ball
            if self.players[i].rect.colliderect(self.ball.rect):
                print("Player with Ball collision")
                self.ball.x_speed = self.ball.rect.centerx - self.players[i].rect.centerx 
                self.ball.y_speed = self.ball.rect.centery - self.players[i].rect.centery
        # check ball collisions with goal and walls
        self.ball.move()
        state = self.check_winner()
        self.check_ball_bounce()
        return state        

    def render(self):
        if self.screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((800, 600))
        self.screen.fill((0, 0, 0))
        for player in self.players:
            player.render(self.screen)
        for wall in self.walls:
            pygame.draw.rect(self.screen, Colors["white"], wall)
        for goal in self.goals:
            pygame.draw.rect(self.screen, Colors["blue"], goal)
        self.ball.render(self.screen)

        pygame.display.flip()

        return self.screen
