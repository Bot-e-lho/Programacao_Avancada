## Miguel Rodrigues Botelho -- 21202191
## Trabalho 11: SAD 4

import pygame
import sys
import math
import numpy as np
import pandas as pd
import datetime
import random
import heapq 
import matplotlib.pyplot as plt
from ponto import Ponto
from factories import *
from pathfiding import *
from chain import PygameInitHandler, GridConfigHandler, AssetsInitHandler
from commands import MoveAgentCommand, CommandHistory
from observer import Subject, ObserverA
from strategies import AvoidanceStrategy, NoCommunicationStrategy, DirectCommunicationStrategy, IndirectCommunicationStrategy

class Agent(Subject):
    def __init__(self, agent_id, start_pos, path, color, grid_adapter):
        super().__init__()
        self.id = agent_id
        self.velocity = np.array([0.0, 0.0])
        self.desired_v_cache = np.array([0.0, 0.0])
        self.avoidance_strategy = NoCommunicationStrategy()

        p_start = grid_adapter.get_pos(start_pos[0], start_pos[1], app.off_x, app.off_y, app.blockSize)
        self.path = path 
        self.color = color
        self.pos = Ponto(p_start[0], p_start[1])

        self.base_speed = 2.0
        self.grid_adapter = grid_adapter
        self.current_step_index = 0
        self.radius = app.blockSize // 3
        self.is_colliding = False
        self.in_warning = False

        self.avoidance_cooldown = 0
        self.speed = self.base_speed
        self.speed_mult = 1.0
        self.drift_vector = np.array([0.0, 0.0])

        self.life = 100
        self.finished = False

    def get_current_grid_pos(self):
        if not self.path:
            return (0, 0)
        if self.current_step_index >= len(self.path):
            return self.path[-1]
        return self.path[self.current_step_index]

    def take_damage(self, amount):
        self.life -= amount
        print(f"Dano detectado\n Vida: {self.life}")
        if self.life <= 0:
            self.notify()

    def set_avoidance_method(self, strategy: AvoidanceStrategy):
        self.avoidance_strategy = strategy 

    def respawn(self):
        self.life = 100
        self.current_step_index = 0
        self.finished = False

    def update(self, others):
        if self.finished or not self.path:
            return

        targe_grid = self.path[self.current_step_index]
        target_pixel = self.grid_adapter.get_pos(targe_grid[0], targe_grid[1], app.off_x, app.off_y, app.blockSize)
        target_vector = np.array([target_pixel[0], target_pixel[1]])
        current_vector = np.array([self.pos.x, self.pos.y])

        direction = target_vector - current_vector
        dist = np.linalg.norm(direction)

        if dist < 5.0:
            self.current_step_index += 1
            if self.current_step_index >= len(self.path):
                self.finished = True
                return
            
            targe_grid = self.path[self.current_step_index]
            target_pixel = self.grid_adapter.get_pos(targe_grid[0], targe_grid[1], app.off_x, app.off_y, app.blockSize)
            target_vector = np.array([target_pixel[0], target_pixel[1]])
            direction = target_vector - current_vector
            dist = np.linalg.norm(direction)

        desired_v = np.array([0.0, 0.0])

        if dist > 0:
            desired_v = (direction / dist) * self.base_speed 

        self.desired_v_cache = desired_v

        game_params = (app.off_x, app.off_y, app.blockSize)
        self.velocity = self.avoidance_strategy.compute_velocity(self, desired_v, others, self.grid_adapter, game_params)

        next_x = self.pos.x + self.velocity[0]
        next_y = self.pos.y + self.velocity[1]
        
        grid_coords = self.grid_adapter.get_grid_coords(next_x, next_y, app.off_x, app.off_y, app.blockSize)
        
        is_valid_move = False
        if grid_coords is not None:
            next_r, next_c = grid_coords  
            
            if self.grid_adapter.data[next_r, next_c] is None:
                is_valid_move = True
            elif (next_r, next_c) == self.path[-1]: 
                is_valid_move = True

        if is_valid_move:
            self.pos.x = next_x
            self.pos.y = next_y
        else:
            self.drift_vector = np.array([0.0, 0.0])
            self.avoidance_cooldown = 10
        


    def draw(self, surface):
        draw_color = self.color
        if self.is_colliding:
            draw_color = (255, 0, 0)
            
        elif self.in_warning:
            draw_color = (255, 255, 0)

        pygame.draw.circle(surface, draw_color, self.pos.int_pos(), self.radius)

