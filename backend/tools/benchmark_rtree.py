"""
benchmark_rtree.py
==================
Σύγκριση O(n) linear scan vs O(log n) R-Tree για το query_near().

Χρήση:
    cd backend
    python tools/benchmark_rtree.py

Παράγει:
    - Πίνακα αποτελεσμάτων στο terminal
    - benchmark_results.csv για γράφημα στη διπλωματική
"""

import random
import time
import csv
from math import hypot
from rtree import index as rtree_index


# ── Minimal Screen / Zone stubs (χωρίς FastAPI dependencies) ────────────────

class FakeScreen:
    __slots__ = ("id", "zone_id", "row", "col", "screen_type")

    def __init__(self, screen_id, zone_id, row, col, screen_type="generic"):
        self.id = screen_id
        self.zone_id = zone_id
        self.row = row
        self.col = col
        self.screen_type = screen_type


# ── Δημιουργία synthetic screens ────────────────────────────────────────────

def generate_screens(n: int) -> list:
    """
    Παράγει n τυχαίες οθόνες σε grid space [0, 100) x [0, 100).
    """
    screens = []
    for i in range(n):
        row = random.uniform(0, 100)
        col = random.uniform(0, 100)
        screens.append(FakeScreen(f"S-{i}", "zone_a", row, col))
    return screens


# ── Linear O(n) query ────────────────────────────────────────────────────────

def build_linear(screens: list):
    return [(float(s.col), float(s.row), s) for s in screens]


def query_near_linear(coords, x, y, radius):
    return [s for sx, sy, s in coords if hypot(sx - x, sy - y) <= radius]


# ── R-Tree O(log n) query ────────────────────────────────────────────────────

def build_rtree(screens: list):
    prop = rtree_index.Property()
    prop.dimension = 2
    idx = rtree_index.Index(properties=prop)
    id_map = {}
    for i, s in enumerate(screens):
        x, y = float(s.col), float(s.row)
        idx.insert(i, (x, y, x, y))
        id_map[i] = (x, y, s)
    return idx, id_map


def query_near_rtree(idx, id_map, x, y, radius):
    bbox = (x - radius, y - radius, x + radius, y + radius)
    results = []
    for i in idx.intersection(bbox):
        sx, sy, s = id_map[i]
        if hypot(sx - x, sy - y) <= radius:
            results.append(s)
    return results


# ── Benchmark ────────────────────────────────────────────────────────────────

SIZES     = [28, 100, 1_000, 10_000, 100_000]
REPEATS   = 200     # επαναλήψεις ανά μέτρηση
QUERY_X   = 50.0
QUERY_Y   = 50.0
RADIUS    = 10.0


def run_benchmark():
    print(f"\n{'-'*65}")
    print(f"  {'N':>8}  {'Linear (ms)':>12}  {'R-Tree (ms)':>12}  {'Speedup':>9}")
    print(f"{'-'*65}")

    rows = []

    for n in SIZES:
        screens = generate_screens(n)

        # Χτίσε και τους δύο index
        coords = build_linear(screens)
        rtree_idx, id_map = build_rtree(screens)

        # ── Μέτρηση Linear ────────────────────────────────────────
        t0 = time.perf_counter()
        for _ in range(REPEATS):
            query_near_linear(coords, QUERY_X, QUERY_Y, RADIUS)
        t_linear = (time.perf_counter() - t0) / REPEATS * 1000  # ms/query

        # ── Μέτρηση R-Tree ────────────────────────────────────────
        t0 = time.perf_counter()
        for _ in range(REPEATS):
            query_near_rtree(rtree_idx, id_map, QUERY_X, QUERY_Y, RADIUS)
        t_rtree = (time.perf_counter() - t0) / REPEATS * 1000  # ms/query

        # Speedup (πόσες φορές πιο γρήγορο το R-Tree)
        speedup = t_linear / t_rtree if t_rtree > 0 else float("inf")

        note = " <- R-Tree overhead se mikro N" if n <= 100 else ""
        print(f"  {n:>8,}  {t_linear:>12.4f}  {t_rtree:>12.4f}  {speedup:>8.1f}x{note}")
        rows.append((n, round(t_linear, 6), round(t_rtree, 6), round(speedup, 2)))

    print(f"{'-'*65}")
    print(f"\n  Query: x={QUERY_X}, y={QUERY_Y}, radius={RADIUS}")
    print(f"  Average of {REPEATS} repetitions per measurement\n")

    # ── Εξαγωγή CSV ──────────────────────────────────────────────
    csv_path = "benchmark_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["N", "Linear_ms", "RTree_ms", "Speedup"])
        writer.writerows(rows)
    print(f"  Results saved to: {csv_path}\n")


if __name__ == "__main__":
    random.seed(42)
    run_benchmark()
