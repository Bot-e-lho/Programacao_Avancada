import time
import numpy as np
import csv
import random
import math
import heapq
import sys
import pandas as pd


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(grid_param, start, goal):
    if grid_param[start] == 1 or grid_param[goal] == 1:
        return []
    
    ROWS, COLS = grid_param.shape 
    
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
            if 0 <= nr < ROWS and 0 <= nc < COLS and grid_param[nr, nc] == 0: 
                tentative_g_score = g_score[current_node] + 1
                
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current_node
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                            
    return []


def create_sparse_grid(rows, cols, obstacle_ratio=0.2):
    grid = np.zeros((rows, cols), dtype=int)
    num_obstacles = int(rows * cols * obstacle_ratio)
    for _ in range(num_obstacles):
        r = random.randint(0, rows - 1)
        c = random.randint(0, cols - 1)
        grid[r, c] = 1
    return grid

def create_maze_grid(rows, cols):
    grid = np.zeros((rows, cols), dtype=int)
    for c in range(cols):
        if c % 2 == 0:
            for r in range(rows - 2): 
                grid[r, c] = 1
    return grid

def get_random_free_cells_pair(grid):
    rows, cols = grid.shape
    free_cells = [(r, c) for r in range(rows) for c in range(cols) if grid[r, c] == 0]
    
    if len(free_cells) < 2:
        return None, None
        
    start = random.choice(free_cells)
    goal = random.choice(free_cells)
    while start == goal:
        goal = random.choice(free_cells)
    
    return start, goal

def analyze_agent_count(grid_size, agent_counts, repeats):
    results = []
    grid = create_sparse_grid(grid_size[0], grid_size[1], 0.2)
    
    for count in agent_counts:
        time_samples = []
        for _ in range(repeats):
            pairs = []
            for _ in range(count):
                s, g = get_random_free_cells_pair(grid)
                if s: pairs.append((s, g))
            
            if not pairs: continue

            start_time = time.perf_counter()
            for start, goal in pairs:
                path = a_star(grid, start, goal) 
            end_time = time.perf_counter()
            
            time_samples.append(end_time - start_time)
        
        mean_time = np.mean(time_samples)
        print(f"Agentes: {count:<4} | Tempo Médio: {mean_time:.6f} s")
        results.append({
            "test_type": "agent_count",
            "agent_count": count,
            "grid_rows": grid_size[0],
            "grid_cols": grid_size[1],
            "mean_time_s": mean_time
        })
    return results

def analyze_grid_resolution(resolution_sizes, repeats):
    results = []
    
    for (rows, cols) in resolution_sizes:
        time_samples = []
        grid = create_sparse_grid(rows, cols, 0.2)
        
        for _ in range(repeats):
            start, goal = get_random_free_cells_pair(grid)
            if not start: continue
            
            start_time = time.perf_counter()
            path = a_star(grid, start, goal)
            end_time = time.perf_counter()
            
            if path:
                time_samples.append(end_time - start_time)
        
        if not time_samples: continue
            
        mean_time = np.mean(time_samples)
        
        print(f"Grid: {rows}x{cols:<5} | Células: {rows*cols:<6} | Tempo Médio: {mean_time:.6f} s")
        results.append({
            "test_type": "resolution",
            "grid_rows": rows,
            "grid_cols": cols,
            "grid_cells": rows * cols,
            "mean_time_s": mean_time,
        })
    return results

def analyze_obstacle_distribution(grid_size, repeats):
    results = []
    
    grid_sparse = create_sparse_grid(grid_size[0], grid_size[1], 0.25)
    grid_maze = create_maze_grid(grid_size[0], grid_size[1])
    
    grids_to_test = {"sparse_25pct": grid_sparse, "maze_columns": grid_maze}
    
    for dist_name, grid in grids_to_test.items():
        time_samples = []
        path_lengths = []
        
        for _ in range(repeats):
            start, goal = get_random_free_cells_pair(grid)
            if not start: continue
            
            start_time = time.perf_counter()
            path = a_star(grid, start, goal)
            end_time = time.perf_counter()
            
            if path:
                time_samples.append(end_time - start_time)
                path_lengths.append(len(path))
        
        if not time_samples: continue

        mean_time = np.mean(time_samples)
        mean_path_len = np.mean(path_lengths)
        
        print(f"Distribuição: {dist_name:<15} | Tempo Médio: {mean_time:.6f} s | Comprimento: {mean_path_len:.1f}")
        results.append({
            "test_type": "distribution",
            "distribution_type": dist_name,
            "grid_rows": grid_size[0],
            "grid_cols": grid_size[1],
            "mean_time_s": mean_time,
            "mean_path_length": mean_path_len
        })
    return results

def analyze_path_length(grid_size, repeats):
    results = []
    grid = create_maze_grid(grid_size[0], grid_size[1]) 
    
    for i in range(repeats):
        start, goal = get_random_free_cells_pair(grid)
        if not start: continue
        
        start_time = time.perf_counter()
        path = a_star(grid, start, goal)
        end_time = time.perf_counter()
        
        if path:
            path_len = len(path)
            time_taken = end_time - start_time
            
            results.append({
                "test_type": "path_length",
                "grid_rows": grid_size[0],
                "grid_cols": grid_size[1],
                "run_id": i,
                "time_s": time_taken,
                "path_length": path_len,
            })
    
    print(f"Gerado {len(results)} caminhos para a Análise 4.")
    return results

if __name__ == "__main__":
    
    all_results_data = []
    
    grid_agentes = (30, 30)
    counts = [1, 10, 25, 50, 100, 150, 200, 300]
    all_results_data.extend(analyze_agent_count(grid_agentes, counts, repeats=10))

    resolutions = [(10, 10), (20, 20), (30, 30), (40, 40), (50, 50), (75, 75), (100, 100)]
    all_results_data.extend(analyze_grid_resolution(resolutions, repeats=20))

    grid_dist = (40, 40)
    all_results_data.extend(analyze_obstacle_distribution(grid_dist, repeats=100))

    grid_path_len = (50, 50)
    all_results_data.extend(analyze_path_length(grid_path_len, repeats=300))
    
    
    csv_filename = "navegacao_analysis_results.csv"

    df = pd.DataFrame(all_results_data)
    df.to_csv(csv_filename, index=False)

    print(f"\nDados salvos em '{csv_filename}'.")