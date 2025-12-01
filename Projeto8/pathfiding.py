import heapq
import math
from abc import *

class Pathfinder(ABC):
    @abstractmethod
    def find_path(self, grid, start, goal):
        pass

class GetStrategy(ABC):
    @abstractmethod
    def get_neighbors(self, grid, node):
        pass

class Heuristic(ABC):
    @abstractmethod
    def calculate(self, a, b):
        pass

class FourWay(GetStrategy):
    def get_neighbors(self, grid, node):
        r, c = node
        neighbors = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        valid_neighbors = []
        for nr, nc in neighbors:
            if 0 <= nr < grid.rows and 0 <= nc < grid.cols and grid.data[nr, nc] is None:
                valid_neighbors.append(((nr, nc), 1)) 
        return valid_neighbors

class EightWay(GetStrategy):
    def get_neighbors(self, grid, node):
        r, c = node
        neighbors = []
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr = r + dr
            nc = c + dc
            if 0 <= nr < grid.rows and 0 <= nc < grid.cols and grid.data[nr, nc] is None:
                neighbors.append(((nr, nc), 1))
        for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nr = r + dr
            nc = c + dc
            if 0 <= nr < grid.rows and 0 <= nc < grid.cols and grid.data[nr, nc] is None:
                if grid.data[r, nc] is None and grid.data[nr, c] is None:
                    neighbors.append(((nr, nc), 1.414))
        return neighbors
    
class HexStrategy(GetStrategy):
    def get_neighbors(self, grid, node):
        r, c = node
        if r % 2 == 0:
            offsets = [(-1, -1), (-1, 0), (0, -1), (0, 1), (1, -1), (1, 0)]
        else:
            offsets = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0), (1, 1)]

        valid_neighbors = []
        for dr, dc in offsets:
            nr = r + dr
            nc = c + dc
            if 0 <= nr < grid.rows and 0 <= nc < grid.cols and grid.data[nr, nc] is None:
                valid_neighbors.append(((nr, nc), 1))
        return valid_neighbors

class ManhattanHeuristic(Heuristic):
    def calculate(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

class DiagonalHeuristic(Heuristic):
    D = 1 
    D2 = 1.414 
    def calculate(self, a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return self.D * (dx + dy) + (self.D2 - 2 * self.D) * min(dx, dy)

class NullHeuristic(Heuristic):
    def calculate(self, a, b):
        return 0

class AStarPathfinder(Pathfinder):
    def __init__(self, heuristic, neighbor_strategy):
        self.heuristic = heuristic
        self.neighbor_strategy = neighbor_strategy

    def find_path(self, grid, start, goal):
        if grid.data[start] is not None or grid.data[goal] is not None:
            return []

        g_score = { (r, c): float('inf') for r in range(grid.rows) for c in range(grid.cols) }
        g_score[start] = 0
        f_score = { (r, c): float('inf') for r in range(grid.rows) for c in range(grid.cols) }
        f_score[start] = self.heuristic.calculate(start, goal)
        
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
            
            for neighbor, cost in self.neighbor_strategy.get_neighbors(grid, current_node):
                tentative_g_score = g_score[current_node] + cost
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current_node
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic.calculate(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))      
        return []
