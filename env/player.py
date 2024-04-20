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

    def reset_position(self):
        self.rect.x = self.initial_x
        self.rect.y = self.initial_y
        self.x_speed = 0
        self.y_speed = 0

    def render(self, screen):
        pygame.draw.rect(screen, self.color, (self.rect.left, self.rect.top, self.rect.width, self.rect.height))