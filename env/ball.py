import pygame

class Ball:
    def __init__(self, x, y, radious):
        self.x = x
        self.y = y
        self.radious = radious
        self.x_speed = 0
        self.y_speed = 0

    def move(self):
        self.x += self.x_speed
        self.y += self.y_speed

    def render(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.radious)