## Miguel Rodrigues Botelho  -- 21202191
## Framework do python, pygame

import pygame
import sys
import random
from ponto import Ponto
from linha import Linha
from log import Log
import math

pygame.init()
W, H = 1000, 700
tela = pygame.display.set_mode((W, H))
pygame.display.set_caption("gear up!")
clock = pygame.time.Clock()
logger = Log()

pontos = []
for _ in range(7): 
    x = random.randint(50, W - 50)
    y = random.randint(50, H - 50)
    dx = (random.random() - 0.5) * 4
    dy = (random.random() - 0.5) * 4
    pontos.append(Ponto(x, y, dx, dy))

linhas = []
for _ in range(5): 
    x1 = random.randint(50, W - 50)
    y1 = random.randint(50, H - 50)
    p1 = Ponto(x1, y1, 0, 0, color=(0, 0, 0))
    comprimento = random.randint(200, 500)
    angulo = random.uniform(0, 2 * math.pi)
    x2 = x1 + comprimento * math.cos(angulo)
    y2 = y1 + comprimento * math.sin(angulo)
    p2 = Ponto(x2, y2, 0, 0, color=(0, 0, 0))
    dx = (random.random() - 0.5) * 4
    dy = (random.random() - 0.5) * 4
    
    linhas.append(Linha(p1, p2, dx, dy, width=3))


running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for p in pontos:
        p.hovered = False
    for l in linhas:
        l.hovered = False

    for p in pontos:
        dist_ponto = ((mouse_pos[0] - p.x)**2 + (mouse_pos[1] - p.y)**2)**0.5
        if dist_ponto < 10:
            p.hovered = True

    for l in linhas:
        if l.distance_to_point(mouse_pos[0], mouse_pos[1]) < l.width + 5:
            l.hovered = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            cliques = []
            
            for i, p in enumerate(pontos):
                dist_ponto = ((pos[0] - p.x)**2 + (pos[1] - p.y)**2)**0.5
                if dist_ponto < 10:
                    p.selected = not p.selected
                    cliques.append(f"Ponto {i}")
            
            for i, l in enumerate(linhas):
                if l.distance_to_point(pos[0], pos[1]) < l.width + 5:
                    l.selected = not l.selected
                    cliques.append(f"Linha {i}")
            
            logger.log_click(pos, cliques)
            print(f"clique em {pos}. objetos clicados: {cliques}")


        elif event.type == pygame.MOUSEMOTION:
            logger.log_mouse_movement(pygame.mouse.get_pos())

    for p in pontos:
        p.move()
    for l in linhas:
        l.move()
        
    tela.fill((173, 216, 230))
    
    for p in pontos:
        p.draw(tela)
    
    for l in linhas:
        l.draw(tela)
    
    pygame.display.flip()
    clock.tick(60)

logger.export_data()
pygame.quit()
sys.exit()
