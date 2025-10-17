import time
import numpy as np
import csv
import pandas as pd
import matplotlib.pyplot as plt
import random
import math


def jarvis_march(points_list):
    if len(points_list) < 3:
        return points_list
    
    start_point = min(points_list, key=lambda p: (p[0], p[1]))
    
    hull = []
    current_point = start_point
    
    while True:
        hull.append(current_point)
        if len(points_list) > 0 and all(np.isclose(points_list[0], current_point)):
            endpoint = points_list[1]
        else:
            endpoint = points_list[0]
        
        for next_point in points_list:
            if all(np.isclose(endpoint, current_point)) or cross_product_check(current_point, endpoint, next_point) > 0:
                endpoint = next_point
        
        current_point = endpoint
        if all(np.isclose(current_point, hull[0])):
            break
            
    return hull

def cross_product_check(p1, p2, p3):
    return (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])


def gen_points_random(n, distribution_type, W=1000, H=700):
    if distribution_type == "uniform":
        return np.random.uniform(50, W-50, size=(n, 2))
    elif distribution_type == "cluster":
        pts = []
        centers = [(200, 200), (800, 200), (500, 500)]
        for _ in range(n):
            cx, cy = random.choice(centers)
            x = np.clip(random.gauss(cx, 40), 0, W)
            y = np.clip(random.gauss(cy, 40), 0, H)
            pts.append([x,y])
        return np.array(pts)
    elif distribution_type == "grid":
        n_side = int(np.ceil(np.sqrt(n)))
        xs = np.linspace(50, W - 50, n_side)
        ys = np.linspace(50, H - 50, n_side)
        
        xx, yy = np.meshgrid(xs, ys)
        coords = np.vstack([xx.ravel(), yy.ravel()]).T
        return coords[:n]
    return np.array([])


def quadrant_distribution(hull_coords, W=1000, H=700):
    if len(hull_coords) == 0:
        return [0, 0, 0, 0]
    
    center_x, center_y = W / 2, H / 2
    
    q_counts = np.zeros(4)
    
    for x, y in hull_coords:
        if x >= center_x and y <= center_y:
            q_counts[0] += 1
        elif x < center_x and y <= center_y: 
            q_counts[1] += 1
        elif x < center_x and y > center_y:
            q_counts[2] += 1
        elif x >= center_x and y > center_y:
            q_counts[3] += 1
            
    return q_counts / len(hull_coords)


def gen(ns, distributions, repeats):
    results = []
    
    for dist in distributions:
        for n in ns:
            times = []
            num_on_hull = []
            quadrant_sums = np.zeros(4)
            
            for r in range(repeats):
                coords = gen_points_random(n, dist)
                
                start_time = time.perf_counter()
                hull = jarvis_march(coords)
                end_time = time.perf_counter()
                
                times.append(end_time - start_time)
                num_on_hull.append(len(hull))
                
                quadrant_sums += quadrant_distribution(hull)

            results.append({
                "tipo": dist,
                "qnt_points": n,
                "mean_time": np.mean(times),
                "std_time": np.std(times),
                "mean_hull_points": np.mean(num_on_hull),
                "std_hull_points": np.std(num_on_hull),
                "quadrant_1_mean": quadrant_sums[0] / repeats,
                "quadrant_2_mean": quadrant_sums[1] / repeats,
                "quadrant_3_mean": quadrant_sums[2] / repeats,
                "quadrant_4_mean": quadrant_sums[3] / repeats
            })
            print(f"Dist: {dist}, n: {n}, Tempo: {results[-1]['mean_time']:.4f}s")

    keys = list(results[0].keys())
    with open("convex_hull_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    ns = [100, 200, 500, 1000, 2000, 5000, 10000, 15000, 20000] 
    distributions = ["uniform", "cluster", "grid"]
    gen(ns=ns, distributions=distributions, repeats=10)