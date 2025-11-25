## Miguel Rodrigues Botelho -- 21202191
## Trabalho 7: SAD

import pygame
import sys
import math
import numpy as np
import random
import heapq 
from ponto import Ponto
from factories import *
from pathfiding import *

class NavigationApp:
    
    def __init__(self):
        self.W, self.H = 1000, 700
        self.tela = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("SAD")
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
            "free": (255, 255, 255),
            "text": (8, 8, 8),
            "path": [(255, 0, 255), (0, 255, 255), (255, 255, 0), (100, 100, 255), (255, 150, 50)]
        }
        self.grid_factory = GridFactory()
        self.obstacle_factory = ObstacleFactory()

        self.path_factories = {
            "A*_HV": VH_A_Star_Factory(),
            "A*_DIAG": Diag_A_Star_Factory(),
            "DIJKSTRA_HV": Factory_Dijkstra(),
            "DIJKSTRA_DIAG": Factory_Dijkstra_Diag(),
            "A*_HEX": Factory_Hex_A_Star()
        }

        self.task_factory = TaskFactory(self.path_factories, self.colors["path"])

        self.grid_type = "rect"
        self.reset_grid()

        self.current_mode = 1 
        self.current_path_pair = [None, None]
        self.task_list = [] 
        self.completed_tasks = [] 
        self.obstacle_keys = ["wall", "movable"]
        self.current_obstacle_index = 0
        self.algo_keys = list(self.path_factories.keys()) 
        self.current_algo_index = 0
        self.update_status_message()
        
    def get_user_config(self):
        #try:
        #    res_input = input("Digite a resolucao (tamanho de cada celula em px): ")
        #    blockSize = int(res_input)
        #    cols_input = input(f"Digite o numero de colunas: ")
        #    COLS = int(cols_input)
        #    rows_input = input(f"Digite o numero de linhas: ")
        #    ROWS = int(rows_input)
        #except ValueError:
        #    blockSize, COLS, ROWS = 25, 20, 15
        #print(f"Grid criado: {ROWS}x{COLS}, resolucao: {blockSize}px")
        #return blockSize, COLS, ROWS
        return 35, 20, 15
    
    def reset_grid(self):
        self.grid = self.grid_factory.create_grid(
            self.grid_type, self.ROWS, self.COLS, self.colors["free"]
        )
        self.completed_tasks = []
        self.task_list = []
        self.current_path_pair = [None, None]

    def pos_to_grid(self, x, y):
        return self.grid.get_grid_coords(x, y, self.off_x, self.off_y, self.blockSize)

    def update_status_message(self):
        obst = self.obstacle_keys[self.current_obstacle_index]
        algo = self.algo_keys[self.current_algo_index]
        self.status_message = f"Grid: {self.grid_type.upper()} | Obst: {obst} | Algoritmo: {algo}"

    def grid_to_pos(self, r, c):
        pixel_pos = self.grid.get_pos(r, c, self.off_x, self.off_y, self.blockSize)
        return Ponto(pixel_pos[0], pixel_pos[1])
    
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
        
        elif self.current_mode == 2: 
            if self.grid.data[cell] is not None: return

            if self.current_path_pair[0] is None:
                self.current_path_pair[0] = cell
            elif self.current_path_pair[1] is None:
                if cell == self.current_path_pair[0]: return
                self.current_path_pair[1] = cell
                
                algo = self.algo_keys[self.current_algo_index]
                new_task = self.task_factory.create_task(
                    self.current_path_pair[0], self.current_path_pair[1], algo
                )
                self.task_list.append(new_task)
                self.current_path_pair = [None, None]
        self.update_status_message()

    def generate_random_pairs(self, count):
        self.task_list = []
        free = [(r,c) for r in range(self.ROWS) for c in range(self.COLS) if self.grid.data[r,c] is None]
        if len(free) < 2: return
        for _ in range(count):
            s = random.choice(free)
            g = random.choice(free)
            algo = random.choice(self.algo_keys)
            self.task_list.append(self.task_factory.create_task(s, g, algo))

    def run_all_paths(self):
        self.completed_tasks = []
        num_success = 0
        for task in self.task_list:
            path = task.pathfinder.find_path(self.grid, task.start, task.goal)
            if path:
                task.path = path
                self.completed_tasks.append(task)
                num_success += 1
        self.task_list = []
        self.status_message = f"Caminhos: {num_success}"


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
                points = [self.grid.get_pos(r, c, self.off_x, self.off_y, self.blockSize) for r, c in task.path]
                
                if len(points) > 1:
                    pygame.draw.lines(self.tela, path_color, False, points, 3)
            
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
        self.draw_text("[C] Limpar | [T] Trocar algoritmo | [M] Trocar obstaculo | [H] Mudar Grid Type", 10, self.H - 50)
        
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

                    elif event.key == pygame.K_h:
                        self.grid_type = "hex" if self.grid_type == "rect" else "rect"
                        self.reset_grid()  

                    self.update_status_message() 

            self.draw_all()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = NavigationApp()
    app.run()
