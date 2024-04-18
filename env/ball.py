import pygame
from .constants import *

class Ball:
    def __init__(self, x, y, radious):
        self.rect = pygame.Rect(x, y, BALL_WIDTH, BALL_HEIGHT)
        self.x = x
        self.y = y
        self.radious = radious
        self.x_speed = 0
        self.y_speed = 0

    def move(self):
        self.rect.move(self.x_speed, self.y_speed)

    def render(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.radious)