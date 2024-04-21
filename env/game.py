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
        self.walls = {
            "top": pygame.Rect(0, 0, SCREEN_WIDTH, BORDER_WIDTH),
            "bottom": pygame.Rect(0, SCREEN_HEIGHT - BORDER_WIDTH, SCREEN_WIDTH, BORDER_WIDTH),
            "left_top": pygame.Rect(0, 0, BORDER_WIDTH, SCREEN_HEIGHT/2 - GOAL_HEIGHT/2),
            "left_bottom": pygame.Rect(0, SCREEN_HEIGHT/2 + GOAL_HEIGHT/2, BORDER_WIDTH, SCREEN_HEIGHT/2 - GOAL_HEIGHT/2),
            "right_top": pygame.Rect(SCREEN_WIDTH - BORDER_WIDTH, 0, BORDER_WIDTH, SCREEN_HEIGHT/2 - GOAL_HEIGHT/2),
            "right_bottom": pygame.Rect(SCREEN_WIDTH - BORDER_WIDTH, SCREEN_HEIGHT/2 + GOAL_HEIGHT/2, BORDER_WIDTH, SCREEN_HEIGHT/2 - GOAL_HEIGHT/2),
        }
        self.score = [0, 0]
        self.done = False
        self.winner = None
        self.screen = None

    def check_goal(self):
        # check left goal
        if self.ball.rect.x + self.ball.rect.width < 0:
            self.score_goal(1)
            return 1

        # check right goal
        if self.ball.rect.x > SCREEN_WIDTH:
            self.score_goal(0)
            return 1
        
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
        # check collision with left_top wall
        if self.ball.rect.colliderect(self.walls["left_top"]):
            self.ball.x_speed = -self.ball.x_speed
            self.ball.rect.x = self.walls["left_top"].right
        # check collision with left_bottom wall
        if self.ball.rect.colliderect(self.walls["left_bottom"]):
            self.ball.x_speed = -self.ball.x_speed
            self.ball.rect.x = self.walls["left_bottom"].right
        # check collision with right_top wall
        if self.ball.rect.colliderect(self.walls["right_top"]):
            self.ball.x_speed = -self.ball.x_speed
            self.ball.rect.x = self.walls["right_top"].left - self.ball.rect.width
        # check collision with right_bottom wall
        if self.ball.rect.colliderect(self.walls["right_bottom"]):
            self.ball.x_speed = -self.ball.x_speed
            self.ball.rect.x = self.walls["right_bottom"].left - self.ball.rect.width
        # check collision with top wall
        if self.ball.rect.y <= self.walls["top"].bottom:
            self.ball.y_speed = -self.ball.y_speed
            self.ball.rect.y = self.walls["top"].bottom
        # check collision with bottom wall
        if (self.ball.rect.y + self.ball.rect.height) >= self.walls["bottom"].top:
            self.ball.y_speed = -self.ball.y_speed
            self.ball.rect.y = self.walls["bottom"].top - self.ball.rect.height


    def move(self):
        # move, check collisions and reverse invalid moves
        for i, player in enumerate(self.players):
            # check player collisions with walls and other players
            player.move()
            if player.rect.collidelist(self.players[:i] + self.players[i+1:]) != -1 or player.rect.collidelist(list(self.walls.values())) != -1 \
            or player.rect.x < 0 or player.rect.x + player.rect.width > SCREEN_WIDTH:
                player.undo()
            # check player collisions with ball
            if player.rect.colliderect(self.ball.rect):
                self.ball.x_speed = ((self.ball.rect.centerx - self.ball.x_speed) - (self.players[i].rect.centerx - self.players[i].x_speed))
                self.ball.y_speed = ((self.ball.rect.centery - self.ball.y_speed) - (self.players[i].rect.centery - self.players[i].y_speed))
                self.ball.normalize_speed()
        # check ball collisions with goal and walls
        self.ball.move()
        state = self.check_goal()
        if state == 0:
            self.check_ball_bounce()
        return state

    def render(self, mode="human"):
        if mode == "human":
            if self.screen is None:
                pygame.init()
                self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                pygame.display.set_caption("Footpong")
            self.screen.fill(COLORS["black"])
            for player in self.players:
                player.render(self.screen)
            for wall in self.walls.values():
                pygame.draw.rect(self.screen, COLORS["orange"], wall)
            self.ball.render(self.screen)

            pygame.display.flip()

            return self.screen

        if mode == "rgb_array":
            if self.screen is None:
                self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screen.fill(COLORS["black"])
            for player in self.players:
                player.render(self.screen)
            for wall in self.walls.values():
                pygame.draw.rect(self.screen, COLORS["orange"], wall)
            self.ball.render(self.screen)

            return pygame.surfarray.array3d(self.screen)
