## Miguel Rodrigues Botelho -- 21202191
## Framework do python, pygame

import pygame
import sys
import random
import numpy as np
import math
from ponto import Ponto

W, H = 1000, 700
tela = pygame.display.set_mode((W, H))
pygame.display.set_caption("Gift Wrapping / Jarvis March")
clock = pygame.time.Clock()

pontos = []
hull_points = []
status_message = ""


def jarvis_march(points_list):
    if len(points_list) < 3:
        return points_list
    
    start_point = min(points_list, key=lambda p: (p.x, p.y))
    
    hull = []
    current_point = start_point
    
    while True:
        hull.append(current_point)
        endpoint = points_list[0]
        
        for next_point in points_list:
            if endpoint == current_point or cross_product_check(current_point, endpoint, next_point) > 0:
                endpoint = next_point
        
        current_point = endpoint
        if current_point == hull[0]:
            break
            
    return hull

def cross_product_check(p1, p2, p3):
    return (p2.x - p1.x) * (p3.y - p1.y) - (p2.y - p1.y) * (p3.x - p1.x)


def draw_hull(hull_points):
    if len(hull_points) > 1:
        pygame.draw.lines(tela, (255, 0, 0), True, [(p.x, p.y) for p in hull_points], 3)


def gen_shape_points(shape_type, n):
    new_points = []
    if shape_type == "rectangle":
        min_x, max_x = W/2 - 200, W/2 + 200
        min_y, max_y = H/2 - 150, H/2 + 150
        for _ in range(n):
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)
            new_points.append(Ponto(x, y))
    elif shape_type == "circle":
        center_x, center_y = W/2, H/2
        radius = 200
        for _ in range(n):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, radius)
            x = center_x + dist * math.cos(angle)
            y = center_y + dist * math.sin(angle)
            new_points.append(Ponto(x, y))

    elif shape_type == "triangle":
        v1 = (W/2, H/2 - 250)    
        v2 = (W/2 - 300, H/2 + 200) 
        v3 = (W/2 + 300, H/2 + 200) 
        
        for _ in range(n):
            s = random.random()
            t = random.random()
            if s + t > 1.0:
                s = 1.0 - s
                t = 1.0 - t
            u = 1.0 - s - t
            x = u * v1[0] + s * v2[0] + t * v3[0]
            y = u * v1[1] + s * v2[1] + t * v3[1]
            new_points.append(Ponto(x, y))
        
    return new_points



def draw_text(surface, text, x, y, color=(0, 0, 0), font_size=16):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))

pygame.font.init()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pos = pygame.mouse.get_pos()
                new_point = Ponto(pos[0], pos[1])
                pontos.append(new_point)
            elif event.button == 3:
                if pontos:
                    pontos.pop()
        elif event.type == pygame.KEYDOWN:
            n_points = 500 # Aqui podemos alterar a quantidade de pointos
            if event.key == pygame.K_1:
                pontos = gen_shape_points("rectangle", n_points)
            elif event.key == pygame.K_2:
                pontos = gen_shape_points("circle", n_points)
            elif event.key == pygame.K_3:
                pontos = gen_shape_points("triangle", n_points)
            elif event.key == pygame.K_c:
                pontos = []
    if pontos:
        for p in pontos:
            p.is_envolt = False
            
        hull_points = jarvis_march(pontos)
        
        for p_hull in hull_points:
            p_hull.is_envolt = True
    else:
        hull_points = []

    tela.fill((173, 216, 230))

    draw_hull(hull_points)

    for p in pontos:
        p.draw(tela)

    draw_text(tela, "[1] Retângulo [2] Círculo [3] Triângulo [C] Limpar", 10, H-40)
    draw_text(tela, status_message, 10, 10)
    draw_text(tela, f"Total de pontos: {len(pontos)}", 10, 30)
    draw_text(tela, f"Main pontos: {len(hull_points)}", 10, 50)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()