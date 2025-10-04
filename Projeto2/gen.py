import time
import numpy as np
import csv
from scipy.spatial import Voronoi, Delaunay

def gen_points(n, types, W=1000, H=700):
    if types == "uniform":
        xs = np.random.uniform(50, W-50, size=n)
        ys = np.random.uniform(50, H-50, size=n)
        return np.column_stack((xs, ys))
    elif types == "cluster":
        pts = []
        centers = [(200,200),(800,200),(500,500)]
        for i in range(n):
            cx, cy = centers[i % len(centers)]
            x = np.clip(np.random.normal(cx, 40), 0, W)
            y = np.clip(np.random.normal(cy, 40), 0, H)
            pts.append((x,y))
        return np.array(pts)
    elif types == "grid":
        side = int(np.ceil(np.sqrt(n)))
        xs = np.linspace(50, W-50, side)
        ys = np.linspace(50, H-50, side)
        pts = []
        for i in range(n):
            xi = i % side
            yi = i // side
            pts.append((xs[xi], ys[yi]))
        return np.array(pts)
    else:
        return gen_points(n, "uniform")

def time_one_run(coords):
    t0 = time.perf_counter()
    _ = Delaunay(coords)
    t1 = time.perf_counter()
    try:
        _ = Voronoi(coords)
        t2 = time.perf_counter()
    except Exception:
        t2 = time.perf_counter()
    return (t1 - t0), (t2 - t1)

def gen(ns=[100, 200, 500, 1000, 2000, 5000, 10000, 15000, 20000, 100000, 10000000], type=["uniform","cluster","grid"]):
    results = []
    for dist in type:
        for n in ns:
            times_del = []
            times_vor = []
            for r in range(5):
                coords = gen_points(n, dist)
                coords += np.random.normal(scale=1e-6, size=coords.shape)
                td, tv = time_one_run(coords)
                times_del.append(td)
                times_vor.append(tv)
            results.append({
                "tipo": dist,
                "qnt_points": n,
                "delaunay_mean": sum(times_del)/len(times_del),
                "delaunay_std": (np.std(times_del)),
                "voronoi_mean": sum(times_vor)/len(times_vor),
                "voronoi_std": (np.std(times_vor)),
            })
            print(f"{dist} n={n}: D {results[-1]['delaunay_mean']:.4f}s V {results[-1]['voronoi_mean']:.4f}s")
    keys = list(results[0].keys())
    with open("results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    ns = [100, 200, 500, 1000, 2000, 5000, 10000, 15000, 20000, 100000]  
    gen(ns=ns, type=["uniform","cluster","grid"])
