# THESIS AI PROMPT — GEO-ADS Διπλωματική Εργασία
# Χρησιμοποίησε αυτό το αρχείο ως context σε ChatGPT ή οποιοδήποτε AI

---

## ΤΑΥΤΟΤΗΤΑ ΕΡΓΑΣΙΑΣ

**Τίτλος:** Σύστημα Διαχείρισης Γεω-Στοχευμένων Διαφημίσεων Αθλητικών Εγκαταστάσεων σε Πραγματικό Χρόνο

**Φοιτητής:** Μιχάλης Δέμης, ΑΜ 1080958

**Ίδρυμα:** Πανεπιστήμιο Πατρών, Τμήμα Μηχανικών Η/Υ & Πληροφορικής

**Επιβλέπων:** (συμπλήρωσε)

**Ακαδημαϊκό Έτος:** 2024–2025

---

## ΤΙ ΕΙΝΑΙ ΤΟ ΣΥΣΤΗΜΑ (GEO-ADS)

Το GEO-ADS είναι ένα real-time σύστημα διαχείρισης και προβολής στοχευμένων διαφημίσεων σε αθλητικές εγκαταστάσεις. Το σύστημα επιτρέπει την ανάθεση διαφημίσεων σε οθόνες γηπέδου με βάση τη γεωγραφική θέση του θεατή, σε πραγματικό χρόνο, με πλήρες επίπεδο ασφάλειας.

### Αρχιτεκτονική

| Στρώμα | Τεχνολογία | Σκοπός |
|--------|-----------|--------|
| Backend | FastAPI (Python) | REST API + WebSocket server |
| Database | PostgreSQL 16 + PostGIS | Αποθήκευση διαφημίσεων, χωρικά ευρετήρια |
| Frontend | React 18 | Stadium Board UI + Security Dashboard |
| Desktop | Electron | All-in-one εφαρμογή (backend + UI) |
| Real-time | WebSockets (native FastAPI) | Live updates διαφημίσεων και alerts |
| Security | JWT + HMAC + Anti-Replay + Rate Limiting + Audit Log + Threat Engine | 6 επίπεδα ασφάλειας |

### Ζώνες Γηπέδου (3 ζώνες, 28 οθόνες συνολικά)

| Ζώνη | Grid | Οθόνες | Τύπος |
|------|------|--------|-------|
| GlassFloor | 4×4 | 16 tiles | glassfloor_tile |
| Surrounding Screens | 2×4 | 8 banners | surrounding_banner |
| Megatron | 2×2 | 4 panels | megatron_panel |

---

## ΕΡΕΥΝΗΤΙΚΕΣ ΕΡΩΤΗΣΕΙΣ (ΕΡ-1 έως ΕΡ-9)

Η διπλωματική απαντά στις εξής 9 ερευνητικές ερωτήσεις:

| Κωδικός | Ερευνητική Ερώτηση | Πού απαντάται |
|---------|-------------------|---------------|
| ΕΡ-1 | Πώς οργανώνονται οι ζώνες οθονών σε ένα γήπεδο; | Αρχιτεκτονική ζωνών |
| ΕΡ-2 | Ποια μέθοδος πολυδιάστατης ευρετηρίασης είναι πιο αποδοτική για χωρικές ερωτήσεις; | Πειράματα κεφ. 6 |
| ΕΡ-3 | Πώς υλοποιείται ένα recommendation engine για ανάθεση διαφημίσεων; | Layout service |
| ΕΡ-4 | Πώς επιτυγχάνεται real-time επικοινωνία μεταξύ server και clients; | WebSocket architecture |
| ΕΡ-5 | Πώς προστατεύονται τα HTTP και WebSocket endpoints με JWT; | Security layer |
| ΕΡ-6 | Πώς ενσωματώνονται εικόνες διαφημίσεων στις οθόνες; | Static files + DB |
| ΕΡ-7 | Γιατί PostgreSQL για real-time γεω-στοχευμένο σύστημα; | DB design |
| ΕΡ-8 | Πώς συσκευάζεται το σύστημα ως desktop εφαρμογή; | Electron |
| ΕΡ-9 | Πώς ανιχνεύονται απειλές σε πραγματικό χρόνο; | Threat Engine |

---

## ΚΥΡΙΑ ΕΡΕΥΝΗΤΙΚΑ ΕΥΡΗΜΑΤΑ

### Εύρημα 1: Σύγκριση Μεθόδων Χωρικής Ευρετηρίασης

