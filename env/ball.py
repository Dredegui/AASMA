import pygame
from .constants import *

class Ball:
    def __init__(self, x, y, radious):
        self.rect = pygame.Rect(x, y, radious*2, radious*2)
        self.radious = radious
        self.initial_x = x
        self.initial_y = y
        self.x_speed = 0
        self.y_speed = 0

    def move(self):
        total = abs(self.x_speed) + abs(self.y_speed)
        if total > 4:
            self.x_speed = (self.x_speed / total) * (total - 1/10 * 1/2) 
            self.y_speed = (self.y_speed / total) * (total - 1/10 * 1/2)
        else:
            self.x_speed = 0
            self.y_speed = 0
        self.rect.move_ip(self.x_speed, self.y_speed)

    def normalize_speed(self):
        norm = abs(self.x_speed) + abs(self.y_speed)
        if norm != 0:
            self.x_speed = (self.x_speed / norm) * BALL_SPEED
            self.y_speed = (self.y_speed / norm) * BALL_SPEED
    
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
        pygame.draw.circle(screen, COLORS["white"], (self.rect.centerx, self.rect.centery), self.radious)