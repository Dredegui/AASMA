import pygame
from .constants import *

class Ball:
    def __init__(self, x, y, radious):
        self.rect = pygame.Rect(x, y, radious, radious)
        self.radious = radious
        self.inicial_x = x
        self.inicial_y = y
        self.x_speed = 0
        self.y_speed = 0

    def move(self):
        self.rect.move_ip(self.x_speed, self.y_speed)

    def normalize_speed(self):
        norm = abs(self.x_speed) + abs(self.y_speed)
        if norm != 0:
            self.x_speed = (self.x_speed / norm) * BALL_SPEED
            self.y_speed = (self.y_speed / norm) * BALL_SPEED

    def undo(self):
        self.rect.move_ip(-self.x_speed, -self.y_speed)
    
    def reset_position(self):
        self.rect.x = self.inicial_x
        self.rect.y = self.inicial_y
        self.x_speed = 0
        self.y_speed = 0

    def render(self, screen):
        pygame.draw.circle(screen, COLORS["white"], (self.rect.x, self.rect.y), self.radious)