class NavigationApp:
    
    def __init__(self):
        init_chain = PygameInitHandler()
        grid_config = GridConfigHandler()
        assets_init = AssetsInitHandler()

        init_chain.set_next(grid_config).set_next(assets_init)
        init_chain.handle(self)

        self.reset_grid()

        self.command_history = CommandHistory()
        self.game_observer = ObserverA()
        self.agents = []
        self.quality_data = []

        self.current_mode = 1 
        self.current_path_pair = [None, None]
        self.task_list = [] 
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
        self.agents = []
        self.task_list = []
        self.current_path_pair = [None, None]
        self.quality_data = []

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
        self.grid.fill_random_obstacles(self.obstacle_factory, self.obstacle_keys[self.current_obstacle_index], percentage)
        self.agents = []
        self.status_message = f"Obstaculos aleatorios adicionados"

    def handle_click(self, pos):
        cell = self.pos_to_grid(pos[0], pos[1])
        if cell is None: 
            return

        if self.current_mode == 1: 
            key = self.obstacle_keys[self.current_obstacle_index]
            self.grid.toggle_obstacle(cell[0], cell[1], self.obstacle_factory, key)
            self.completed_tasks = [] 
        
        elif self.current_mode == 2: 
            if self.grid.data[cell] is not None: 
                return

            if self.current_path_pair[0] is None:
                self.current_path_pair[0] = cell
            elif self.current_path_pair[1] is None:
                if cell == self.current_path_pair[0]: 
                    return
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
        if len(free) < 2: 
            return
        for _ in range(count):
            s = random.choice(free)
            g = random.choice(free)
            algo = random.choice(self.algo_keys)
            self.task_list.append(self.task_factory.create_task(s, g, algo))

    def run_all_paths(self):
        self.agents = []
        for i, task in enumerate(self.task_list):
            path = task.pathfinder.find_path(self.grid, task.start, task.goal)
            if path:
                new_agent = Agent(i, task.start, path, task.color, self.grid)
                new_agent.attach(self.game_observer)
                self.agents.append(new_agent)
        
        self.task_list = [] 
        self.status_message = f"Agentes criados: {len(self.agents)}"


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

        for agent in self.agents:
            path_color = agent.color
            if agent.path:
                points = [self.grid.get_pos(r, c, self.off_x, self.off_y, self.blockSize) for r, c in agent.path]
                    
                if len(points) > 1:
                    pygame.draw.lines(self.tela, path_color, False, points, 3)

                goal_r, goal_c = agent.path[-1]
                goal_pos = self.grid_to_pos(goal_r, goal_c)
                goal_rect = pygame.Rect(goal_pos.x - self.blockSize / 3, goal_pos.y - self.blockSize / 3, self.blockSize * 2 / 3, self.blockSize * 2 / 3)
                pygame.draw.rect(self.tela, path_color, goal_rect)

    def calculate_metrics(self):
        deviation_sum = 0
        for agent in self.agents:
            deviation_sum += np.linalg.norm(agent.velocity - agent.desired_v_cache)
        
        self.quality_data.append(deviation_sum / len(self.agents))

    def draw_all(self):
        self.tela.fill((173, 216, 230))
        
        self.grid.draw(self.tela, self.off_x, self.off_y, self.blockSize)
        self.draw_paths()

        for agent in self.agents:
            agent.draw(self.tela)

        self.draw_text(self.status_message, 10, 10)
        self.draw_text("[J] Sem Com. | [K] Indireta | [L] Direta (RVO)", 10, self.H - 130)
        self.draw_text("[1] Obstaculos | [2] Start/Goal", 10, self.H - 110)
        self.draw_text("[G] Gerar pares | [R] Rodar | [O] Obstac. aleatorios", 10, self.H - 70)
        self.draw_text("[C] Limpar | [T] Trocar algoritmo | [M] Trocar obstaculo | [H] Mudar Grid", 10, self.H - 50)
        self.draw_text("[A] Mover | [Z] Undo | [D] Dano agente", 10, self.H - 90)
        
        algo_name = self.algo_keys[self.current_algo_index]
        self.draw_text(f"Algoritmo atual: {algo_name}", 10, self.H - 30)

    def run(self):
        running = True
        self.data = []
        frame_count = 0

        while running:
            self.grid.update_movables()
            active_agents = [agent for agent in self.agents if not agent.finished]
            
            if hasattr(self.grid, 'clear_reservations'): 
                self.grid.clear_reservations()

            if active_agents:
                deviation = sum(np.linalg.norm(a.velocity - a.desired_v_cache) for a in active_agents) / len(active_agents)
                self.quality_data.append(deviation)
                
                self.data.append({
                    "frame": frame_count,
                    "active": len(active_agents),
                    "colliding": sum(1 for a in self.agents if a.is_colliding),
                    "quality_dev": deviation
                })
                frame_count += 1

            for agent in active_agents:
                agent.update(active_agents)

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
                        self.generate_random_pairs(20) 
                    
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
                        self.agents = []
                        self.task_list = []

                    elif event.key == pygame.K_h:
                        self.grid_type = "hex" if self.grid_type == "rect" else "rect"
                        self.reset_grid()  

                    elif event.key == pygame.K_z:
                        if self.agents:
                            for _ in self.agents:
                                self.command_history.undo_last()

                    elif event.key == pygame.K_d:
                        if self.agents:
                            self.agents[0].take_damage(50)
                    
                    elif event.key == pygame.K_j:
                        for a in self.agents: 
                            a.set_avoidance_method(NoCommunicationStrategy())
                    elif event.key == pygame.K_k:
                        for a in self.agents: 
                            a.set_avoidance_method(IndirectCommunicationStrategy())
                    elif event.key == pygame.K_l:
                        for a in self.agents: 
                            a.set_avoidance_method(DirectCommunicationStrategy())

                    self.update_status_message() 

            self.draw_all()
            pygame.display.flip()
            self.clock.tick(60)
        
        if self.quality_data:
            plt.figure(figsize=(10, 5))
            plt.subplot(1, 2, 1)
            plt.plot(self.quality_data)
            plt.title("Qualidade: Desvio da Rota Ideal")
            plt.xlabel("Frames")
            plt.ylabel("Erro de Velocidade")
            
            plt.subplot(1, 2, 2)
            plt.plot([d["colliding"] for d in self.data])
            plt.title("Performance: Concorrência/Colisões")
            plt.show()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = NavigationApp()
    app.run()
    