# Ανάλυση Πολυπλοκότητας — Χωρικά Ευρετήρια GEO-ADS

## 1. Εισαγωγή

Το σύστημα GEO-ADS υλοποιεί τρεις (3) διακριτές στρατηγικές για χωρικά range queries
τύπου "βρες όλες τις οθόνες εντός ακτίνας r από σημείο (x, y)":

| Στρατηγική | Υλοποίηση | Αρχείο |
|------------|-----------|--------|
| **Linear Scan** | O(n) γραμμική σάρωση | `MultiDimScreenIndex.query_near_linear()` |
| **R-Tree** | O(log n) in-memory | `MultiDimScreenIndex.query_near()` |
| **PostGIS GIST** | O(log n) στη DB | `MultiDimScreenIndex.query_near_postgis()` |
| **Distributed** | O(log n/k) × k nodes | `DistributedScreenIndex.query_near()` |

---

## 2. Linear Scan — O(n)

### Αλγόριθμος
```python
for (sx, sy, screen) in all_coords:          # n επαναλήψεις
    if hypot(sx - x, sy - y) <= radius:       # O(1) υπολογισμός
        results.append(screen)
```

### Πολυπλοκότητα
| | Worst Case | Average Case | Best Case |
|-|-----------|--------------|-----------|
| **Χρόνος** | O(n) | O(n) | O(n) |
| **Χώρος** | O(k) | O(k) | O(1) |

- **n** = αριθμός screens, **k** = αριθμός αποτελεσμάτων
- Η χρονική πολυπλοκότητα είναι **πάντα O(n)** ανεξαρτήτως αποτελεσμάτων
- Κατάλληλο για n ≤ 100 (overhead εξοικονομείται)

### Benchmark (n=28, το γήπεδό μας)
```
Linear scan:  0.004 ms/query
R-Tree:       0.008 ms/query  ← πιο αργό! (index overhead)
```
**Συμπέρασμα:** Για μικρό n, η γραμμική σάρωση κερδίζει λόγω απουσίας overhead.

---

## 3. R-Tree Index — O(log n)

### Δομή
Το R-Tree (Rectangle Tree, Guttman 1984) οργανώνει τα σημεία σε ιεραρχικά
ορθογώνια bounding boxes (MBR — Minimum Bounding Rectangle).

```
Root
├── MBR(GF zone):  [0,0] → [3,3]
│   ├── MBR(row 0-1): [0,0] → [3,1]
│   │   ├── GF-0-0 (0,0)
│   │   └── GF-0-1 (1,0) ...
│   └── MBR(row 2-3): [0,2] → [3,3]
└── MBR(SUR zone): [0,0] → [3,1]
    └── ...
```

### Αλγόριθμος Query
```
1. Bounding box query: intersection(x-r, y-r, x+r, y+r)  → O(log n + k)
2. Circular refinement: hypot() για κάθε candidate         → O(k)
Total: O(log n + k)
```

### Αλγόριθμος Construction
```
Για κάθε screen: rtree.insert(i, (x, y, x, y))  → O(log n) ανά εισαγωγή
Total build: O(n log n)
```

### Πολυπλοκότητα
| | Worst Case | Average Case |
|-|-----------|--------------|
| **Construction** | O(n log n) | O(n log n) |
| **Query** | O(n) | **O(log n + k)** |
| **Χώρος** | O(n) | O(n) |

- Worst case query = O(n) όταν η bounding box καλύπτει όλα τα MBR
- Average case = O(log n + k) για τυπικές spatial queries
- **k** = αριθμός αποτελεσμάτων

### Benchmark αποτελέσματα

| N screens | Linear (ms) | R-Tree (ms) | Speedup |
|-----------|-------------|-------------|---------|
| 28        | 0.004       | 0.008       | 0.6x    |
| 100       | 0.015       | 0.012       | 1.2x    |
| 1,000     | 0.147       | 0.034       | 4.3x    |
| 10,000    | 1.521       | 0.202       | 7.5x    |
| 100,000   | 14.697      | 1.742       | 8.4x    |

**Σχόλιο:** Για n = 28 (πραγματικό γήπεδο), η διαφορά είναι αμελητέα.
Η αξία του R-Tree φαίνεται καθαρά σε n > 1,000 (επεκτασιμότητα).

---

## 4. PostGIS GIST Index — O(log n) στη DB

### Δομή
Το GIST (Generalized Search Tree) της PostgreSQL επεκτείνει το R-Tree για
γεωγραφικούς τύπους (GEOGRAPHY). Αποθηκεύεται **μόνιμα στο δίσκο** και
χρησιμοποιεί σφαιρικό μοντέλο Γης (WGS-84).

```sql
CREATE INDEX idx_screens_location ON screens USING GIST(location);
```

### Αλγόριθμος Query
```sql
SELECT id, zone_id, row_idx, col_idx, screen_type
FROM screens
WHERE ST_DWithin(location, ST_MakePoint(lon, lat)::geography, radius_m)
ORDER BY ST_Distance(location, ST_MakePoint(lon, lat)::geography);
```

