# backend/app/services/layout_service.py

from math import hypot
from rtree import index as rtree_index
from scipy.spatial import KDTree
from app.models.layout_models import Zone, Screen, MultiIndexKey


class LayoutService:
    """
    Κεντρική υπηρεσία που ξέρει τη διάταξη των οθονών στο γήπεδο.
    Προς το παρόν είναι static (in-memory), χωρίς βάση.
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
                        screen_type="glassfloor_tile",  # ΝΕΟ
                    )
                )

        zones.append(
            Zone(
                id="glassfloor",
                name="GlassFloor",
                description="Γυάλινο γήπεδο στο κέντρο",
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
                        screen_type="surrounding_banner",  # ΝΕΟ
                    )
                )

        zones.append(
            Zone(
                id="surrounding",
                name="Surrounding Screens",
                description="Περιμετρικές οθόνες γύρω από το γήπεδο",
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
                        screen_type="megatron_panel",  # ΝΕΟ
                    )
                )

        zones.append(
            Zone(
                id="megatron",
                name="Megatron Screens",
                description="Κεντρικές μεγάλες οθόνες (Megatron)",
                rows=2,
                cols=2,
                screens=mega_screens,
            )
        )

        return zones


# ------------------------------------------
#  ΠΟΛΥΔΙΑΣΤΑΤΟΣ INDEX (ένα μόνο αντίγραφο!)
# ------------------------------------------


class MultiDimScreenIndex:
    """
    Πιο έξυπνος index για screens.

    Κρατάει:
    - ανά ζώνη (zone_id)
    - ανά grid (zone_id, row, col)
    - 2D συντεταγμένες (x, y) για κοντινά queries

    Για αρχή όλα είναι in-memory (single process),
    ώστε αργότερα να το "σπάσουμε" σε distributed nodes.
    """

    def __init__(self, zones: list[Zone]):
        # 1) Αποθηκεύουμε τις ζώνες
        self._zones_by_id: dict[str, Zone] = {z.id: z for z in zones}

        # 2) Flat λίστα με όλα τα screens
        self._screens: list[Screen] = [s for z in zones for s in z.screens]

        # 3) Index ανά ζώνη
        self._screens_by_zone: dict[str, list[Screen]] = {}

        # 4) Index ανά grid (zone_id, row, col)
        self._screens_by_grid: dict[tuple[str, int, int], Screen] = {}

        # 5) Index για 2D κοντινά queries (x, y, screen)
        #    Προς το παρόν linear scan. Αργότερα μπαίνει R-Tree.
        self._coords: list[tuple[float, float, Screen]] = []

        for screen in self._screens:
            # Ανά ζώνη
            self._screens_by_zone.setdefault(screen.zone_id, []).append(screen)

            # Ανά grid
            grid_key = (screen.zone_id, screen.row, screen.col)
            self._screens_by_grid[grid_key] = screen

            # 2D θέση στο "grid space"
            # Για αρχή: x = col, y = row (απλό μοντέλο)
            x = float(screen.col)
            y = float(screen.row)
            self._coords.append((x, y, screen))

        # 6) R-Tree για O(log n) 2D range queries
        self._build_rtree()

        # 7) KD-Tree (scipy) — εναλλακτικό O(log n) spatial index
        self._build_kdtree()

        # 8) Grid Index — hash-based O(1) amortized lookup
        self._cell_size = 1.0
        self._build_grid_index()

    # -----------------------------
    #  R-TREE CONSTRUCTION
    # -----------------------------

    def _build_rtree(self) -> None:
        """
        Χτίζει R-Tree 2D index για O(log n) range queries.
        Κάθε screen εισάγεται ως point: bounding box (x, y, x, y).
        Το integer key i αντιστοιχεί στο _coords[i].
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
        Χτίζει KD-Tree (scipy) για O(log n) 2D range queries.
        Εναλλακτικό του R-Tree — διαφορετικός αλγόριθμος, ίδια complexity.
        Το KD-Tree κάνει binary space partitioning (ανά άξονα),
        ενώ το R-Tree χρησιμοποιεί ορθογώνια bounding boxes.
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
        query_ball_point() επιστρέφει ακριβώς τα indices εντός κύκλου ακτίνας radius.
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
        Χτίζει Hash-based Grid Index για O(1) amortized range queries.
        Ο χώρος χωρίζεται σε κελιά μεγέθους cell_size.
        Κάθε screen ανήκει σε ένα κελί (hash key = (cx, cy)).
        Για query: ελέγχει μόνο τα κελιά που τέμνονται με το bounding box.
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
        Υπολογίζει ποια κελιά τέμνονται με το bounding box (x±r, y±r),
        ελέγχει μόνο αυτά — χωρίς να σαρώσει όλο τον χώρο.
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
    #  ΑΠΛΑ QUERIES (όπως πριν)
    # -----------------------------

    def query_by_zone(self, zone_id: str) -> list[Screen]:
        """
        Επιστρέφει όλα τα screens για μια ζώνη.
        Πλήρως συμβατό με το παλιό NaiveScreenIndex.
        """
        return list(self._screens_by_zone.get(zone_id, []))

    def query_by_grid(self, zone_id: str, row: int, col: int) -> Screen | None:
        """
        Επιστρέφει ένα screen με βάση zone + row + col.
        """
        return self._screens_by_grid.get((zone_id, row, col))

    # -----------------------------
    #  ΠΟΛΥΔΙΑΣΤΑΤΑ QUERIES
    # -----------------------------

    def query_near_linear(
        self,
        x: float,
        y: float,
        radius: float,
        zone_id: str | None = None,
    ) -> list[Screen]:
        """
        O(n) γραμμική αναζήτηση — χρησιμοποιείται ΜΟΝΟ για benchmark σύγκριση.
        Ελέγχει κάθε screen ένα-ένα με hypot().
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

        Βήματα:
        1) Bounding box query στο R-Tree: (x-r, y-r, x+r, y+r)
           → επιστρέφει υποψηφίους γρήγορα
        2) Ακριβής κυκλικός έλεγχος με hypot() για όσους βρέθηκαν
           (το R-Tree επιστρέφει ορθογώνιο, όχι κύκλο)
        3) Προαιρετικό φίλτρο zone_id
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
        PostGIS ST_DWithin range query — πραγματικές γεωγραφικές συντεταγμένες.

        Διαφορά από query_near():
        - query_near()        : in-memory R-Tree, grid coords (row/col), απόσταση σε grid units
        - query_near_postgis(): PostGIS DB query, WGS-84 lat/lon, απόσταση σε ΜΕΤΡΑ

        Χρησιμοποιεί GIST index → O(log n) στη DB.
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
        """Χρήσιμο για debugging / testing."""
        return list(self._screens)

    def build_keys(
        self,
        ad_category: str | None = None,
        time_window: str | None = None,
    ) -> list[MultiIndexKey]:
        """
        Δημιουργεί μια λίστα από MultiIndexKey αντικείμενα
        για ΟΛΑ τα screens του γηπέδου.

        Προς το παρόν:
        - βάζουμε ίδια ad_category / time_window σε όλα,
          όπως τα δώσει το endpoint.
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
        Βρίσκει την "καλύτερη" οθόνη για μια διαφήμιση γύρω από ένα σημείο (x, y).

        Βήματα:
        1) Παίρνουμε όλα τα κοντινά screens (query_near)
        2) Αν έχει δοθεί screen_type, φιλτράρουμε
        3) Επιλέγουμε αυτό με τη μικρότερη απόσταση
        4) Γυρνάμε (MultiIndexKey, distance)

        Προς το παρόν η "ποιότητα" = μικρότερη γεωμετρική απόσταση.
        Αργότερα μπορεί να προσθέσω scoring (π.χ. Megatron > GlassFloor).
        """
        # 1) Κοντινά υποψήφια
        candidates = self.query_near(x=x, y=y, radius=radius, zone_id=zone_id)

        # 2) Φίλτρο screen_type (αν ζητηθεί)
        if screen_type is not None:
            candidates = [s for s in candidates if s.screen_type == screen_type]

        if not candidates:
            return None

        # 3) Βρες το πιο κοντινό
        def distance_to_screen(s: Screen) -> float:
            return hypot(float(s.col) - x, float(s.row) - y)

        best_screen = min(candidates, key=distance_to_screen)
        best_distance = distance_to_screen(best_screen)

        # 4) Φτιάξε το κλειδί
        key = MultiIndexKey.from_screen(
            best_screen,
            ad_category=ad_category,
            time_window=time_window,
        )

        return key, best_distance


# ──────────────────────────────────────────────────────────────────────────────
#  DISTRIBUTED INDEX SIMULATION  (Phase 3)
#
#  Αρχιτεκτονική:
#    3 IndexShard  — κάθε ένα κρατά ένα υποσύνολο screens + δικό του R-tree
#    DistributedScreenIndex (coordinator) — fan-out query παράλληλα σε όλα τα shards
#
#  MapReduce pattern:
#    Map    = κάθε shard.query_near() εκτελείται ανεξάρτητα (ThreadPoolExecutor)
#    Reduce = coordinator merge + sort by distance
#
#  Σε πραγματικό σύστημα οι IndexShard θα τρέχουν σε ξεχωριστά machines/processes
#  επικοινωνώντας μέσω gRPC ή HTTP. Εδώ προσομοιώνονται σε ένα process.
# ──────────────────────────────────────────────────────────────────────────────

class IndexShard:
    """
    Ένας κόμβος (node) του κατανεμημένου index.
    Κρατά ένα partition των screens και το δικό του R-tree.
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
        """O(log n) R-tree range query τοπικά στο shard."""
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
    Coordinator του κατανεμημένου index.

    Partitioning strategy: κάθε zone → ξεχωριστός IndexShard (node).
      Node A: GlassFloor  (16 screens)
      Node B: Surrounding ( 8 screens)
      Node C: Megatron    ( 4 screens)

    Fan-out: ThreadPoolExecutor(3) — όλα τα shards ερωτώνται ταυτόχρονα.
    Merge:   αποτελέσματα ταξινομούνται κατά απόσταση (Reduce step).
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

        Map step  : κάθε shard εκτελεί query_near() ανεξάρτητα (parallel threads).
        Reduce step: coordinator merge-άρει και ταξινομεί κατά απόσταση.

        Returns list of {"screen": Screen, "distance": float, "node": str}
        """
        from concurrent.futures import ThreadPoolExecutor

        def shard_query(shard: IndexShard):
            local_results = shard.query_near(x, y, radius, zone_id)
            return [
                (screen, hypot(float(screen.col) - x, float(screen.row) - y), shard.node_id)
                for screen in local_results
            ]

        # MAP: fan-out σε 3 threads ταυτόχρονα
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


# SINGLETON (ένα index για όλο το backend)
_INDEX: MultiDimScreenIndex | None = None


def get_screen_index() -> MultiDimScreenIndex:
    """
    Lazy δημιουργία του index.
    Καλείται από τα endpoints του main.py.
    """
    global _INDEX
    if _INDEX is None:
        zones = LayoutService.get_layout()
        _INDEX = MultiDimScreenIndex(zones)
    return _INDEX
