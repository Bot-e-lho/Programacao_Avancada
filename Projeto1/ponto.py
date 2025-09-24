import math, random
import numpy as np
import pygame

W, H = 1000, 700

class Ponto:
    def __init__(self, x, y, dx, dy, color = (30,30,220)):
        self.x = float(x); 
        self.y = float(y)
        self.color = color
        self.dx = float(dx)
        self.dy = float(dy)
        self.hovered = False
        self.selected = False
        self.base_color = color
        self.selected_color = (255, 0, 0) 
        self.hover_outline_color = (255, 255, 0) 

    def pos(self):
        return np.array([self.x, self.y])

    def move(self):
        self.x += self.dx; 
        self.y += self.dy
        if self.x < 0:
            self.x = 0
            self.dx *= -1
        elif self.x > W:
            self.x = W
            self.dx *= -1

        if self.y < 0:
            self.y = 0
            self.dy *= -1
        elif self.y > H:
            self.y = H
            self.dy *= -1

    def draw(self, surface):
        int_pos = (int(self.x), int(self.y))
        pygame.draw.circle(surface, self.base_color, int_pos, 5)
        if self.hovered:
            pygame.draw.circle(surface, self.hover_outline_color, int_pos, 8)
        if self.selected:
            pygame.draw.circle(surface, self.selected_color, int_pos, 5)


    def distance_to_point(self, px, py):
        return math.hypot(self.x - px, self.y - py)
