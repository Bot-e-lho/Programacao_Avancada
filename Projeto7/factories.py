from pathfiding import *
import numpy as np
import pygame
import random
from abc import *


class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

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

class Factory_Hex_A_Star(PathfindingFactory):
    def create_pathfinder(self):
        heuristic = ManhattanHeuristic()
        neighbors = HexStrategy()
        return AStarPathfinder(heuristic, neighbors)

class Obstacle(ABC):
    def __init__(self, r, c):
        self.r = r
        self.c = c
        self.color = (52, 52, 52)
    
    @abstractmethod
    def draw(self, surface, rect):
        pass

    @abstractmethod 
    def update(self, grid):
        pass

class Wall(Obstacle):
    def draw(self, surface, rect):
        pygame.draw.rect(surface, self.color, rect)
    def update(self, grid):
        pass

class ObstacleDecorator(Obstacle):
    def __init__(self, obstacle: Obstacle):
        self.wrapped = obstacle
        self.r = obstacle.r 
        self.c = obstacle.c
        self.color = obstacle.color
    
    def draw(self, surface, rect):
        self.wrapped.draw(surface, rect)
    
    def update(self, grid):
        self.wrapped.update(grid)
        self.r = self.wrapped.r
        self.c = self.wrapped.c
        self.color = self.wrapped.color


class MovableDecorator(ObstacleDecorator):
    def __init__(self, obstacle: Obstacle):
        super().__init__(obstacle)
        self.wrapped.color = (0, 0, 80) 
        self.color = self.wrapped.color
        self.move_timer = 0
        self.move_delay = 30
        
    def update(self, grid):
        super().update(grid)
        
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
            self.wrapped.c = new_c 
            self.wrapped.r = self.r

    def draw(self, surface, rect):
        super().draw(surface, rect)
        pygame.draw.rect(surface, (255, 255, 255), rect, 2)


class ObstacleFactory(metaclass=SingletonMeta): 
    def create_obstacle(self, key, r, c):
        base_obstacle = Wall(r, c)
        
        if key == "wall":
            return base_obstacle
        elif key == "movable":
            return MovableDecorator(base_obstacle)
        raise ValueError(f"Tipo desconhecido: {key}")

class Grid:
    @abstractmethod
    def draw(self, surface, offset_x, offset_y, block_size): 
        pass
    @abstractmethod
    def get_pixel_pos(self, r, c, off_x, off_y, size): 
        pass
    @abstractmethod
    def get_grid_coords(self, pixel_x, pixel_y, off_x, off_y, size):
        pass


class RectGrid(Grid):
    def __init__(self, rows, cols, free_color):
        self.rows = rows; self.cols = cols; self.free_color = free_color
        self.data = np.full((rows, cols), None, dtype=object)

    def draw(self, surface, offset_x, offset_y, block_size):
        for r in range(self.rows):
            for c in range(self.cols):
                rect = pygame.Rect(offset_x + c * block_size, offset_y + r * block_size, block_size, block_size)
                obj = self.data[r, c]
                if obj: obj.draw(surface, rect)
                else: pygame.draw.rect(surface, self.free_color, rect)
                pygame.draw.rect(surface, (12, 8, 20), rect, 1)

    def get_pixel_pos(self, r, c, off_x, off_y, size):
        return (off_x + c * size + size/2, off_y + r * size + size/2)
    
    def get_grid_coords(self, pixel_x, pixel_y, off_x, off_y, size):
        x_rel = pixel_x - off_x
        y_rel = pixel_y - off_y
        c = int(x_rel // size)
        r = int(y_rel // size)
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return (r, c)
        return None
    

class HexGrid(Grid):
    def __init__(self, rows, cols, free_color):
        self.rows = rows; self.cols = cols; self.free_color = free_color
        self.data = np.full((rows, cols), None, dtype=object)

    
    def _calc_hex_center(self, r, c, off_x, off_y, size):
        radius = size / 2
        w = size 
        h = size * 0.866 
        
        x = off_x + c * w + (w/2 if r % 2 == 1 else 0) + w/2
        y = off_y + r * (h * 0.85) + h/2 
        
        return x, y

    def draw_hex(self, surface, color, x, y, size):
        points = []
        for i in range(6):
            angle_deg = 60 * i + 30
            angle_rad = math.pi / 180 * angle_deg
            px = x + size/2 * math.cos(angle_rad)
            py = y + size/2 * math.sin(angle_rad)
            points.append((px, py))
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, (12, 8, 20), points, 1) 

    def get_pixel_pos(self, r, c, off_x, off_y, size):
        return self._calc_hex_center(r, c, off_x, off_y, size)

    def draw(self, surface, offset_x, offset_y, block_size):
        for r in range(self.rows):
            for c in range(self.cols):
                cx, cy = self.get_pixel_pos(r, c, offset_x, offset_y, block_size)
                obj = self.data[r, c]
                color = obj.color if obj else self.free_color
                self.draw_hex(surface, color, cx, cy, block_size)

    
    def get_grid_coords(self, pixel_x, pixel_y, off_x, off_y, size):
        closest_dist = float('inf')
        closest_cell = None

        for r in range(self.rows):
            for c in range(self.cols):
                cx, cy = self.get_pixel_pos(r, c, off_x, off_y, size)
                dist = math.hypot(pixel_x - cx, pixel_y - cy)
                if dist < size / 2 and dist < closest_dist:
                    closest_dist = dist
                    closest_cell = (r, c)
        
        return closest_cell

class GridAdapter:
    def __init__(self, grid_impl: Grid):
        self.impl = grid_impl
        self.rows = grid_impl.rows
        self.cols = grid_impl.cols
        self.data = grid_impl.data
    
    def draw(self, *args): 
        return self.impl.draw(*args)
    
    def get_pos(self, r, c, off_x, off_y, size):
        return self.impl.get_pixel_pos(r, c, off_x, off_y, size)
    
    def get_grid_coords(self, px, py, off_x, off_y, size):
        return self.impl.get_grid_coords(px, py, off_x, off_y, size)

    def update_movables(self):
        for r in range(self.rows):
            for c in range(self.cols):
                obj = self.data[r, c]
                if isinstance(obj, MovableDecorator): 
                    obj.update(self) 
                    
    def toggle_obstacle(self, r, c, factory, key):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            if self.data[r, c] is None:
                self.data[r, c] = factory.create_obstacle(key, r, c)
            else:
                self.data[r, c] = None
                
    def fill_random_obstacles(self, factory, key, pct):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.data[r, c] is None and random.random() < pct:
                    self.data[r, c] = factory.create_obstacle(key, r, c)
    
    def clear(self): self.data.fill(None)

class GridFactory(metaclass=SingletonMeta): 
    def create_grid(self, type_key, rows, cols, free_color):
        if type_key == "rect":
            return GridAdapter(RectGrid(rows, cols, free_color))
        elif type_key == "hex":
            return GridAdapter(HexGrid(rows, cols, free_color))
        raise ValueError("Tipo de grid invalido")
    
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
        factory = self.path_factories[algorithm_key]
        pathfinder = factory.create_pathfinder()
        color = self.colors[self.color_index % len(self.colors)]
        self.color_index += 1
        return PathTask(start, goal, pathfinder, color)
