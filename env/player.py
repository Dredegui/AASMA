import pygame
from .constants import *

class Player:
    def __init__(self, name, x, y, team, color=COLORS["white"]):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.name = name
        self.initial_x = x
        self.initial_y = y
        self.y_speed = 0
        self.x_speed = 0
        self.team = team
        self.color = color

    def move(self):
        self.rect.move_ip(self.x_speed, self.y_speed)

    def move_up(self):
        self.y_speed = -PLAYER_SPEED
        self.x_speed = 0
    
    def move_down(self):
        self.y_speed = PLAYER_SPEED
        self.x_speed = 0

    def move_left(self):
        self.x_speed = -PLAYER_SPEED
        self.y_speed = 0

    def move_right(self):
        self.x_speed = PLAYER_SPEED
        self.y_speed = 0

    def stop(self):
        self.y_speed = 0
        self.x_speed = 0
    
    def undo(self):
        self.rect.move_ip(-self.x_speed, -self.y_speed)

    def reset_position(self, start_padding=50):
        def randomize_positions(x, y, start_padding=50):
            import numpy as np
            x_out = np.random.randint(x - 2*start_padding, x + 2*start_padding)
            y_out = np.random.randint(y - start_padding, y + start_padding)
            return x_out, y_out
         
        self.rect.x, self.rect.y = randomize_positions(self.initial_x, self.initial_y, start_padding=start_padding)
        self.x_speed = 0
        self.y_speed = 0

    def render(self, screen):
        pygame.draw.rect(screen, self.color, (self.rect.left, self.rect.top, self.rect.width, self.rect.height))