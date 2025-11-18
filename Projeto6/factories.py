from pathfiding import *
import numpy as np
import pygame
import random
from abc import *

class PathfindingFactory(ABC):
    @abstractmethod
    def create_pathfinder(self):
        pass

class VH_A_Star_Factory(PathfindingFactory):
    def create_pathfinder(self):
        heuristic = ManhattanHeuristic()
        neighbors = FourWay()
        return AStarPathfinder(heuristic, neighbors)

class Diag_A_Star_Factory(PathfindingFactory):
    def create_pathfinder(self):
        heuristic = DiagonalHeuristic()
        neighbors = EightWay()
        return AStarPathfinder(heuristic, neighbors)

class Factory_Dijkstra(PathfindingFactory):
    def create_pathfinder(self):
        heuristic = NullHeuristic()
        neighbors = FourWay()
        return AStarPathfinder(heuristic, neighbors)
    
class Factory_Dijkstra_Diag(PathfindingFactory):
    def create_pathfinder(self):
        heuristic = NullHeuristic()
        neighbors = EightWay() 
        return AStarPathfinder(heuristic, neighbors)

class Obstacle(ABC):
    def __init__(self, r, c):
        self.r = r
        self.c = c
        self.color = (255, 0, 0)
    
    @abstractmethod
    def draw(self, surface, rect):
        pass

    @abstractmethod 
    def update(self, grid):
        pass

class Wall(Obstacle):
    def __init__(self, r, c):
        super().__init__(r, c)
        self.color = (52, 52, 52)

    def draw(self, surface, rect):
        pygame.draw.rect(surface, self.color, rect)
        
    def update(self, grid):
        pass


class MovableObstacle(Obstacle):
    def __init__(self, r, c):
        super().__init__(r, c)
        self.color = (0, 0, 200) 
        self.move_timer = 0
        self.move_delay = 30 
    
    def update(self, grid):
        self.move_timer += 1
        if self.move_timer < self.move_delay:
            return

        self.move_timer = 0
        dir_c = random.choice([-1, 1])
        new_c = self.c + dir_c
        
        if 0 <= new_c < grid.cols and grid.data[self.r, new_c] is None:
            grid.data[self.r, new_c] = self
            grid.data[self.r, self.c] = None
            self.c = new_c
            
    def draw(self, surface, rect):
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, (255,255,255), rect, 2)


class ObstacleFactory:
    def create_obstacle(self, key, r, c):
        if key == "wall":
            return Wall(r, c)
        elif key == "movable":
            return MovableObstacle(r, c)
        raise ValueError(f"Tipo de obdtaculo desconhecido: {key}")

class Grid:
    def __init__(self, rows, cols, free_color):
        self.rows = rows
        self.cols = cols
        self.free_color = free_color
        self.data = np.full((rows, cols), None, dtype=object)

    def draw(self, surface, offset_x, offset_y, block_size):
        for r in range(self.rows):
            for c in range(self.cols):
                rect = pygame.Rect(offset_x + c * block_size, offset_y + r * block_size, block_size, block_size)
                
                obstacle_obj = self.data[r, c]
                
                if obstacle_obj is not None:
                    obstacle_obj.draw(surface, rect)
                else:
                    pygame.draw.rect(surface, self.free_color, rect)
                
                pygame.draw.rect(surface, (12, 8, 20), rect, 1) 

    def update_movables(self):
        for r in range(self.rows):
            for c in range(self.cols):
                obj = self.data[r, c]
                if isinstance(obj, MovableObstacle):
                    obj.update(self) 

    def toggle_obstacle(self, r, c, factory, key):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            if self.data[r, c] is None:
                self.data[r, c] = factory.create_obstacle(key, r, c)
            else:
                self.data[r, c] = None
            
    def get_data(self):
        return self.data
    

    def fill_random_obstacles(self, factory, key, percentage):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.data[r, c] is None and random.random() < percentage:
                    self.data[r, c] = factory.create_obstacle(key, r, c)
                    
    def clear(self):
        self.data.fill(None)


class GridFactory:
    def create_grid(self, rows, cols, free_color):
        return Grid(rows, cols, free_color)
    
class PathTask:
    def __init__(self, start, goal, pathfinder, color, algorithm_key=None):
        self.start = start
        self.goal = goal
        self.pathfinder = pathfinder
        self.color = color
        self.path = []
        self.algorithm_key = algorithm_key

class TaskFactory:
    def __init__(self, path_factories, colors):
        self.path_factories = path_factories
        self.colors = colors
        self.color_index = 0

    def create_task(self, start, goal, algorithm_key):
        if algorithm_key not in self.path_factories:
            raise ValueError(f"Erro de algoritmo: {algorithm_key}")
            
        factory = self.path_factories[algorithm_key]
        pathfinder = factory.create_pathfinder()
        color = self.colors[self.color_index % len(self.colors)]
        self.color_index += 1
        
        return PathTask(start, goal, pathfinder, color, algorithm_key)
