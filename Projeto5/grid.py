## Miguel Rodrigues Botelho -- 21202191
## Trabalho 5:  Navegação

import pygame
import sys
import math
import numpy as np
import random
import heapq 
from ponto import Ponto

try:
    res_input = input("Digite a Resolução (tamanho de cada célula em px): ")
    blockSize = int(res_input) if res_input else 25

    cols_input = input(f"Digite o número de Colunas: ")
    COLS = int(cols_input) if cols_input else 20

    rows_input = input(f"Digite o número de Linhas: ")
    ROWS = int(rows_input) if rows_input else 15

except ValueError:
    print("Usando valores padrao")
    blockSize = 25
    COLS = 20
    ROWS = 15

print(f"Grid criado: {ROWS}x{COLS}, Resolução: {blockSize}px")

W, H = 1000, 700
tela = pygame.display.set_mode((W, H))
pygame.display.set_caption("Navegação")
clock = pygame.time.Clock()
tela.fill((173, 216, 230))
pygame.font.init()

GRID_WIDTH = COLS * blockSize
GRID_HEIGHT = ROWS * blockSize
off_x = (W - GRID_WIDTH) // 2
off_y = (H - GRID_HEIGHT) // 2
start = (0, 215, 0)
goal = (215, 0, 0)
colors = [(255, 0, 255), (0, 255, 255), (255, 255, 0), (100, 100, 255), (255, 150, 50)]
text = (8, 8, 8) 
obstacle = (52, 52, 52) 


current_mode = 1 
current_path_pair = [None, None]
path_pairs_list = [] 
computed_paths = [] 
status_message = "Modo: Adicionando obstaculos (1)"
grid = np.zeros((ROWS, COLS), dtype=int)


def draw_grid():
    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(off_x + c * blockSize, off_y + r * blockSize, blockSize, blockSize)
            
            color = obstacle if grid[r, c] == 1 else (255,255,255)
            pygame.draw.rect(tela, color, rect)
            pygame.draw.rect(tela, (12,8,20), rect, 1)

def pos_to_grid(x, y):
    x_relative = x - off_x
    y_relative = y - off_y
    
    if 0 <= x_relative < GRID_WIDTH and 0 <= y_relative < GRID_HEIGHT:
        c = int(x_relative // blockSize)
        r = int(y_relative // blockSize)
        return (r, c)
    return None

def grid_to_pos(r, c):
    center_x = off_x + c * blockSize + blockSize / 2
    center_y = off_y + r * blockSize + blockSize / 2
    return Ponto(center_x, center_y)


def draw_text(surface, text_str, x, y, color=text, font_size=14):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text_str, True, color)
    surface.blit(text_surface, (x, y))


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star(start, goal):
    
    if grid[start] == 1 or grid[goal] == 1:
        return []

    g_score = { (r, c): float('inf') for r in range(ROWS) for c in range(COLS) }
    g_score[start] = 0
    
    f_score = { (r, c): float('inf') for r in range(ROWS) for c in range(COLS) }
    f_score[start] = heuristic(start, goal)
    
    open_set = [(f_score[start], start)]
    came_from = {} 

    while open_set:
        current_f, current_node = heapq.heappop(open_set)
        
        if current_node == goal:
            path = []
            while current_node in came_from:
                path.append(current_node)
                current_node = came_from[current_node]
            path.append(start)
            return path[::-1] 
        
        r, c = current_node
        
        neighbors = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)] 
        
        for neighbor in neighbors:
            nr, nc = neighbor
            
            if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr, nc] == 0:
                tentative_g_score = g_score[current_node] + 1
                
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current_node
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                        
    return []


def handle_grid_planning(pos):
    global current_path_pair, status_message, path_pairs_list
    
    if current_path_pair is None:
        current_path_pair = [None, None]
    
    cell = pos_to_grid(pos[0], pos[1])
    if cell is None:
        return
        
    if grid[cell] == 1:
        status_message = ""
        return

    if current_path_pair[0] is None:
        current_path_pair[0] = cell
        status_message = f""
        
    elif current_path_pair[1] is None:
        if cell == current_path_pair[0]:
            status_message = ""
            return
            
        current_path_pair[1] = cell
        
        path_pairs_list.append(tuple(current_path_pair))
        status_message = f"Par ({current_path_pair[0]} -> {current_path_pair[1]}) adicionado. Total: {len(path_pairs_list)}"
        
        current_path_pair = [None, None]