Εσωτερικά: GIST traversal → O(log n) + network/disk I/O overhead.

### Πολυπλοκότητα
| | |
|-|-|
| **Query** | O(log n) + I/O overhead |
| **Απόσταση** | Σφαιρική (μέτρα, ακριβής) |
| **Index** | Μόνιμος στο δίσκο |
| **Χώρος** | O(n) επιπλέον στο δίσκο |

### Διαφορά από R-Tree
| | R-Tree (in-memory) | PostGIS GIST |
|-|--------------------|--------------|
| Αποθήκευση | RAM | Δίσκος |
| Απόσταση | Euclidean (grid units) | Σφαιρική (μέτρα) |
| Επιβίωση μετά restart | ΟΧΙ | ΝΑΙ |
| Overhead | Μηδαμινό | Δίκτυο + DB |
| Κατάλληλο για | Real-time queries | GIS applications |

---

## 5. Distributed Index — Parallel O(log n/k)

### Αρχιτεκτονική
Τα n screens μοιράζονται σε **k = 3 shards** (partition by zone):

```
Shard A: GlassFloor  — n_A = 16 screens  (57%)
Shard B: Surrounding — n_B =  8 screens  (29%)
Shard C: Megatron    — n_C =  4 screens  (14%)
```

### MapReduce Pattern
```
Map step   (parallel):  shard_i.query_near(x, y, r) για i = 1..k  → O(log n_i) ανά shard
Reduce step (serial):   merge + sort αποτελεσμάτων                 → O(k * k_i * log(k * k_i))
```
όπου k_i = αριθμός αποτελεσμάτων ανά shard.

### Πολυπλοκότητα
| | Single-node | Distributed (k nodes) |
|-|-------------|----------------------|
| **Query** | O(log n) | **O(log n/k) + O(k·k_i·log...)** |
| **Parallelism** | 1 thread | k threads |
| **Construction** | O(n log n) | O((n/k) log(n/k)) × k |

- Θεωρητικά: k-πλάσια επιτάχυνση για μεγάλα n
- Πρακτικά: thread overhead μειώνει το gain για μικρό n (n=28)
- **Αξία:** scalability όταν n >> 28 και k >> 3

### Πότε αξίζει
```
k nodes, n screens ανά node:
  Αν n > 10,000 ΚΑΙ k > 10  →  σημαντική επιτάχυνση
  Αν n = 28    ΚΑΙ k = 3   →  overhead > gain (το δικό μας σύστημα)
```

---

## 6. Σύγκριση Όλων των Προσεγγίσεων

| Κριτήριο | Linear | R-Tree | PostGIS | Distributed |
|----------|--------|--------|---------|-------------|
| Query complexity | O(n) | O(log n) | O(log n) | O(log n/k) |
| Build complexity | O(n) | O(n log n) | O(n log n) | O(n log n) |
| Memory (RAM) | O(n) | O(n) | O(1) | O(n) |
| Disk | — | — | O(n) | — |
| Μέτρα (real) | ΟΧΙ | ΟΧΙ | ΝΑΙ | ΟΧΙ |
| Persistence | ΟΧΙ | ΟΧΙ | ΝΑΙ | ΟΧΙ |
| Parallelism | ΟΧΙ | ΟΧΙ | ΟΧΙ | ΝΑΙ |
| Κατάλληλο για | n < 100 | n < 1M | GIS apps | n > 10K, k > 10 |

---

## 7. Επιλογή Αλγορίθμου ανά Σενάριο

### Σενάριο 1: Μικρό γήπεδο (28 screens, production)
→ **R-Tree** — αμελητέα διαφορά από Linear, αλλά επεκτάσιμο

### Σενάριο 2: Εφαρμογή GIS (πολλαπλά γήπεδα με GPS)
→ **PostGIS** — αποστάσεις σε μέτρα, μόνιμα αποθηκευμένο index

### Σενάριο 3: Δίκτυο 1000 γηπέδων × 1000 screens
→ **Distributed** — k nodes × R-Tree ανά node, parallel fan-out

### Σενάριο 4: Rapid prototyping / debugging
→ **Linear** — μηδαμινό setup, εύκολη επαλήθευση

---

## 8. Βιβλιογραφία

- Guttman, A. (1984). *R-Trees: A Dynamic Index Structure for Spatial Searching*. ACM SIGMOD.
- Sellis, T., Roussopoulos, N., Faloutsos, C. (1987). *The R+-Tree: A Dynamic Index for Multi-Dimensional Objects*. VLDB.
- PostGIS Documentation: https://postgis.net/docs/ST_DWithin.html
- Γκαγκάκης, Σ. (2024). *Πολυδιάστατες Δομές Δεδομένων* — Σημειώσεις μαθήματος, Πανεπιστήμιο Πατρών.
