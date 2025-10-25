import time
import numpy as np
import csv
import random
import math
from ponto import Ponto

def jarvis_march(points_list):
    if len(points_list) < 3:
        return points_list
    start_point = min(points_list, key=lambda p: (p.x, p.y))
    hull = []
    current_point = start_point
    while True:
        hull.append(current_point)
        endpoint = points_list[0]
        if endpoint == current_point:
            if len(points_list) > 1:
                endpoint = points_list[1]
            else:
                break
        for next_point in points_list:
            if next_point == current_point:
                continue
            orientation = (endpoint.x - current_point.x) * (next_point.y - current_point.y) - \
                          (endpoint.y - current_point.y) * (next_point.x - current_point.x)
            if orientation < 0:
                endpoint = next_point
            elif orientation == 0:
                dist_sq_endpoint = (endpoint.x - current_point.x)**2 + (endpoint.y - current_point.y)**2
                dist_sq_next = (next_point.x - current_point.x)**2 + (next_point.y - current_point.y)**2
                if dist_sq_next > dist_sq_endpoint:
                    endpoint = next_point
        current_point = endpoint
        if current_point == hull[0]:
            break
    return hull

def find_centroid(points):
    if not points:
        return Ponto(0, 0)
    num_points = len(points)
    sum_x = sum(p.x for p in points)
    sum_y = sum(p.y for p in points)
    return Ponto(sum_x / num_points, sum_y / num_points)

def get_reflected_shape(points):
    return [Ponto(-p.x, -p.y) for p in points]

def get_shape_at_origin(points):
    center = find_centroid(points)
    return [p - center for p in points]

def compute_minkowski_sum(poly_P, poly_Q):
    if not poly_P or not poly_Q:
        return []
    all_vertex_sums = []
    for p in poly_P:
        for q in poly_Q:
            all_vertex_sums.append(p + q)
    return jarvis_march(all_vertex_sums)

def get_point_segment_distance(p, a, b):
    px, py = p.x, p.y
    ax, ay = a.x, a.y
    bx, by = b.x, b.y
    ab_x = bx - ax
    ab_y = by - ay
    ap_x = px - ax
    ap_y = py - ay
    ab_len_sq = ab_x**2 + ab_y**2
    if ab_len_sq == 0:
        return math.hypot(ap_x, ap_y)
    t = (ap_x * ab_x + ap_y * ab_y) / ab_len_sq
    if t < 0.0:
        closest_x, closest_y = ax, ay
    elif t > 1.0:
        closest_x, closest_y = bx, by
    else:
        closest_x = ax + t * ab_x
        closest_y = ay + t * ab_y
    return math.hypot(px - closest_x, py - closest_y)

def min_distance_to_origin(polygon_points):
    if not polygon_points:
        return float('inf')
    origin = Ponto(0, 0)
    test_hull = jarvis_march(polygon_points + [origin])
    if len(test_hull) == len(polygon_points):
        return 0.0
    min_dist = float('inf')
    num_points = len(polygon_points)
    for i in range(num_points):
        p1 = polygon_points[i]
        p2 = polygon_points[(i + 1) % num_points]
        dist = get_point_segment_distance(origin, p1, p2)
        if dist < min_dist:
            min_dist = dist
    return min_dist


def generate_random_convex_polygon(target_vertices, center_x=500, center_y=350, radius=300):
    points_for_hull = []
    num_to_generate = target_vertices * 3
    for _ in range(num_to_generate):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(radius * 0.8, radius) 
        x = center_x + dist * math.cos(angle)
        y = center_y + dist * math.sin(angle)
        points_for_hull.append(Ponto(x,y))
    if not points_for_hull:
        return []
    return jarvis_march(points_for_hull)

def run_analysis(vertex_sizes, repeats=5):
    results = []
    
    print(f"Testando com {repeats} repeticoes para cada N")
    print("N (Alvo) | m (Real) | n (Real) | m*n (Pontos) | Tempo Medio (s) | Distância Minima")
    print("-" * 80)
    
    header = [
        "target_vertices", "m_real", "n_real", "mn_points_generated", 
        "mean_time_s", "std_time_s", "min_distance"
    ]
    results.append(header)
    
    for n in vertex_sizes:
        m = n
        times = []
        distances = []
        real_m_avg = 0
        real_n_avg = 0
        
        for _ in range(repeats):
            poly_P = generate_random_convex_polygon(m) 
            poly_Q_shape = generate_random_convex_polygon(n, center_x=100, center_y=100, radius=50)
            
            if len(poly_P) < 3 or len(poly_Q_shape) < 3:
                continue

            real_m_avg += len(poly_P)
            real_n_avg += len(poly_Q_shape)

            start_time = time.perf_counter()
            cs_poly = compute_minkowski_sum(poly_P, poly_Q_shape)
            end_time = time.perf_counter()
            times.append(end_time - start_time)
            
            dist = min_distance_to_origin(cs_poly)
            distances.append(dist)

        if not times:
            continue
            
        mean_time = np.mean(times)
        std_time = np.std(times)
        mean_dist = np.mean(distances)
        real_m = int(real_m_avg / repeats)
        real_n = int(real_n_avg / repeats)
        mn_points = real_m * real_n
        
        print(f"{n:<8} | {real_m:<8} | {real_n:<8} | {mn_points:<12} | {mean_time:<13.6f} | {mean_dist:<16.2f}")
        
        results.append([
            n, real_m, real_n, mn_points, 
            mean_time, std_time, mean_dist
        ])

    csv_filename = "minkowski_results.csv"
    try:
        with open(csv_filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(results)
        print(f"\nResultados salvos com sucesso em: {csv_filename}")
    except IOError as e:
        print(f"\nErro ao salvar o arquivo CSV: {e}")
        
    return csv_filename


if __name__ == "__main__":
    n_sizes = [10, 20, 30, 40, 50, 70, 90, 110] 
    run_analysis(n_sizes, repeats=5)
