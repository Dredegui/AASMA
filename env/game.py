from .player import Player
from .ball import Ball
from .constants import *
from fifo_queue import Fifo
import numpy as np
from copy import deepcopy

import pygame
import cv2

class Game:
    def __init__(self, seed=None, padding=100, n_players=4, learning_mode=False, statistics=None):
        self.seed = seed
        start_padding = padding
        self.n_players = n_players
        self.statistics = statistics
        #coords = [[start_padding, SCREEN_HEIGHT - (start_padding + PLAYER_HEIGHT)],
        #          [SCREEN_WIDTH - (start_padding + PLAYER_WIDTH), SCREEN_HEIGHT - (start_padding + PLAYER_HEIGHT)],
        #          [start_padding, start_padding],
        #          [SCREEN_WIDTH - (start_padding + PLAYER_WIDTH), start_padding],
        #          [SCREEN_WIDTH/2, SCREEN_HEIGHT/2]]
        coords = [
            [SCREEN_WIDTH/4, SCREEN_HEIGHT/2-padding-PLAYER_HEIGHT],
            [SCREEN_WIDTH - SCREEN_WIDTH/4 - PLAYER_WIDTH/2, SCREEN_HEIGHT/2-padding-PLAYER_HEIGHT],
            [SCREEN_WIDTH/4, SCREEN_HEIGHT/2+padding],
            [SCREEN_WIDTH - SCREEN_WIDTH/4 - PLAYER_WIDTH/2, SCREEN_HEIGHT/2+padding],
            
            [SCREEN_WIDTH/2 - BALL_RADIUS, SCREEN_HEIGHT/2 - BALL_RADIUS]
        ]
        coords = coords[: n_players] + [[SCREEN_WIDTH/2, SCREEN_HEIGHT/2]]
        
        if seed is not None:
            # generate random coordinates that are not too close to the walls or each other 
            if learning_mode:
                coords = self.randomize_positions_learning(coords, start_padding)
            else:
                coords = self.randomize_positions(coords)
        self.players = [Player(f"player{i+1}", coords[i][0], coords[i][1], PLAYER_TEAM_LEFT if i%2 == 0 else PLAYER_TEAM_RIGHT, COLORS["red"] if i%2 == 0 else COLORS["green"]) for i in range(self.n_players)]
        self.ball = Ball(coords[n_players][0], coords[n_players][1], BALL_RADIUS)
        self.walls = {
            "top": pygame.Rect(0, 0, SCREEN_WIDTH, BORDER_WIDTH),
            "bottom": pygame.Rect(0, SCREEN_HEIGHT - BORDER_WIDTH, SCREEN_WIDTH, BORDER_WIDTH),
            "left_top": pygame.Rect(0, 0, BORDER_WIDTH, GOAL_TOP),
            "left_bottom": pygame.Rect(0, GOAL_BOTTOM, BORDER_WIDTH, GOAL_TOP),
            "right_top": pygame.Rect(SCREEN_WIDTH - BORDER_WIDTH, 0, BORDER_WIDTH, GOAL_TOP),
            "right_bottom": pygame.Rect(SCREEN_WIDTH - BORDER_WIDTH, GOAL_BOTTOM, BORDER_WIDTH, GOAL_TOP),
        }
        self.score = [0, 0]
        self.last_player_ball_collision = {i: False for i in range(self.n_players)}
        self.ball_touches_fifo = Fifo(2)
        self.passes_fifo = Fifo(2)
        self.screen = None
        self.n_touches = 0
        self.timestamp = 0
        self.timestamp_limit = 2_500

    def set_statistics(self, statistics):
        self.statistics = statistics

    def randomize_positions(self, coords, start_padding=50):
        for i in range(self.n_players):
            x = np.random.randint(coords[i][0] - start_padding, coords[i][0] + start_padding)
            y = np.random.randint(coords[i][1] - start_padding, coords[i][1] + start_padding)
            coords[i] = [x, y]
        return coords
    
    def randomize_positions_learning(self, coords, start_padding=100):
        for i in range(self.n_players + 1): # +1 for the ball
            x = np.random.randint(start_padding, SCREEN_WIDTH - start_padding - PLAYER_WIDTH)
            y = np.random.randint(start_padding, SCREEN_HEIGHT - start_padding - PLAYER_HEIGHT)
            while any([np.sqrt((x - c[0])**2 + (y - c[1])**2) < 2*PLAYER_WIDTH for c in coords]):
                x = np.random.randint(start_padding, SCREEN_WIDTH - start_padding - PLAYER_WIDTH)
                y = np.random.randint(start_padding, SCREEN_HEIGHT - start_padding - PLAYER_HEIGHT)
            coords[i] = [x, y]
        return coords

    # update goal, own goal, and assist statistics
    def update_goal_related_statistics(self, team_that_scored: int):
        if self.statistics is not None:
            last_player = self.ball_touches_fifo.get_first()
            if last_player is not None:
                # check if the player scored an own goal
                if last_player.team == team_that_scored:
                    self.statistics.update_goals(last_player.name)
                else:
                    self.statistics.update_own_goals(last_player.name)
            previous_player = self.ball_touches_fifo.get_last_in_max_size()
            if previous_player is not None:
                # check if the player assisted the goal
                if previous_player.team == team_that_scored and previous_player.name != last_player.name and previous_player.team == last_player.team:
                    self.statistics.update_assists(previous_player.name)

    def update_ball_touch_statistics(self, player: Player):
        if self.statistics is not None:
            # FIXME: some ball touches are counted twice
            self.statistics.update_ball_touches(player.name)

    def update_passes_statistics(self, player: Player):
        if self.statistics is not None:
            prev_player = self.passes_fifo.get_last_in_max_size()
            if prev_player is not None and prev_player.team == player.team and prev_player.name != player.name:
                self.statistics.update_passes(prev_player.name)
    
    def update_shot_statistics(self):
        if self.statistics is not None:
            will_score = self.check_collision_route_with_goal()
            last_player = self.ball_touches_fifo.get_first()
            if will_score is not None and last_player is not None and abs(will_score - last_player.team) == 1:
                self.statistics.update_shots(last_player.name)

    def update_direct_shot_statistics(self, player: Player):
        if self.statistics is not None:
            will_score = self.check_collision_route_with_goal()
            if will_score is not None and abs(will_score - player.team) == 1:
                self.statistics.update_direct_shots(player.name)
                self.statistics.update_shots(player.name)
        
    def update_save_statistics(self, player: Player):
        if self.statistics is not None:
            will_score = self.check_collision_route_with_goal()
            prev_player = self.ball_touches_fifo.get_last_in_max_size()
            if not (player.team == PLAYER_TEAM_LEFT and player.rect.x + PLAYER_WIDTH < SCREEN_WIDTH/4 \
                     or player.team == PLAYER_TEAM_RIGHT and player.rect.x > SCREEN_WIDTH - SCREEN_WIDTH/4):
                if prev_player is not None and prev_player.team != player.team and will_score == player.team:
                    self.statistics.update_blocked_shots(player.name)
                return
            if will_score == player.team:
                self.statistics.update_saves(player.name)

    def check_collision_route_with_goal(self):
        ball = self.ball
        if ball.x_speed < 0:
            # check collision with left goal
            nsteps = int(abs(ball.rect.left / ball.x_speed))
            ypredicted = ball.rect.top + nsteps * ball.y_speed
            if ypredicted > GOAL_TOP and ypredicted < GOAL_BOTTOM:
                return PLAYER_TEAM_LEFT
        elif ball.x_speed > 0:
            # check collision with right goal
            nsteps = int(abs((SCREEN_WIDTH - ball.rect.right) / ball.x_speed))
            ypredicted = ball.rect.top + nsteps * ball.y_speed
            if ypredicted > GOAL_TOP and ypredicted < GOAL_BOTTOM:
                return PLAYER_TEAM_RIGHT
        return None

    def check_goal(self):
        # check left goal
        if self.ball.rect.x + BALL_DIAMETER < 0:
            self.update_goal_related_statistics(PLAYER_TEAM_RIGHT)
            self.score_goal(PLAYER_TEAM_RIGHT)
            return PLAYER_TEAM_RIGHT
        # check right goal
        if self.ball.rect.x > SCREEN_WIDTH:
            self.update_goal_related_statistics(PLAYER_TEAM_LEFT)
            self.score_goal(PLAYER_TEAM_LEFT)
            return PLAYER_TEAM_LEFT
        return None

    def score_goal(self, team: int):
        print(f"Statistics:\n{self.statistics}")
        # update score
        self.score[team] += 1
        if self.statistics is not None:
            self.statistics.update_score(team)
        print(f"Goal scored: {self.score[PLAYER_TEAM_LEFT]} - {self.score[PLAYER_TEAM_RIGHT]}")
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
            self.update_shot_statistics()

        # check collision with left_bottom wall
        if ball_beyond_left_border and ball_bellow_goal:
            # check if the ball is moving towards the top side of the wall
            if vertical_bounce:
                self.ball.y_speed = -self.ball.y_speed
                self.ball.rect.y = self.walls["left_bottom"].top - BALL_DIAMETER
            else:
                self.ball.x_speed = -self.ball.x_speed
                self.ball.rect.x = self.walls["left_bottom"].right
            self.update_shot_statistics()

        # check collision with right_top wall
        if ball_beyond_right_border and ball_above_goal:
            # check if the ball is moving towards the bottom side of the wall
            if vertical_bounce:
                self.ball.y_speed = -self.ball.y_speed
                self.ball.rect.y = self.walls["right_top"].bottom
            else:
                self.ball.x_speed = -self.ball.x_speed
                self.ball.rect.x = self.walls["right_top"].left - BALL_DIAMETER
            self.update_shot_statistics()

        # check collision with right_bottom wall
        if ball_beyond_right_border and ball_bellow_goal:
            # check if the ball is moving towards the top side of the wall
            if vertical_bounce:
                self.ball.y_speed = -self.ball.y_speed
                self.ball.rect.y = self.walls["right_bottom"].top - BALL_DIAMETER
            else:
                self.ball.x_speed = -self.ball.x_speed
                self.ball.rect.x = self.walls["right_bottom"].left - BALL_DIAMETER
            self.update_shot_statistics()

        # check collision with top wall
        if self.ball.rect.y <= self.walls["top"].bottom:
            self.ball.y_speed = -self.ball.y_speed
            self.ball.rect.y = self.walls["top"].bottom
            self.update_shot_statistics()

        # check collision with bottom wall
        if (self.ball.rect.y + BALL_DIAMETER) >= self.walls["bottom"].top:
            self.ball.y_speed = -self.ball.y_speed
            self.ball.rect.y = self.walls["bottom"].top - BALL_DIAMETER
            self.update_shot_statistics()

    def move(self):
        self.timestamp += 1
        if self.timestamp >= self.timestamp_limit:
            for player in self.players:
                player.reset_position()
            self.ball.reset_position()
            self.timestamp = 0
            return None
        # move, check collisions and reverse invalid moves
        for i, player in enumerate(self.players):
            # check player collisions with walls and other players
            player.move()
            if self.statistics is not None:
                self.statistics.update_heat_map(player.name, player.rect.x, player.rect.y)
            if player.rect.collidelist(self.players[:i] + self.players[i+1:]) != -1 \
                    or player.rect.collidelist(list(self.walls.values())) != -1 \
                    or player.rect.x < 0 or player.rect.x + player.rect.width > SCREEN_WIDTH:
                player.undo()
            # check player collisions with ball
            if player.rect.colliderect(self.ball.rect):
                self.n_touches += 1
                self.last_player_ball_collision[i] = True
                # push the player to the fifo queue if it is not already there
                last_player = self.ball_touches_fifo.get_first()
                if last_player is None or last_player.name != player.name:
                    self.ball_touches_fifo.push(player)
                self.passes_fifo.push(player)
                # update ball touch and save statistics
                self.update_ball_touch_statistics(player)
                self.update_passes_statistics(player)
                self.update_save_statistics(player)
                # reverse the ball direction
                self.ball.x_speed = ((self.ball.rect.centerx - self.ball.x_speed) - (self.players[i].rect.centerx - self.players[i].x_speed))
                self.ball.y_speed = ((self.ball.rect.centery - self.ball.y_speed) - (self.players[i].rect.centery - self.players[i].y_speed))
                self.ball.normalize_speed()
                # update direct shot statistics
                self.update_direct_shot_statistics(player)
            else:
                self.last_player_ball_collision[i] = False
        # check ball collisions with goal and walls
        self.ball.move()
        state = self.check_goal()
        if state is None:
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
