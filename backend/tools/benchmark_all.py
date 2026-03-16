"""
benchmark_all.py
================
Συγκρίνει ΟΛΕΣτις στρατηγικές query για το GEO-ADS:
  1. Linear Scan     O(n)
  2. R-Tree          O(log n)  in-memory
  3. Distributed     O(log n/k) × 3 nodes parallel

Χρήση:
    cd backend
    python tools/benchmark_all.py

Παράγει: benchmark_all_results.csv
"""

import random
import time
import csv
from math import hypot
from concurrent.futures import ThreadPoolExecutor
from rtree import index as rtree_index


# ── Stub Screen ──────────────────────────────────────────────────────────────

class FakeScreen:
    __slots__ = ("id", "zone_id", "row", "col", "screen_type")
    ZONES = ["glassfloor", "surrounding", "megatron"]

    def __init__(self, i, zone_id, row, col):
        self.id         = f"S-{i}"
        self.zone_id    = zone_id
        self.row        = row
        self.col        = col
        self.screen_type = "generic"


def generate_screens(n: int) -> list:
    screens = []
    zones = FakeScreen.ZONES
    for i in range(n):
        z = zones[i % 3]
        row = random.uniform(0, 100)
        col = random.uniform(0, 100)
        screens.append(FakeScreen(i, z, row, col))
    return screens


# ── 1. Linear Scan ───────────────────────────────────────────────────────────

def build_linear(screens):
    return [(float(s.col), float(s.row), s) for s in screens]

def query_linear(coords, x, y, radius):
    return [s for sx, sy, s in coords if hypot(sx-x, sy-y) <= radius]


# ── 2. R-Tree (single node) ──────────────────────────────────────────────────

def build_rtree(screens):
    prop = rtree_index.Property(); prop.dimension = 2
    idx = rtree_index.Index(properties=prop)
    id_map = {}
    for i, s in enumerate(screens):
        x, y = float(s.col), float(s.row)
        idx.insert(i, (x, y, x, y))
        id_map[i] = (x, y, s)
    return idx, id_map

def query_rtree(idx, id_map, x, y, radius):
    bbox = (x-radius, y-radius, x+radius, y+radius)
    res = []
    for i in idx.intersection(bbox):
        sx, sy, s = id_map[i]
        if hypot(sx-x, sy-y) <= radius:
            res.append(s)
    return res


# ── 3. Distributed (3 shards, parallel) ─────────────────────────────────────

class Shard:
    def __init__(self, screens):
        self._screens = screens
        prop = rtree_index.Property(); prop.dimension = 2
        self._rtree = rtree_index.Index(properties=prop)
        self._map = {}
        for i, s in enumerate(screens):
            x, y = float(s.col), float(s.row)
            self._rtree.insert(i, (x, y, x, y))
            self._map[i] = (x, y, s)

    def query(self, x, y, radius):
        bbox = (x-radius, y-radius, x+radius, y+radius)
        res = []
        for i in self._rtree.intersection(bbox):
            sx, sy, s = self._map[i]
            if hypot(sx-x, sy-y) <= radius:
                res.append(s)
        return res

def build_distributed(screens):
    z0 = [s for s in screens if s.zone_id == "glassfloor"]
    z1 = [s for s in screens if s.zone_id == "surrounding"]
    z2 = [s for s in screens if s.zone_id == "megatron"]
    return [Shard(z0), Shard(z1), Shard(z2)]

def query_distributed(shards, x, y, radius):
    def shard_q(sh): return sh.query(x, y, radius)
    with ThreadPoolExecutor(max_workers=3) as ex:
        parts = list(ex.map(shard_q, shards))
    return [s for chunk in parts for s in chunk]


# ── Benchmark ────────────────────────────────────────────────────────────────

SIZES   = [28, 100, 1_000, 10_000, 100_000]
REPEATS = 100
QX, QY, QR = 50.0, 50.0, 10.0


def run():
    hdr = f"{'N':>8}  {'Linear':>11}  {'R-Tree':>11}  {'Distrib':>11}  {'Lin/RT':>7}  {'Lin/Di':>7}"
    sep = "-" * len(hdr)
    print(f"\n{sep}\n{hdr}\n{sep}")

    rows = []
    for n in SIZES:
        screens = generate_screens(n)

        coords  = build_linear(screens)
        rtidx, rtmap = build_rtree(screens)
        shards  = build_distributed(screens)

        def bench(fn):
            t0 = time.perf_counter()
            for _ in range(REPEATS): fn()
            return (time.perf_counter() - t0) / REPEATS * 1000

        t_lin  = bench(lambda: query_linear(coords, QX, QY, QR))
        t_rt   = bench(lambda: query_rtree(rtidx, rtmap, QX, QY, QR))
        t_dist = bench(lambda: query_distributed(shards, QX, QY, QR))

        sp_rt   = t_lin / t_rt   if t_rt   > 0 else 0
        sp_dist = t_lin / t_dist if t_dist > 0 else 0

        print(f"{n:>8,}  {t_lin:>11.4f}  {t_rt:>11.4f}  {t_dist:>11.4f}"
              f"  {sp_rt:>6.1f}x  {sp_dist:>6.1f}x")
        rows.append((n, round(t_lin,6), round(t_rt,6), round(t_dist,6),
                     round(sp_rt,2), round(sp_dist,2)))

    print(f"{sep}")
    print(f"\n  Query: x={QX}, y={QY}, radius={QR}  |  {REPEATS} reps each\n")
    print("  Columns: Linear(ms) | R-Tree(ms) | Distributed(ms) | Lin/RT speedup | Lin/Dist speedup\n")

    csv_path = "benchmark_all_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["N","Linear_ms","RTree_ms","Distributed_ms","Speedup_RT","Speedup_Dist"])
        writer.writerows(rows)
    print(f"  Results saved: {csv_path}\n")


if __name__ == "__main__":
    random.seed(42)
    run()
