import math, random
import numpy as np
import pygame

W, H = 1000, 700

class Ponto:
    def __init__(self, x, y, color=(30, 30, 220)):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.hovered = False
        self.selected = False
        self.is_envolt = False
        self.base_color = color
        self.selected_color = (255, 0, 0)
        self.hover_outline_color = (255, 255, 0)

    def pos(self):
        return np.array([self.x, self.y])
    
    def int_pos(self):
        return (int(self.x), int(self.y))

    def draw(self, surface, color=None, radius=5):
        int_pos = (int(self.x), int(self.y))
        if color is not None:
            draw_color = color  
        else:
            draw_color = self.base_color 

        if self.is_envolt:
            draw_color = (0, 0, 0)
        
        pygame.draw.circle(surface, draw_color, int_pos, radius) 
        if self.hovered:
            pygame.draw.circle(surface, self.hover_outline_color, int_pos, radius+3)
        if self.selected:
            pygame.draw.circle(surface, self.selected_color, int_pos, radius)


    def __add__(self, other):
        return Ponto(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Ponto(self.x - other.x, self.y - other.y)

    def __repr__(self):
        return f"Ponto({self.x}, {self.y})"
