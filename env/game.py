from .player import Player
from .ball import Ball
from .constants import *

import pygame

class Game:
    def __init__(self):
        start_padding = 200
        self.players = [
            Player("player1", start_padding, SCREEN_HEIGHT - (start_padding + PLAYER_HEIGHT), "team1", COLORS["red"]),
            Player("player2", SCREEN_WIDTH - (start_padding + PLAYER_WIDTH), SCREEN_HEIGHT - (start_padding + PLAYER_HEIGHT), "team2", COLORS["green"]),
            Player("player3", start_padding, start_padding, "team1", COLORS["red"]),
            Player("player4", SCREEN_WIDTH - (start_padding + PLAYER_WIDTH), start_padding, "team2", COLORS["green"]),
        ]
        self.ball = Ball(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, BALL_RADIUS)
        self.walls = [pygame.Rect(0, 0, SCREEN_WIDTH, 10), pygame.Rect(0, 0, 10, SCREEN_HEIGHT), pygame.Rect(0, 590, SCREEN_WIDTH, 10), pygame.Rect(790, 0, 10, SCREEN_HEIGHT)]
        # goals are in the middle of the left and right walls
        self.goals = [pygame.Rect(0, SCREEN_HEIGHT/2 - GOAL_HEIGHT/2, BORDER_WIDTH, GOAL_HEIGHT), pygame.Rect(790, SCREEN_HEIGHT/2 - GOAL_HEIGHT/2, BORDER_WIDTH, GOAL_HEIGHT)]
        self.score = [0, 0]
        self.done = False
        self.winner = None
        self.screen = None

    def check_goal(self):
        # if ball collides with goals, score and reset ball and player positions
        # check left goal
        if self.ball.rect.x <= self.goals[0].right:
            if self.ball.rect.y >= self.goals[0].top and (self.ball.rect.y + self.ball.rect.width) <= self.goals[0].bottom:
                self.score_goal(1)
                return 1
        # check right goal
        if (self.ball.rect.x + self.ball.rect.width) >= self.goals[1].left:
            if self.ball.rect.y >= self.goals[1].top and (self.ball.rect.y + self.ball.rect.width) <= self.goals[1].bottom:
                self.score_goal(0)
                return 2
        return 0

    def score_goal(self, team: int):
        # update score
        self.score[team] += 1
        print(f"Goal scored: {self.score[0]} - {self.score[1]}")
        # reset ball and player positions
        for player in self.players:
            player.reset_position()
        self.ball.reset_position()

    def check_ball_bounce(self):
        # check collision with left wall
        if self.ball.rect.x <= self.walls[1].right:
            self.ball.x_speed = -self.ball.x_speed  # reverse x speed
            # undo the move and position the ball in contact with the wall
            self.ball.rect.x = self.walls[1].right
        # check collision with right wall
        if (self.ball.rect.x + self.ball.rect.width) >= self.walls[3].left:
            self.ball.x_speed = -self.ball.x_speed # reverse x speed
            # undo the move and position the ball in contact with the wall
            self.ball.rect.x = self.walls[3].left - self.ball.rect.width
        # check collision with top wall
        if self.ball.rect.y <= self.walls[0].bottom:
            self.ball.y_speed = -self.ball.y_speed # reverse y speed
            # undo the move and position the ball in contact with the wall
            self.ball.rect.y = self.walls[0].bottom
        # check collision with bottom wall
        if (self.ball.rect.y + self.ball.rect.height) >= self.walls[2].top:
            self.ball.y_speed = -self.ball.y_speed # reverse y speed
            # undo the move and position the ball in contact with the wall
            self.ball.rect.y = self.walls[2].top - self.ball.rect.height


    def move(self):
        # move, check collisions and reverse invalid moves
        for i, player in enumerate(self.players):
            # check player collisions with walls and other players
            player.move()
            if player.rect.collidelist(self.players[:i] + self.players[i+1:]) != -1 or player.rect.collidelist(self.walls) != -1:
                # print("Player collision")
                player.undo()
            # check player collisions with ball
            if player.rect.colliderect(self.ball.rect):
                print("Old speed", self.ball.x_speed, self.ball.y_speed)
                self.ball.x_speed = ((self.ball.rect.centerx - self.ball.x_speed) - (self.players[i].rect.centerx - self.players[i].x_speed))
                self.ball.y_speed = ((self.ball.rect.centery - self.ball.y_speed) - (self.players[i].rect.centery - self.players[i].y_speed))
                self.ball.normalize_speed()
                print("New speed", self.ball.x_speed, self.ball.y_speed)
        # check ball collisions with goal and walls
        self.ball.move()
        state = self.check_goal()
        if state == 0:
            self.check_ball_bounce()
        return state

    def render(self):
        if self.screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode(DISPLAY_SIZE)
            pygame.display.set_caption("Footpong")
        self.screen.fill(COLORS["black"])
        for player in self.players:
            player.render(self.screen)
        for wall in self.walls:
            pygame.draw.rect(self.screen, COLORS["orange"], wall)
        for goal in self.goals:
            pygame.draw.rect(self.screen, COLORS["blue"], goal)
        self.ball.render(self.screen)

        pygame.display.flip()

        return self.screen
