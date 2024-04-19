from .player import Player
from .ball import Ball
from .constants import *

import pygame

class Game:
    def __init__(self):
        start_padding = 250
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
        if self.ball.rect.collidelist(self.goals) == 1: # team 1 scores
            self.score_goal(1)
            return 1
        elif self.ball.rect.collidelist(self.goals) == 0: # team 2 scores
            self.score_goal(0)
            return 2
        return 0

    def score_goal(self, team):
        # update score
        self.score[team] += 1
        print(f"Goal scored: {self.score[0]} - {self.score[1]}")
        # reset ball and player positions
        for player in self.players:
            player.reset_position()
        self.ball.reset_position()

    def check_ball_bounce(self):
        undo_move = False
        top_bot_collision = self.ball.rect.collidelist([self.walls[0], self.walls[2]])
        left_right_collision = self.ball.rect.collidelist([self.walls[1], self.walls[3]])

        if top_bot_collision != -1: # if ball collides with top or bottom walls, reverse y_speed
            print("Ball collision with wall")
            self.ball.undo()
            undo_move = True
            self.ball.y_speed = -self.ball.y_speed
        if left_right_collision != -1: # if ball collides with left or right walls, reverse x_speed
            print("Ball collision with wall")
            if not undo_move:
                self.ball.undo()
            self.ball.x_speed = -self.ball.x_speed
        if undo_move:
            self.ball.move()

    def move(self):
        # move, check collisions and reverse invalid moves
        for i in range(len(self.players)):
            # check player collisions with walls and other players
            self.players[i].move()
            if self.players[i].rect.collidelist(self.players[:i] + self.players[i+1:]) != -1 or self.players[i].rect.collidelist(self.walls) != -1:
                # print("Player collision")
                self.players[i].undo()
            # check player collisions with ball
            if self.players[i].rect.colliderect(self.ball.rect):
                # print old ball speed
                print(self.ball.x_speed, self.ball.y_speed)
                self.ball.x_speed = ((self.ball.rect.centerx - self.ball.x_speed) - (self.players[i].rect.centerx - self.players[i].x_speed)) 
                self.ball.y_speed = ((self.ball.rect.centery - self.ball.y_speed) - (self.players[i].rect.centery - self.players[i].y_speed)) 
                norm = abs(self.ball.x_speed) + abs(self.ball.y_speed)
                if norm != 0:
                    self.ball.x_speed = (self.ball.x_speed / norm) * BALL_SPEED
                    self.ball.y_speed = (self.ball.y_speed / norm) * BALL_SPEED
                # print new ball speed
                print(self.ball.x_speed, self.ball.y_speed)
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
        self.screen.fill(COLORS["black"])
        for player in self.players:
            player.render(self.screen)
        for wall in self.walls:
            pygame.draw.rect(self.screen, COLORS["white"], wall)
        for goal in self.goals:
            pygame.draw.rect(self.screen, COLORS["blue"], goal)
        self.ball.render(self.screen)

        pygame.display.flip()

        return self.screen