Υλοποιήθηκαν και μετρήθηκαν 4 στρατηγικές για spatial range queries ("βρες οθόνες εντός ακτίνας r από σημείο x,y"):

**Αλγοριθμική Πολυπλοκότητα:**
- Linear Scan: O(n) — πάντα σαρώνει όλες τις οθόνες
- R-Tree: O(log n + k) — ιεραρχικό ευρετήριο bounding boxes
- PostGIS GIST: O(log n) — μόνιμο ευρετήριο στη DB, σφαιρικές αποστάσεις
- Distributed: O(log n/k) × k shards — παράλληλη εκτέλεση σε 3 shards

**Πειραματικά Αποτελέσματα (benchmark_all_results.csv):**

| N screens | Linear (ms) | R-Tree (ms) | Distributed (ms) | Speedup R-Tree | Speedup Dist |
|-----------|------------|-------------|-----------------|---------------|-------------|
| 28 | 0.004 | 0.008 | 0.444 | 0.54x | 0.01x |
| 100 | 0.018 | 0.012 | 0.435 | 1.45x | 0.04x |
| 1,000 | 0.148 | 0.035 | 0.455 | 4.25x | 0.32x |
| 10,000 | 1.475 | 0.200 | 0.616 | 7.36x | 2.4x |
| 100,000 | 14.551 | 1.799 | 2.414 | 8.09x | 6.03x |

**Βασικά συμπεράσματα:**
- Για n=28 (πραγματικό γήπεδο): Linear κερδίζει λόγω απουσίας overhead
- Για n>100: R-Tree ξεπερνά το Linear
- Για n>10,000: Distributed αρχίζει να αποδίδει αλλά R-Tree παραμένει ταχύτερο
- Distributed έχει σταθερό overhead ~0.44ms από thread spawning (δεν αξίζει για n<10,000)
- Επιλογή production: R-Tree (επεκτάσιμο, αμελητέα διαφορά για n=28)

### Εύρημα 2: Σύγκριση Rule-based vs Statistical Threat Detection

Υλοποιήθηκε υβριδικό σύστημα ανίχνευσης απειλών που τρέχει παράλληλα δύο detectors:

**Rule-based Detector:**
- Έλεγχος αριθμού events ανά IP σε χρονικό παράθυρο
- brute_force: 5+ auth_failed / 5 λεπτά → CRITICAL alert
- credential_stuffing: 10+ μοναδικά usernames / 10 λεπτά → CRITICAL
- replay_attack: 3+ replays / 5 λεπτά → CRITICAL
- rate_abuse: 20+ rate-limited / 10 λεπτά → WARNING

**Statistical Detector (Z-score):**
- Παρακολουθεί rate events σε windows 5min / 15min / 1h
- Alert όταν current_rate > mean + 2×std_dev
- Χρειάζεται ≥3 historical data points για baseline

**Τυπικά αποτελέσματα από test_threat_detection.py:**
- Rule avg detection time: ~0.014 ms
- Statistical avg detection time: ~0.013 ms
- Για brute force simulation (6 failed logins): Rule detector ανιχνεύει πρώτος
- Statistical detector ανιχνεύει ανωμαλίες που δεν καλύπτουν οι κανόνες (anomaly)
- "Both detected": ο αριθμός events που ανιχνεύτηκαν και από τους δύο detectors
- Συμπέρασμα: Υβριδική προσέγγιση καλύπτει περισσότερες περιπτώσεις από κάθε μέθοδο μόνη της

---

## ΕΠΙΠΕΔΑ ΑΣΦΑΛΕΙΑΣ (6 επίπεδα)

| Επίπεδο | Μηχανισμός | Λεπτομέρεια |
|---------|-----------|-------------|
| v1 | JWT Bearer Tokens | HS256, scoped (ads:read, placements:write, security:read κλπ), 1h TTL |
| v2 | HMAC-SHA256 | Υπογραφή WS μηνυμάτων node-to-node, SHA-256 / SHA3-256 |
| v3 | Anti-Replay | Timestamp window 60s + nonce deduplication |
| v4 | Rate Limiting | slowapi: 10/min login, 5/min token, 10/min refresh |
| v5 | Audit Logging | JSON middleware → audit.log (method, path, user, status, ms) |
| v6 | Threat Detection | ThreatEngine: Rule-based + Z-score Statistical, real-time WS alerts |

---

## ΤΕΧΝΟΛΟΓΙΕΣ ΠΟΥ ΧΡΗΣΙΜΟΠΟΙΗΘΗΚΑΝ

