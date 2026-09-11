# backend/app/services/layout_service.py

from math import hypot
from rtree import index as rtree_index
from scipy.spatial import KDTree
from app.models.layout_models import Zone, Screen, MultiIndexKey


class LayoutService:
    """
    Knows the layout of the screens in the stadium.
    Static and in-memory for now; no database.
    """

    @staticmethod
    def get_layout() -> list[Zone]:
        zones: list[Zone] = []

        # 1️⃣ GlassFloor: 4x4
        gf_screens: list[Screen] = []
        for row in range(4):
            for col in range(4):
                gf_screens.append(
                    Screen(
                        id=f"GF-{row}-{col}",
                        zone_id="glassfloor",
                        row=row,
                        col=col,
                        screen_type="glassfloor_tile",
                    )
                )

        zones.append(
            Zone(
                id="glassfloor",
                name="GlassFloor",
                description="Glass floor in the centre",
                rows=4,
                cols=4,
                screens=gf_screens,
            )
        )

        # 2️⃣ Surrounding: 2x4
        sur_screens: list[Screen] = []
        for row in range(2):
            for col in range(4):
                sur_screens.append(
                    Screen(
                        id=f"SUR-{row}-{col}",
                        zone_id="surrounding",
                        row=row,
                        col=col,
                        screen_type="surrounding_banner",
                    )
                )

        zones.append(
            Zone(
                id="surrounding",
                name="Surrounding Screens",
                description="Perimeter screens around the pitch",
                rows=2,
                cols=4,
                screens=sur_screens,
            )
        )

        # 3️⃣ Megatron: 2x2
        mega_screens: list[Screen] = []
        for row in range(2):
            for col in range(2):
                mega_screens.append(
                    Screen(
                        id=f"MEGA-{row}-{col}",
                        zone_id="megatron",
                        row=row,
                        col=col,
                        screen_type="megatron_panel",
                    )
                )

        zones.append(
            Zone(
                id="megatron",
                name="Megatron Screens",
                description="Large central screens (Megatron)",
                rows=2,
                cols=2,
                screens=mega_screens,
            )
        )

        return zones


# ------------------------------------------
#  MULTI-DIMENSIONAL INDEX (a single copy)
# ------------------------------------------


