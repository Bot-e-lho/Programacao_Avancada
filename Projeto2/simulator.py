## Miguel Rodrigues Botelho  -- 21202191
## Framework do python, pygame

import pygame
import sys
import random
import numpy as np
from scipy.spatial import Voronoi, Delaunay
from ponto import Ponto

W, H = 1000, 700
tela = pygame.display.set_mode((W, H))
pygame.display.set_caption("Voronoy in red and delaunay in green")
clock = pygame.time.Clock()

pontos = []

def draw_diagrams():
    if len(pontos) < 3:
        return

    coords = np.array([[p.x, p.y] for p in pontos])

    try:
        delaunay = Delaunay(coords)
        for simplex in delaunay.simplices:
            p1_idx, p2_idx, p3_idx = simplex
            p1 = pontos[p1_idx]
            p2 = pontos[p2_idx]
            p3 = pontos[p3_idx]
            
            pygame.draw.line(tela, (0, 150, 0), (p1.x, p1.y), (p2.x, p2.y), 1)
            pygame.draw.line(tela, (0, 150, 0), (p2.x, p2.y), (p3.x, p3.y), 1)
            pygame.draw.line(tela, (0, 150, 0), (p3.x, p3.y), (p1.x, p1.y), 1)
    except Exception as e:
        print(f"Erro no calculo(delaunay): {e}")
        return

    try:
        vor = Voronoi(coords)
        for ridge_pair in vor.ridge_vertices:
            if -1 in ridge_pair:
                continue
            
            p1 = vor.vertices[ridge_pair[0]]
            p2 = vor.vertices[ridge_pair[1]]
            
            pygame.draw.line(tela, (255, 0, 0), p1, p2, 2)
    except Exception as e:
        print(f"Erro no calculo(voronoy): {e}")


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
                print(f"Ponto adicionado em ({new_point.x}, {new_point.y}). Total: {len(pontos)}")
            elif event.button == 3:
                if pontos:
                    pontos.pop()
                    print(f"Ponto removido. Total: {len(pontos)}")

    tela.fill((173, 216, 230)) 

    draw_diagrams()

    for p in pontos:
        p.draw(tela)

    pygame.display.flip()
    
    clock.tick(60)

pygame.quit()
sys.exit()