### Backend
- **FastAPI** (Python 3.11+): async REST + WebSocket
- **PostgreSQL 16**: κύρια βάση δεδομένων
- **PostGIS**: γεωγραφική επέκταση για spatial queries
- **python-jose**: JWT generation/verification
- **slowapi**: rate limiting
- **uvicorn**: ASGI server
- **rtree** (libspatialindex): in-memory R-Tree index
- **psycopg2**: PostgreSQL driver

### Frontend
- **React 18**: SPA framework
- **WebSocket API**: native browser WebSockets
- **CSS Grid/Flexbox**: layout

### Desktop
- **Electron**: packaging της React app + backend σε desktop εφαρμογή
- **cross-env**: cross-platform environment variables

### Database Schema (κύριοι πίνακες)
- `advertisements(id, name, image_url, zone, created_at)`
- `zones(id, name, type)`
- `screens(id, zone_id, row_idx, col_idx, screen_type, location GEOGRAPHY)`
- Placements: in-memory (χάνονται στο restart — γνωστό limitation)

---

## ΔΟΜΗ ΔΙΠΛΩΜΑΤΙΚΗΣ (συμφωνημένη)

```
Προκαταρκτικά: Εξώφυλλο, Περίληψη (ΕΛ+EN), Ευχαριστίες, ΠΠ, Ευρετήριο Εικόνων

Κεφ. 1: Εισαγωγή (~8-10 σελ.)
  1.1 Κίνητρο & Πρόβλημα
  1.2 Στόχοι Διπλωματικής
  1.3 Ερευνητικές Ερωτήσεις (ΕΡ-1 έως ΕΡ-9)
  1.4 Συνεισφορά Εργασίας
  1.5 Δομή Εργασίας

Κεφ. 2: Βιβλιογραφική Ανασκόπηση (~10-12 σελ.)
  2.1 Ψηφιακή Διαφήμιση & Real-time Συστήματα
  2.2 Χωρικά Ευρετήρια (R-Tree, PostGIS)
  2.3 WebSocket & Real-time Αρχιτεκτονικές
  2.4 Ασφάλεια Web Εφαρμογών (JWT, HMAC)
  2.5 Ανίχνευση Ανωμαλιών (Anomaly Detection)

Κεφ. 3: Θεωρητικό Πλαίσιο (~12-15 σελ.)
  3.1 Χωρικά Ευρετήρια: Linear, R-Tree, PostGIS GIST, Distributed
  3.2 Ανάλυση Πολυπλοκότητας (O notation)
  3.3 WebSocket Protocol
  3.4 JWT & HMAC — θεωρητικό υπόβαθρο
  3.5 Rule-based vs Statistical Anomaly Detection (Z-score)

Κεφ. 4: Σχεδιασμός Συστήματος (~10-12 σελ.)
  4.1 Αρχιτεκτονική Συστήματος (διάγραμμα)
  4.2 Ζώνες Γηπέδου & Μοντέλο Οθονών
  4.3 Σχεδιασμός Βάσης Δεδομένων
  4.4 Σχεδιασμός Real-time Επικοινωνίας
  4.5 Σχεδιασμός Ασφάλειας (6 επίπεδα)

Κεφ. 5: Υλοποίηση Συστήματος (~15-20 σελ.)
  5.1 Εργαλεία & Τεχνολογίες
  5.2 Backend: REST API & WebSocket Handlers
  5.3 Spatial Indexing: Υλοποίηση 4 μεθόδων
  5.4 Recommendation Engine
  5.5 Frontend: VisualBoard & SecurityDashboard
  5.6 Desktop Εφαρμογή (Electron)
  5.7 Σύστημα Ασφάλειας: Threat Engine

Κεφ. 6: Πειράματα & Αξιολόγηση (~15-18 σελ.)
  6.1 Μεθοδολογία Αξιολόγησης
  6.2 Πείραμα 1 — Χωρική Ευρετηρίαση
    6.2.1 Στόχος & Υπόθεση
    6.2.2 Μεθοδολογία (benchmark script)
    6.2.3 Αποτελέσματα (πίνακες + γραφήματα)
    6.2.4 Ανάλυση & Συμπεράσματα
  6.3 Πείραμα 2 — Ανίχνευση Απειλών
    6.3.1 Στόχος & Υπόθεση
    6.3.2 Μεθοδολογία (test_threat_detection.py)
    6.3.3 Αποτελέσματα (rule vs statistical)
    6.3.4 Ανάλυση & Συμπεράσματα
  6.4 Συζήτηση Αποτελεσμάτων

Κεφ. 7: Συμπεράσματα & Μελλοντικές Προεκτάσεις (~6-8 σελ.)
  7.1 Ανακεφαλαίωση
  7.2 Απαντήσεις στις Ερευνητικές Ερωτήσεις (ΕΡ-1 έως ΕΡ-9)
  7.3 Συνεισφορά στη Βιβλιογραφία
  7.4 Limitations (placements in-memory, μικρό dataset)
  7.5 Μελλοντικές Προεκτάσεις

Κεφ. 8: Βιβλιογραφία
```

