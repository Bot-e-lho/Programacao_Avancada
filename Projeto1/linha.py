import pygame, sys, time, random, math
import numpy as np
from ponto import Ponto

W, H = 1000, 700


class Linha:
    def __init__(self, a: Ponto, b: Ponto, dx, dy, color=(10,10,10), width=2):
        self.a = a
        self.b = b
        self.dx = dx
        self.dy = dy
        self.width = width
        self.hovered = False
        self.selected = False
        self.base_color = color
        self.selected_color = (255, 0, 0) 
        self.hover_outline_color = (255, 255, 10) 

    def draw(self, surface):
        draw_color = self.base_color
        pygame.draw.line(surface, draw_color, (int(self.a.x), int(self.a.y)), (int(self.b.x), int(self.b.y)), self.width)
        if self.selected:
            draw_color = self.selected_color
            pygame.draw.line(surface, draw_color, (int(self.a.x), int(self.a.y)), (int(self.b.x), int(self.b.y)), self.width + 2)
        elif self.hovered:
            draw_color = self.hover_outline_color
            pygame.draw.line(surface, draw_color, (int(self.a.x), int(self.a.y)), (int(self.b.x), int(self.b.y)), self.width + 2)
        

    def distance_to_point(self, point_x, point_y):
        p1 = np.array([self.a.x, self.a.y])
        p2 = np.array([self.b.x, self.b.y])
        p3 = np.array([point_x, point_y])
        
        line_vec = p2 - p1
        point_vec = p3 - p1
        
        line_len_sq = np.dot(line_vec, line_vec)
        if line_len_sq == 0:
            return np.linalg.norm(p3 - p1)
            
        t = np.dot(point_vec, line_vec) / line_len_sq
        t = max(0, min(1, t))
        
        projection = p1 + t * line_vec
        return np.linalg.norm(p3 - projection)
    
    def move(self):
        self.a.x += self.dx
        self.a.y += self.dy
        self.b.x += self.dx
        self.b.y += self.dy

        colisao_x = False
        colisao_y = False

        if self.a.x < 0 or self.a.x > W or self.b.x < 0 or self.b.x > W:
            colisao_x = True
        if self.a.y < 0 or self.a.y > H or self.b.y < 0 or self.b.y > H:
            colisao_y = True
            
        if colisao_x:
            self.dx *= -1
        if colisao_y:
            self.dy *= -1
            
        self.a.x = max(0, min(W, self.a.x))
        self.b.x = max(0, min(W, self.b.x))
        self.a.y = max(0, min(H, self.a.y))
        self.b.y = max(0, min(H, self.b.y))
