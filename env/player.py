import pygame

class Player:
    def __init__(self, name, x, y, team, color=(255, 255, 255)):
        self.name = name
        self.x = x
        self.y = y
        self.y_speed = 0
        self.x_speed = 0
        self.team = team
        self.color = color

    def move(self):
        self.y += self.speed
        self.x += self.x_speed

    def render(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, 10, 50))