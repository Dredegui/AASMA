from .player import Player
from .ball import Ball
from .constants import *
import numpy as np

import pygame
import cv2

class Game:
    def __init__(self, seed=None):
        self.seed = seed
        start_padding = 200
        coords = [[start_padding, SCREEN_HEIGHT - (start_padding + PLAYER_HEIGHT)],
                  [SCREEN_WIDTH - (start_padding + PLAYER_WIDTH), SCREEN_HEIGHT - (start_padding + PLAYER_HEIGHT)],
                  [start_padding, start_padding],
                  [SCREEN_WIDTH - (start_padding + PLAYER_WIDTH), start_padding],
                  [SCREEN_WIDTH/2, SCREEN_HEIGHT/2]]
        print(coords)
        if seed is not None:
            # generate random coordinates that are not too close to the walls or each other
            coords = self.randomize_positions(coords, start_padding)
        print(coords)
        self.players = [Player(f"player{i+1}", coords[i][0], coords[i][1], f"team{i%2 + 1}", COLORS["red"] if i%2 == 0 else COLORS["green"]) for i in range(4)]
        self.ball = Ball(coords[4][0], coords[4][1], BALL_RADIUS)
        self.walls = {
            "top": pygame.Rect(0, 0, SCREEN_WIDTH, BORDER_WIDTH),
            "bottom": pygame.Rect(0, SCREEN_HEIGHT - BORDER_WIDTH, SCREEN_WIDTH, BORDER_WIDTH),
            "left_top": pygame.Rect(0, 0, BORDER_WIDTH, GOAL_TOP),
            "left_bottom": pygame.Rect(0, GOAL_BOTTOM, BORDER_WIDTH, GOAL_TOP),
            "right_top": pygame.Rect(SCREEN_WIDTH - BORDER_WIDTH, 0, BORDER_WIDTH, GOAL_TOP),
            "right_bottom": pygame.Rect(SCREEN_WIDTH - BORDER_WIDTH, GOAL_BOTTOM, BORDER_WIDTH, GOAL_TOP),
        }
        self.score = [0, 0]
        self.last_player_ball_collision = {i: False for i in range(4)}
        self.screen = None

    def randomize_positions(self, coords, start_padding=200):
        for i in range(4):
                x = np.random.randint(start_padding, SCREEN_WIDTH - start_padding - PLAYER_WIDTH)
                y = np.random.randint(start_padding, SCREEN_HEIGHT - start_padding - PLAYER_HEIGHT)
                while any([np.sqrt((x - c[0])**2 + (y - c[1])**2) < 2*PLAYER_WIDTH for c in coords]):
                    x = np.random.randint(start_padding, SCREEN_WIDTH - start_padding - PLAYER_WIDTH)
                    y = np.random.randint(start_padding, SCREEN_HEIGHT - start_padding - PLAYER_HEIGHT)
                coords[i] = [x, y]
        return coords

    def check_goal(self):
        # check left goal
        if self.ball.rect.x + BALL_DIAMETER < 0:
            self.score_goal(1)
            return 2
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
        ball_above_goal = True if self.ball.rect.y <= GOAL_TOP else False
        ball_bellow_goal = True if self.ball.rect.y + BALL_DIAMETER >= GOAL_BOTTOM else False
        ball_beyond_left_border = True if self.ball.rect.x <= BORDER_WIDTH else False
        ball_beyond_right_border = True if self.ball.rect.x + BALL_DIAMETER >= SCREEN_WIDTH - BORDER_WIDTH else False
        # if the ball in its previous position was between the goals and in the current
        # position touches a side wall, then it should bounce vertically and not horizontally
        previous_y = self.ball.rect.centery - self.ball.y_speed
        vertical_bounce = True if previous_y > GOAL_TOP and previous_y < GOAL_BOTTOM else False

        # check collision with left_top wall
        if ball_beyond_left_border and ball_above_goal:
            # check if the ball is moving towards the bottom side of the wall
            if vertical_bounce:
                self.ball.y_speed = -self.ball.y_speed
                self.ball.rect.y = self.walls["left_top"].bottom
            else:
                self.ball.x_speed = -self.ball.x_speed
                self.ball.rect.x = self.walls["left_top"].right

        # check collision with left_bottom wall
        if ball_beyond_left_border and ball_bellow_goal:
            # check if the ball is moving towards the top side of the wall
            if vertical_bounce:
                self.ball.y_speed = -self.ball.y_speed
                self.ball.rect.y = self.walls["left_bottom"].top - BALL_DIAMETER
            else:
                self.ball.x_speed = -self.ball.x_speed
                self.ball.rect.x = self.walls["left_bottom"].right

        # check collision with right_top wall
        if ball_beyond_right_border and ball_above_goal:
            # check if the ball is moving towards the bottom side of the wall
            if vertical_bounce:
                self.ball.y_speed = -self.ball.y_speed
                self.ball.rect.y = self.walls["right_top"].bottom
            else:
                self.ball.x_speed = -self.ball.x_speed
                self.ball.rect.x = self.walls["right_top"].left - BALL_DIAMETER

        # check collision with right_bottom wall
        if ball_beyond_right_border and ball_bellow_goal:
            # check if the ball is moving towards the top side of the wall
            if vertical_bounce:
                self.ball.y_speed = -self.ball.y_speed
                self.ball.rect.y = self.walls["right_bottom"].top - BALL_DIAMETER
            else:
                self.ball.x_speed = -self.ball.x_speed
                self.ball.rect.x = self.walls["right_bottom"].left - BALL_DIAMETER

        # check collision with top wall
        if self.ball.rect.y <= self.walls["top"].bottom:
            self.ball.y_speed = -self.ball.y_speed
            self.ball.rect.y = self.walls["top"].bottom

        # check collision with bottom wall
        if (self.ball.rect.y + BALL_DIAMETER) >= self.walls["bottom"].top:
            self.ball.y_speed = -self.ball.y_speed
            self.ball.rect.y = self.walls["bottom"].top - BALL_DIAMETER


    def move(self):
        # move, check collisions and reverse invalid moves
        for i, player in enumerate(self.players):
            # check player collisions with walls and other players
            player.move()
            if player.rect.collidelist(self.players[:i] + self.players[i+1:]) != -1 \
                    or player.rect.collidelist(list(self.walls.values())) != -1 \
                    or player.rect.x < 0 or player.rect.x + player.rect.width > SCREEN_WIDTH:
                player.undo()
            # check player collisions with ball
            if player.rect.colliderect(self.ball.rect):
                self.last_player_ball_collision[i] = True
                self.ball.x_speed = ((self.ball.rect.centerx - self.ball.x_speed) - (self.players[i].rect.centerx - self.players[i].x_speed))
                self.ball.y_speed = ((self.ball.rect.centery - self.ball.y_speed) - (self.players[i].rect.centery - self.players[i].y_speed))
                self.ball.normalize_speed()
            else:
                self.last_player_ball_collision[i] = False
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

            array = pygame.surfarray.array3d(self.screen)
            array = cv2.rotate(array, cv2.ROTATE_90_CLOCKWISE)
            array = cv2.flip(array, 1)
            return array

