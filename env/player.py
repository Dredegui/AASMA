import pygame
from .constants import *

class Player:
    def __init__(self, name, x, y, team, color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.name = name
        self.y_speed = 0
        self.x_speed = 0
        self.team = team
        self.color = color

    def move(self):
        self.rect.move(self.x_speed, self.y_speed)
    
    def undo(self):
        self.rect.move(-self.x_speed, -self.y_speed)

    def render(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))