**Εκτιμώμενες σελίδες: ~84–104**

---

## ΟΔΗΓΙΕΣ ΓΙΑ ΤΟ AI ΠΟΥ ΘΑ ΒΟΗΘΗΣΕΙ

Όταν ζητάς βοήθεια από AI για τη διπλωματική, χρησιμοποίησε αυτές τις οδηγίες:

### Γλώσσα & Ύφος
- Γράψε στα **Ελληνικά**, ακαδημαϊκό ύφος
- Χρησιμοποίησε τρίτο πρόσωπο ("αναπτύχθηκε", "υλοποιήθηκε", "παρατηρείται")
- Αποφύγε πρώτο πρόσωπο εκτός από Ευχαριστίες
- Κάθε ισχυρισμός πρέπει να συνοδεύεται από αναφορά ή αποτέλεσμα

### Για κάθε κεφάλαιο ζήτα
- "Γράψε το Κεφ. Χ.Χ [τίτλος] χρησιμοποιώντας τα δεδομένα από το context"
- "Πρόσθεσε αναφορές για [τεχνολογία] από βιβλιογραφία"
- "Δημιούργησε λεζάντα για εικόνα που δείχνει [περιγραφή]"

### Ό,τι ΔΕΝ πρέπει να αλλάξει
- Τα αριθμητικά αποτελέσματα (benchmark CSV) — χρησιμοποίησε ακριβώς αυτά
- Τα ονόματα τεχνολογιών
- Τις ερευνητικές ερωτήσεις ΕΡ-1 έως ΕΡ-9

### Πώς να αναφέρεσαι στον κώδικα
- Μη βάζεις μεγάλα κομμάτια κώδικα — μόνο αποσπάσματα (5-10 γραμμές) για απεικόνιση έννοιας
- Προτίμησε pseudocode ή διαγράμματα από πλήρη implementation

---

## ΓΝΩΣΤΑ LIMITATIONS (ειλικρίνεια στη διπλωματική)

- Τα placements αποθηκεύονται **in-memory** — χάνονται στο restart (μελλοντική εργασία: persistence στη DB)
- Το benchmark έγινε σε **τοπικό μηχάνημα** Windows, όχι σε production server
- Το dataset γηπέδου είναι **μικρό (n=28)** — τα αποτελέσματα για μεγάλο n είναι προσομοίωση
- Ο Statistical detector χρειάζεται **warm-up period** (≥3 data points) πριν αρχίσει να ανιχνεύει
- Δεν υπάρχει **real GPS data** — οι συντεταγμένες είναι προσομοιωμένες για το γήπεδο

---

## ΠΑΡΑΔΕΙΓΜΑ PROMPT ΓΙΑ ΕΝΑΡΞΗ

Αντέγραψε αυτό στο ChatGPT/Claude/άλλο AI:

```
Είμαι φοιτητής στο Πανεπιστήμιο Πατρών (ΤΗΜΜΥ) και γράφω τη διπλωματική μου
με τίτλο "Σύστημα Διαχείρισης Γεω-Στοχευμένων Διαφημίσεων Αθλητικών
Εγκαταστάσεων σε Πραγματικό Χρόνο" (GEO-ADS).

Επισυνάπτω το πλήρες context της εργασίας μου (thesis_ai_prompt.md).
Θέλω να γράψεις [ΤΙ ΘΕΛΕΙΣ] σύμφωνα με τη δομή που έχω ορίσει.
Γράψε στα Ελληνικά, ακαδημαϊκό ύφος, τρίτο πρόσωπο.
[ΠΡΟΣΘΕΣΕ ΟΠΟΙΕΣ ΕΠΙΠΛΕΟΝ ΟΔΗΓΙΕΣ ΘΕΛΕΙΣ]
```