def generate_random_pairs(count):
    global path_pairs_list, status_message
    path_pairs_list = []
    
    free_cells = [(r, c) for r in range(ROWS) for c in range(COLS) if grid[r, c] == 0]
    
    if len(free_cells) < 2:
        status_message = "Poucas células"
        return

    for _ in range(count):
        start = random.choice(free_cells)
        goal = random.choice(free_cells)
        while start == goal:
            goal = random.choice(free_cells)
            
        path_pairs_list.append((start, goal))
        
    status_message = f"{count} pares gerados aleatoriamente"

def run_all_paths():
    global computed_paths, path_pairs_list, status_message
    computed_paths = []

    num_success = 0
    for start, goal in path_pairs_list:
        path = a_star(start, goal)
        if path:
            computed_paths.append((path, start, goal))
            num_success += 1

    status_message = f"Execução concluida {num_success}/{len(path_pairs_list)} caminhos encontrados"
    path_pairs_list = []

def draw_paths(): 
    for idx, (start_node, goal_node) in enumerate(path_pairs_list):
        if start_node and grid[start_node] == 0:
            start_pos = grid_to_pos(start_node[0], start_node[1])
            pygame.draw.circle(tela, start, start_pos.int_pos(), blockSize // 4) 
        if goal_node and grid[goal_node] == 0:
            goal_pos = grid_to_pos(goal_node[0], goal_node[1])
            pygame.draw.rect(tela, goal, pygame.Rect(goal_pos.x - blockSize/4, goal_pos.y - blockSize/4, blockSize/2, blockSize/2))

    for idx, (path, start_node, goal_node) in enumerate(computed_paths):
        path_color = colors[idx % len(colors)]
        if path:
            point_tuples = []
            for r, c in path:
                pos = grid_to_pos(r, c)
                point_tuples.append(pos.int_pos())
            
            if len(point_tuples) > 1:
                pygame.draw.lines(tela, path_color, False, point_tuples, 3)
        
        start_pos = grid_to_pos(start_node[0], start_node[1])
        pygame.draw.circle(tela, path_color, start_pos.int_pos(), blockSize // 3)
        
        goal_pos = grid_to_pos(goal_node[0], goal_node[1])
        goal_rect = pygame.Rect(goal_pos.x - blockSize / 3, goal_pos.y - blockSize / 3, blockSize * 2 / 3, blockSize * 2 / 3)
        pygame.draw.rect(tela, path_color, goal_rect)


def draw_all():
    tela.fill((173, 216, 230))
    draw_grid()
    draw_paths()

    draw_text(tela, status_message, 10, 10)
    draw_text(tela, "[1] Obstaculos | [2] Start/Goal", 10, H - 90)
    draw_text(tela, "[G] Gera Pares Aleatorios | [R] Roda A* | [C] Limpa Tudo", 10, H - 50)
    draw_text(tela, f"Caminhos Encontrados: {len(computed_paths)}", 10, H - 30)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pos = pygame.mouse.get_pos()
                
                if current_mode == 1:
                    cell = pos_to_grid(pos[0], pos[1])
                    if cell is not None:
                        r, c = cell
                        grid[r, c] = 1 - grid[r, c] 
                        computed_paths = [] 
                        status_message = f"Célula {cell} alterada. Caminhos antigos invalidados."
                elif current_mode == 2:
                    handle_grid_planning(pos)

        elif event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_1: current_mode = 1; status_message = "Modo: Ocupação (1)"
            elif event.key == pygame.K_2: current_mode = 2; status_message = "Modo: Start/Goal (2)"

            elif event.key == pygame.K_g:
                generate_random_pairs(5) 
            
            elif event.key == pygame.K_r:
                run_all_paths()
                
            elif event.key == pygame.K_c:
                grid.fill(0); computed_paths = []; path_pairs_list = []; current_path_pair = [None, None]
                status_message = "Tudo limpo."

    draw_all()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
        
