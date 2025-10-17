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

    def draw(self, surface):
        int_pos = (int(self.x), int(self.y))
        draw_color = (0, 0, 0) if self.is_envolt else self.base_color
        pygame.draw.circle(surface, draw_color, int_pos, 5)
        if self.hovered:
            pygame.draw.circle(surface, self.hover_outline_color, int_pos, 8)
        if self.selected:
            pygame.draw.circle(surface, self.selected_color, int_pos, 5)