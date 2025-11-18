## Miguel Rodrigues Botelho -- 21202191
## Trabalho 6: Fabricas

import pygame
import sys
import math
import numpy as np
import random
import heapq 
from ponto import Ponto
from factories import *

class NavigationApp:
    
    def __init__(self):
        self.W, self.H = 1000, 700
        self.tela = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("Fabricas")
        self.clock = pygame.time.Clock()
        pygame.font.init()
        
        self.blockSize, self.COLS, self.ROWS = self.get_user_config()
        
        self.GRID_WIDTH = self.COLS * self.blockSize
        self.GRID_HEIGHT = self.ROWS * self.blockSize
        self.off_x = (self.W - self.GRID_WIDTH) // 2
        self.off_y = (self.H - self.GRID_HEIGHT) // 2

        self.colors = {
            "start": (0, 215, 0),
            "goal": (215, 0, 0),
            "obstacle": (52, 52, 52),
            "free": (255, 255, 255),
            "text": (8, 8, 8),
            "path": [(255, 0, 255), (0, 255, 255), (255, 255, 0), (100, 100, 255), (255, 150, 50)]
        }
        self.grid_factory = GridFactory()
        self.obstacle_factory = ObstacleFactory()
        self.grid = self.grid_factory.create_grid(self.ROWS, self.COLS, self.colors["free"])
        path_factories = {
            "A*_HV": VH_A_Star_Factory(),
            "A*_DIAG": Diag_A_Star_Factory(),
            "DIJKSTRA_HV": Factory_Dijkstra(),
            "DIJKSTRA_DIAG": Factory_Dijkstra_Diag() 
        }
        self.algo_keys = list(path_factories.keys()) 
        self.current_algo_index = 0

        self.task_factory = TaskFactory(path_factories, self.colors["path"])
        self.current_mode = 1 
        self.current_path_pair = [None, None]
        self.task_list = [] 
        self.completed_tasks = [] 
        self.obstacle_keys = ["wall", "movable"]
        self.current_obstacle_index = 0
        self.update_status_message()
        
    def get_user_config(self):
        try:
            res_input = input("Digite a resolucao (tamanho de cada celula em px): ")
            blockSize = int(res_input)
            cols_input = input(f"Digite o numero de colunas: ")
            COLS = int(cols_input)
            rows_input = input(f"Digite o numero de linhas: ")
            ROWS = int(rows_input)
        except ValueError:
            blockSize, COLS, ROWS = 25, 20, 15
        print(f"Grid criado: {ROWS}x{COLS}, resolucao: {blockSize}px")
        return blockSize, COLS, ROWS

    def pos_to_grid(self, x, y):
        x_relative = x - self.off_x
        y_relative = y - self.off_y
        if 0 <= x_relative < self.GRID_WIDTH and 0 <= y_relative < self.GRID_HEIGHT:
            c = int(x_relative // self.blockSize)
            r = int(y_relative // self.blockSize)
            return (r, c)
        return None

    def update_status_message(self):
        if self.current_mode == 1:
            self.status_message = "Modo: Obstaculos (1)"
        elif self.current_mode == 2:
            algo_name = self.algo_keys[self.current_algo_index]
            self.status_message = f"Modo: Start/Goal (2) | Algoritmo: {algo_name}"

    def grid_to_pos(self, r, c):
        center_x = self.off_x + c * self.blockSize + self.blockSize / 2
        center_y = self.off_y + r * self.blockSize + self.blockSize / 2
        return Ponto(center_x, center_y)
    
    def generate_random_obstacles(self, percentage=0.2):
        self.status_message = f"Adicionando {percentage*100}% de obstaculos"
        self.completed_tasks = [] 
        
        key = self.obstacle_keys[self.current_obstacle_index]
        self.grid.fill_random_obstacles(self.obstacle_factory, key, percentage)
        
        self.status_message = f"Obstaculos aleatorios adicionados"

    def handle_click(self, pos):
        cell = self.pos_to_grid(pos[0], pos[1])
        if cell is None: return

        if self.current_mode == 1:
            key = self.obstacle_keys[self.current_obstacle_index]
            self.grid.toggle_obstacle(cell[0], cell[1], self.obstacle_factory, key)
            self.completed_tasks = [] 
            self.update_status_message()
        
        elif self.current_mode == 2:
            if self.grid.data[cell] is not None:
                self.status_message = "Celula ocupada"
                return

            if self.current_path_pair[0] is None:
                self.current_path_pair[0] = cell
                self.status_message = f"Start: {cell}"
            elif self.current_path_pair[1] is None:
                if cell == self.current_path_pair[0]:
                    self.status_message = "Start e goal devem ser diferentes"
                    return
                
                self.current_path_pair[1] = cell
                start, goal = self.current_path_pair
                
                algo_key = self.algo_keys[self.current_algo_index]
                new_task = self.task_factory.create_task(start, goal, algo_key)
                self.task_list.append(new_task)
                
                self.status_message = f"Tarefa ({algo_key}) adicionada. Total: {len(self.task_list)}."
                self.current_path_pair = [None, None]

    def generate_random_pairs(self, count):
        self.task_list = []
        free_cells = [(r, c) for r in range(self.ROWS) for c in range(self.COLS) if self.grid.data[r, c] is None]
        
        if len(free_cells) < 2:
            self.status_message = "Poucas celulas livres"
            return

        for _ in range(count):
            start = random.choice(free_cells)
            goal = random.choice(free_cells)
            while start == goal:
                goal = random.choice(free_cells)
            
            algo_key = random.choice(self.algo_keys)
            new_task = self.task_factory.create_task(start, goal, algo_key)
            self.task_list.append(new_task)
        self.status_message = f"{count} pares gerados aleatoriamente"

    def run_all_paths(self):
        self.completed_tasks = []
        if not self.task_list:
            self.status_message = "Nenhuma tarefa na fila"
            return

        num_success = 0
        grid_data = self.grid.get_data()
        total_tasks = len(self.task_list)
        
        for task in self.task_list:
            path = task.pathfinder.find_path(grid_data, task.start, task.goal)
            if path:
                task.path = path
                self.completed_tasks.append(task)
                num_success += 1

        self.status_message = f"{len(self.task_list)} caminhos encontrados"
        self.task_list = []


    def draw_text(self, text_str, x, y, font_size=14):
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text_str, True, self.colors["text"])
        self.tela.blit(text_surface, (x, y))

    def draw_paths(self): 
        for task in self.task_list:            
            if task.start and self.grid.data[task.start] is None:
                start_pos = self.grid_to_pos(task.start[0], task.start[1])
                pygame.draw.circle(self.tela, self.colors["start"], start_pos.int_pos(), self.blockSize // 4) 
            
            if task.goal and self.grid.data[task.goal] is None:
                goal_pos = self.grid_to_pos(task.goal[0], task.goal[1])
                pygame.draw.rect(self.tela, self.colors["goal"], pygame.Rect(goal_pos.x - self.blockSize/4, goal_pos.y - self.blockSize/4, self.blockSize/2, self.blockSize/2))

        for task in self.completed_tasks:
            path_color = task.color
            
            if task.path:
                points_on_path = [self.grid_to_pos(r, c).int_pos() for r, c in task.path]
                
                if len(points_on_path) > 1:
                    
                    algo_key = getattr(task, "algorithm_key", "")
                    is_hv_only = "HV" in algo_key
                    
                    if is_hv_only:
                        for i in range(len(points_on_path) - 1):
                            p1 = points_on_path[i]
                            p2 = points_on_path[i+1]
                            
                            p_mid = (p1[0], p2[1]) 
                            
                            pygame.draw.lines(self.tela, path_color, False, [p1, p_mid, p2], 3)
                    else:
                        pygame.draw.lines(self.tela, path_color, False, points_on_path, 3)
            
            start_pos = self.grid_to_pos(task.start[0], task.start[1])
            pygame.draw.circle(self.tela, path_color, start_pos.int_pos(), self.blockSize // 3)
            goal_pos = self.grid_to_pos(task.goal[0], task.goal[1])
            goal_rect = pygame.Rect(goal_pos.x - self.blockSize / 3, goal_pos.y - self.blockSize / 3, self.blockSize * 2 / 3, self.blockSize * 2 / 3)
            pygame.draw.rect(self.tela, path_color, goal_rect)

    def draw_all(self):
        self.tela.fill((173, 216, 230))
        
        self.grid.draw(self.tela, self.off_x, self.off_y, self.blockSize)
        
        self.draw_paths()

        self.draw_text(self.status_message, 10, 10)
        self.draw_text("[1] Obstaculos | [2] Start/Goal", 10, self.H - 90)
        self.draw_text("[G] Gerar pares | [R] Rodar | [O] Obstac. aleatorios", 10, self.H - 70)
        self.draw_text("[C] Limpar | [T] Trocar algoritmo | [M] Trocar bbstaculo", 10, self.H - 50)
        
        algo_name = self.algo_keys[self.current_algo_index]
        self.draw_text(f"Algoritmo atual: {algo_name}", 10, self.H - 30)

    def run(self):
        running = True
        while running:
            self.grid.update_movables()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_click(pygame.mouse.get_pos())

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1: 
                        self.current_mode = 1
                    elif event.key == pygame.K_2: 
                        self.current_mode = 2
                    
                    elif event.key == pygame.K_g:
                        self.generate_random_pairs(5) 
                    
                    elif event.key == pygame.K_r:
                        self.run_all_paths()
                    
                    elif event.key == pygame.K_t:
                        self.current_algo_index = (self.current_algo_index + 1) % len(self.algo_keys)

                    elif event.key == pygame.K_o:
                        self.generate_random_obstacles(0.2)
                    
                    elif event.key == pygame.K_m: 
                        self.current_obstacle_index = (self.current_obstacle_index + 1) % len(self.obstacle_keys)

                    elif event.key == pygame.K_c:
                        self.grid.clear()
                        self.completed_tasks = []
                        self.task_list = []
                        self.current_path_pair = [None, None]
                        
                    self.update_status_message() 

            self.draw_all()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = NavigationApp()
    app.run()