class MultiDimScreenIndex:
    """
    The screen index.

    Keeps:
    - screens per zone (zone_id)
    - screens per grid cell (zone_id, row, col)
    - 2D coordinates (x, y) for proximity queries

    Everything is in-memory in a single process,
    so it can later be split into distributed nodes.
    """

    def __init__(self, zones: list[Zone]):
        # 1) Store the zones
        self._zones_by_id: dict[str, Zone] = {z.id: z for z in zones}

        # 2) Flat list of every screen
        self._screens: list[Screen] = [s for z in zones for s in z.screens]

        # 3) Index per zone
        self._screens_by_zone: dict[str, list[Screen]] = {}

        # 4) Index per grid cell (zone_id, row, col)
        self._screens_by_grid: dict[tuple[str, int, int], Screen] = {}

        # 5) Index for 2D proximity queries (x, y, screen)
        #    Linear scan here; the R-Tree below is the fast path.
        self._coords: list[tuple[float, float, Screen]] = []

        for screen in self._screens:
            # Per zone
            self._screens_by_zone.setdefault(screen.zone_id, []).append(screen)

            # Per grid cell
            grid_key = (screen.zone_id, screen.row, screen.col)
            self._screens_by_grid[grid_key] = screen

            # 2D position in grid space
            # Simple model: x = col, y = row
            x = float(screen.col)
            y = float(screen.row)
            self._coords.append((x, y, screen))

        # 6) R-Tree for O(log n) 2D range queries
        self._build_rtree()

        # 7) KD-Tree (scipy), an alternative O(log n) spatial index
        self._build_kdtree()

        # 8) Grid Index — hash-based O(1) amortized lookup
        self._cell_size = 1.0
        self._build_grid_index()

    # -----------------------------
    #  R-TREE CONSTRUCTION
    # -----------------------------

    def _build_rtree(self) -> None:
        """
        Build the 2D R-Tree index for O(log n) range queries.
        Each screen is inserted as a point: bounding box (x, y, x, y).
        The integer key i maps to _coords[i].
        """
        prop = rtree_index.Property()
        prop.dimension = 2
        self._rtree = rtree_index.Index(properties=prop)
        self._rtree_id_to_screen: dict[int, Screen] = {}
        for i, (x, y, screen) in enumerate(self._coords):
            self._rtree.insert(i, (x, y, x, y))
            self._rtree_id_to_screen[i] = screen

    # -----------------------------
    #  KD-TREE CONSTRUCTION
    # -----------------------------

    def _build_kdtree(self) -> None:
        """
        Build the scipy KD-Tree for O(log n) 2D range queries.
        An alternative to the R-Tree: different algorithm, same complexity.
        The KD-Tree partitions space by axis,
        while the R-Tree uses rectangular bounding boxes.
        """
        points = [(x, y) for x, y, _ in self._coords]
        self._kdtree = KDTree(points)
        self._kdtree_screens: list[Screen] = [s for _, _, s in self._coords]

    def query_near_kdtree(
        self,
        x: float,
        y: float,
        radius: float,
        zone_id: str | None = None,
    ) -> list[Screen]:
        """
        O(log n) KD-Tree range query (scipy).
        query_ball_point() returns exactly the indices inside the circle of the given radius.
        """
        indices = self._kdtree.query_ball_point([x, y], radius)
        results: list[Screen] = []
        for i in indices:
            screen = self._kdtree_screens[i]
            if zone_id is not None and screen.zone_id != zone_id:
                continue
            results.append(screen)
        return results

    # -----------------------------
    #  GRID INDEX CONSTRUCTION
    # -----------------------------

    def _build_grid_index(self) -> None:
        """
        Build the hash-based grid index for O(1) amortised range queries.
        Space is divided into cells of size cell_size.
        Each screen belongs to one cell (hash key = (cx, cy)).
        A query checks only the cells that intersect the bounding box.
        """
        self._grid: dict[tuple[int, int], list[tuple[float, float, Screen]]] = {}
        for x, y, screen in self._coords:
            cell = (int(x // self._cell_size), int(y // self._cell_size))
            self._grid.setdefault(cell, []).append((x, y, screen))

    def query_near_grid(
        self,
        x: float,
        y: float,
        radius: float,
        zone_id: str | None = None,
    ) -> list[Screen]:
        """
        O(1) amortized Grid Index range query.
        Work out which cells intersect the bounding box (x±r, y±r)
        and check only those, never the whole space.
        """
        min_cx = int((x - radius) // self._cell_size)
        max_cx = int((x + radius) // self._cell_size)
        min_cy = int((y - radius) // self._cell_size)
        max_cy = int((y + radius) // self._cell_size)

        results: list[Screen] = []
        seen: set[str] = set()
        for cx in range(min_cx, max_cx + 1):
            for cy in range(min_cy, max_cy + 1):
                for sx, sy, screen in self._grid.get((cx, cy), []):
                    if screen.id in seen:
                        continue
                    if zone_id is not None and screen.zone_id != zone_id:
                        continue
                    if hypot(sx - x, sy - y) <= radius:
                        seen.add(screen.id)
                        results.append(screen)
        return results

    # -----------------------------
    #  SIMPLE QUERIES
    # -----------------------------

    def query_by_zone(self, zone_id: str) -> list[Screen]:
        """
        Return every screen in a zone.
        Same contract as the earlier NaiveScreenIndex.
        """
        return list(self._screens_by_zone.get(zone_id, []))

    def query_by_grid(self, zone_id: str, row: int, col: int) -> Screen | None:
        """
        Return one screen by zone, row and column.
        """
        return self._screens_by_grid.get((zone_id, row, col))

    # -----------------------------
    #  MULTI-DIMENSIONAL QUERIES
    # -----------------------------

    def query_near_linear(
        self,
        x: float,
        y: float,
        radius: float,
        zone_id: str | None = None,
    ) -> list[Screen]:
        """
        O(n) linear scan, used only as the benchmark baseline.
        Checks every screen one by one with hypot().
        """
        results: list[Screen] = []
        for sx, sy, screen in self._coords:
            if zone_id is not None and screen.zone_id != zone_id:
                continue
            if hypot(sx - x, sy - y) <= radius:
                results.append(screen)
        return results

    def query_near(
        self,
        x: float,
        y: float,
        radius: float,
        zone_id: str | None = None,
    ) -> list[Screen]:
        """
        O(log n) R-Tree range query.

        Steps:
        1) Bounding-box query on the R-Tree: (x-r, y-r, x+r, y+r)
           returns candidates quickly
        2) Exact circular check with hypot() on the candidates
           (the R-Tree returns a rectangle, not a circle)
        3) Optional zone_id filter
        """
        bbox = (x - radius, y - radius, x + radius, y + radius)
        results: list[Screen] = []
        for i in self._rtree.intersection(bbox):
            screen = self._rtree_id_to_screen[i]
            if zone_id is not None and screen.zone_id != zone_id:
                continue
            sx, sy = float(screen.col), float(screen.row)
            if hypot(sx - x, sy - y) <= radius:
                results.append(screen)
        return results

    def query_near_postgis(
        self,
        lat: float,
        lon: float,
        radius_m: float,
        zone_id: str | None = None,
    ) -> list[Screen]:
        """
        PostGIS ST_DWithin range query on real geographic coordinates.

        Difference from query_near():
        - query_near()        : in-memory R-Tree, grid coordinates (row/col), distance in grid units
        - query_near_postgis(): PostGIS query, WGS-84 lat/lon, distance in metres

        Uses the GIST index, O(log n) inside the database.
        ST_MakePoint(lon, lat) — PostGIS convention: X=longitude, Y=latitude.

        Security: parameterized queries (no f-string SQL) + try/finally for connection cleanup.
        """
        from app.config import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()

        try:
            if zone_id:
                cur.execute("""
                    SELECT id, zone_id, row_idx, col_idx, screen_type
                    FROM screens
                    WHERE zone_id = %s
                      AND ST_DWithin(location, ST_MakePoint(%s, %s)::geography, %s)
                    ORDER BY ST_Distance(location, ST_MakePoint(%s, %s)::geography)
                """, (zone_id, lon, lat, radius_m, lon, lat))
            else:
                cur.execute("""
                    SELECT id, zone_id, row_idx, col_idx, screen_type
                    FROM screens
                    WHERE ST_DWithin(location, ST_MakePoint(%s, %s)::geography, %s)
                    ORDER BY ST_Distance(location, ST_MakePoint(%s, %s)::geography)
                """, (lon, lat, radius_m, lon, lat))

            rows = cur.fetchall()
        finally:
            cur.close()
            conn.close()

        return [
            Screen(id=r[0], zone_id=r[1], row=r[2], col=r[3], screen_type=r[4])
            for r in rows
        ]

    def get_all_screens(self) -> list[Screen]:
        """Handy for debugging and tests."""
        return list(self._screens)

    def build_keys(
        self,
        ad_category: str | None = None,
        time_window: str | None = None,
    ) -> list[MultiIndexKey]:
        """
        Build a list of MultiIndexKey objects
        for every screen in the stadium.

        For now:
        - the same ad_category / time_window is applied to all of them,
          as given by the endpoint.
        """
        return [
            MultiIndexKey.from_screen(
                screen,
                ad_category=ad_category,
                time_window=time_window,
            )
            for screen in self._screens
        ]


    def recommend_screen(
        self,
        x: float,
        y: float,
        radius: float = 10.0,
        zone_id: str | None = None,
        screen_type: str | None = None,
        ad_category: str | None = None,
        time_window: str | None = None,
    ) -> tuple[MultiIndexKey, float] | None:
        """
        Find the "best" screen for an advertisement around a point (x, y).

        Steps:
        1) Fetch the nearby screens (query_near)
        2) Filter by screen_type if one was given
        3) Pick the one with the smallest distance
        4) Return (MultiIndexKey, distance)

        "Best" currently means smallest geometric distance.
        A scoring model (e.g. Megatron over GlassFloor) could replace it later.
        """
        # 1) Nearby candidates
        candidates = self.query_near(x=x, y=y, radius=radius, zone_id=zone_id)

        # 2) screen_type filter, if requested
        if screen_type is not None:
            candidates = [s for s in candidates if s.screen_type == screen_type]

        if not candidates:
            return None

        # 3) Closest one wins
        def distance_to_screen(s: Screen) -> float:
            return hypot(float(s.col) - x, float(s.row) - y)

        best_screen = min(candidates, key=distance_to_screen)
        best_distance = distance_to_screen(best_screen)

        # 4) Build the key
        key = MultiIndexKey.from_screen(
            best_screen,
            ad_category=ad_category,
            time_window=time_window,
        )

        return key, best_distance


# ──────────────────────────────────────────────────────────────────────────────
#  DISTRIBUTED INDEX SIMULATION  (Phase 3)
#
#  Architecture:
#    3 IndexShard  - each holds a subset of the screens and its own R-tree
#    DistributedScreenIndex (coordinator) - fans a query out to every shard in parallel
#
#  MapReduce pattern:
#    Map    = each shard.query_near() runs independently (ThreadPoolExecutor)
#    Reduce = coordinator merge + sort by distance
#
#  In a real system the shards would run on separate machines or processes
#  talking over gRPC or HTTP. Here they are simulated inside one process.
# ──────────────────────────────────────────────────────────────────────────────

class IndexShard:
    """
    One node of the distributed index.
    Holds one partition of the screens and its own R-tree.
    """

    def __init__(self, node_id: str, screens: list[Screen]):
        self.node_id = node_id
        self._screens = screens
        self._coords: list[tuple[float, float, Screen]] = [
            (float(s.col), float(s.row), s) for s in screens
        ]
        self._build_rtree()

    def _build_rtree(self) -> None:
        prop = rtree_index.Property()
        prop.dimension = 2
        self._rtree = rtree_index.Index(properties=prop)
        self._id_map: dict[int, Screen] = {}
        for i, (x, y, screen) in enumerate(self._coords):
            self._rtree.insert(i, (x, y, x, y))
            self._id_map[i] = screen

    def query_near(
        self,
        x: float,
        y: float,
        radius: float,
        zone_id: str | None = None,
    ) -> list[Screen]:
        """O(log n) R-tree range query local to this shard."""
        bbox = (x - radius, y - radius, x + radius, y + radius)
        results: list[Screen] = []
        for i in self._rtree.intersection(bbox):
            screen = self._id_map[i]
            if zone_id is not None and screen.zone_id != zone_id:
                continue
            sx, sy = float(screen.col), float(screen.row)
            if hypot(sx - x, sy - y) <= radius:
                results.append(screen)
        return results


class DistributedScreenIndex:
    """
    Coordinator of the distributed index.

    Partitioning: one IndexShard (node) per zone.
      Node A: GlassFloor  (16 screens)
      Node B: Surrounding ( 8 screens)
      Node C: Megatron    ( 4 screens)

    Fan-out: ThreadPoolExecutor(3), every shard is queried at the same time.
    Merge:   results are sorted by distance (the Reduce step).
    """

    def __init__(self, zones: list[Zone]):
        screens_by_zone: dict[str, list[Screen]] = {}
        for zone in zones:
            screens_by_zone[zone.id] = list(zone.screens)

        self._shards: list[IndexShard] = [
            IndexShard("node_glassfloor",  screens_by_zone.get("glassfloor",  [])),
            IndexShard("node_surrounding", screens_by_zone.get("surrounding", [])),
            IndexShard("node_megatron",    screens_by_zone.get("megatron",    [])),
        ]

    def query_near(
        self,
        x: float,
        y: float,
        radius: float,
        zone_id: str | None = None,
    ) -> list[dict]:
        """
        Distributed fan-out query.

        Map step  : each shard runs query_near() independently (parallel threads).
        Reduce step: the coordinator merges and sorts by distance.

        Returns list of {"screen": Screen, "distance": float, "node": str}
        """
        from concurrent.futures import ThreadPoolExecutor

        def shard_query(shard: IndexShard):
            local_results = shard.query_near(x, y, radius, zone_id)
            return [
                (screen, hypot(float(screen.col) - x, float(screen.row) - y), shard.node_id)
                for screen in local_results
            ]

        # MAP: fan out to 3 threads at once
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(shard_query, shard) for shard in self._shards]
            partial = [f.result() for f in futures]

        # REDUCE: flatten + sort by distance
        merged = [item for chunk in partial for item in chunk]
        merged.sort(key=lambda t: t[1])

        return [
            {"screen": t[0], "distance": round(t[1], 4), "node": t[2]}
            for t in merged
        ]


# SINGLETON (one index for the whole backend)
_INDEX: MultiDimScreenIndex | None = None


def get_screen_index() -> MultiDimScreenIndex:
    """
    Create the index lazily.
    Called from the endpoints in main.py.
    """
    global _INDEX
    if _INDEX is None:
        zones = LayoutService.get_layout()
        _INDEX = MultiDimScreenIndex(zones)
    return _INDEX
