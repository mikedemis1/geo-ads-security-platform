# ΠΛΗΡΕΙΣ ΟΔΗΓΙΕΣ ΣΥΓΓΡΑΦΗΣ ΔΙΠΛΩΜΑΤΙΚΗΣ — GEO-ADS
# Επικόλλησε ΟΛΟ αυτό το αρχείο στο ChatGPT πριν ζητήσεις οτιδήποτε.

---

## ΜΕΡΟΣ Α — ΤΑΥΤΟΤΗΤΑ ΕΡΓΑΣΙΑΣ

**Τίτλος:** Σύστημα Διαχείρισης Γεω-Στοχευμένων Διαφημίσεων Αθλητικών Εγκαταστάσεων σε Πραγματικό Χρόνο

**Αγγλικός Τίτλος:** Real-Time Geo-Targeted Advertising Management System for Sports Facilities

**Φοιτητής:** Μιχάλης Δέμης, ΑΜ 1080958

**Ίδρυμα:** Πανεπιστήμιο Πατρών, Πολυτεχνική Σχολή, Τμήμα Μηχανικών Η/Υ & Πληροφορικής

**Ακαδημαϊκό Έτος:** 2024–2025

---

## ΜΕΡΟΣ Β — ΓΕΝΙΚΕΣ ΟΔΗΓΙΕΣ ΣΥΓΓΡΑΦΗΣ

### 1. Σχήματα, Πίνακες, Διαγράμματα

- Όλα τα σχήματα/πίνακες/διαγράμματα πρέπει να είναι **ευδιάκριτα και υψηλής ποιότητας**, να συνοδεύονται από **λεζάντα**, και να **αναφέρονται τουλάχιστον μία φορά μέσα στο κείμενο**.
- Λεζάντες εικόνων: "Εικόνα X: [Περιγραφή]"
- Λεζάντες πινάκων: "Πίνακας X: [Περιγραφή]"

### 2. Στόχος έκτασης (~25.000–30.000 λέξεις, 100–120 σελίδες)

Ενδεικτική κατανομή λέξεων ανά κεφάλαιο:

| Κεφάλαιο | Τίτλος | Λέξεις |
|----------|--------|--------|
| Περίληψη + Abstract | — | 400–600 |
| Κεφ. 1 | Εισαγωγή | 2.000–2.500 |
| Κεφ. 2 | Βιβλιογραφική Ανασκόπηση | 4.500–5.500 |
| Κεφ. 3 | Θεωρητικό Πλαίσιο | 5.000–6.000 |
| Κεφ. 4 | Σχεδιασμός Συστήματος | 3.000–4.000 |
| Κεφ. 5 | Υλοποίηση Συστήματος | 4.500–5.500 |
| Κεφ. 6 | Πειράματα & Αξιολόγηση | 4.000–5.000 |
| Κεφ. 7 | Συμπεράσματα & Μελλοντικές Προεκτάσεις | 1.500–2.000 |
| **Σύνολο** | | **~25.000–31.000** |

### 3. Δομή & Συνοχή

- Σαφής αρίθμηση ενοτήτων (1.1, 1.2, 2.1.1 κλπ.)
- Κάθε κεφάλαιο **ανοίγει** με σύντομη εισαγωγή τι θα καλυφθεί
- Κάθε κεφάλαιο **κλείνει** με σύνοψη βασικών σημείων
- Σαφής μετάβαση μεταξύ ενοτήτων ("Στο επόμενο κεφάλαιο...")

### 4. Παραπομπές και Βιβλιογραφία

- Ενδοκειμενικές αναφορές με **αριθμητικό σύστημα**: [1], [2], [3]...
- Βιβλιογραφία **ανά κεφάλαιο** ("Βιβλιογραφία Κεφαλαίου X") με αρίθμηση που ξεκινά από [1] σε κάθε κεφάλαιο
- Κάθε αναφορά να έχει **DOI link** όπου διαθέσιμο: `doi: https://doi.org/...`
- Όλες οι βιβλιογραφικές εγγραφές πρέπει να έχουν αναφερθεί μέσα στο κείμενο
- Η βιβλιογραφική επισκόπηση να είναι **εκτενής**, με θεματική οργάνωση, σύγκριση μεθόδων/ευρημάτων

### 5. Κώδικας

- **Μη βάζεις μεγάλα κομμάτια κώδικα** — μόνο αποσπάσματα 5–15 γραμμών για απεικόνιση έννοιας
- Προτίμησε pseudocode ή διαγράμματα ροής από πλήρη implementation
- Όταν δείχνεις κώδικα: να συνοδεύεται από εξήγηση δομής, κύριων συναρτήσεων, εισόδων–εξόδων

### 6. Γενικές Αρχές Συγγραφής

- **Γλώσσα:** Ελληνικά, ακαδημαϊκό ύφος
- **Πρόσωπο:** Τρίτο ("αναπτύχθηκε", "υλοποιήθηκε", "παρατηρείται") — εκτός Ευχαριστιών
- Κάθε ισχυρισμός να συνοδεύεται από βιβλιογραφική αναφορά ή πειραματικό αποτέλεσμα
- Έμφαση στην **αναπαραγωγιμότητα**: περιγραφή πειραματικού πλαισίου, ρυθμίσεων, μετρικών

---

## ΜΕΡΟΣ Γ — ΤΙ ΕΙΝΑΙ ΤΟ ΣΥΣΤΗΜΑ GEO-ADS

Το GEO-ADS είναι ένα **real-time σύστημα διαχείρισης και προβολής στοχευμένων διαφημίσεων σε αθλητικές εγκαταστάσεις**. Επιτρέπει την ανάθεση διαφημίσεων σε οθόνες γηπέδου με βάση τη γεωγραφική θέση του θεατή, σε πραγματικό χρόνο, με πλήρες επίπεδο ασφάλειας 6 στρωμάτων.

### Αρχιτεκτονική Συστήματος

| Στρώμα | Τεχνολογία | Σκοπός |
|--------|-----------|--------|
| Backend | FastAPI (Python 3.11+) | REST API + WebSocket server, port 8000 |
| Database | PostgreSQL 16 + PostGIS | Αποθήκευση διαφημίσεων, χωρικά ευρετήρια |
| Frontend | React 18 | Stadium Board UI + Security Dashboard, port 3000 |
| Desktop | Electron | All-in-one εφαρμογή (εκκινεί backend + φορτώνει UI) |
| Real-time | WebSockets (native FastAPI) | Live updates διαφημίσεων και security alerts |
| Security | JWT + HMAC + Anti-Replay + Rate Limiting + Audit Log + Threat Engine | 6 επίπεδα ασφάλειας |

### Ζώνες Γηπέδου (3 ζώνες, 28 οθόνες συνολικά)

| Ζώνη | Grid | Οθόνες | Τύπος |
|------|------|--------|-------|
| GlassFloor | 4×4 | 16 tiles | glassfloor_tile |
| Surrounding Screens | 2×4 | 8 banners | surrounding_banner |
| Megatron | 2×2 | 4 panels | megatron_panel |

### REST API Endpoints

| Method | Path | Scope | Περιγραφή |
|--------|------|-------|-----------|
| GET | /health | — | Health check |
| GET | /advertisements | ads:read | Λίστα διαφημίσεων |
| GET | /advertisements/zone/{zone_id} | ads:read | Διαφημίσεις ανά ζώνη |
| GET | /layout | layout:read | Layout ζωνών & οθονών |
| GET | /layout/query/near | layout:read | Χωρική αναζήτηση (R-Tree) |
| GET | /layout/multiindex | layout:read | Σύγκριση όλων των indexes |
| GET | /layout/recommendation/screen | recommendation:read | Recommendation engine |
| GET | /placements | placements:read | Τρέχουσες αναθέσεις |
| POST | /placements/recommend_and_assign/advertisements/{ad_id} | placements:write | Ανάθεση διαφήμισης |
| POST | /auth/login | — | Login (username/password) |
| POST | /auth/token | X-Admin-Secret | Internal token |
| POST | /auth/refresh | — | Refresh access token |
| GET | /security/alerts | security:read | Active alerts |
| GET | /security/events | security:read | Event log |
| GET | /security/stats | security:read | Στατιστικά |
| GET | /security/comparison | security:read | Rule vs Statistical σύγκριση |
| WS | /ws/ads | ads:read | Real-time ads updates |
| WS | /ws/placements | placements:read | Real-time placement events |
| WS | /ws/security | security:read | Real-time security alerts |

---

## ΜΕΡΟΣ Δ — ΕΡΕΥΝΗΤΙΚΕΣ ΕΡΩΤΗΣΕΙΣ (ΕΡ-1 έως ΕΡ-9)

| Κωδικός | Ερευνητική Ερώτηση | Πού απαντάται στη διπλωματική |
|---------|-------------------|-------------------------------|
| ΕΡ-1 | Πώς οργανώνονται οι ζώνες οθονών σε ένα γήπεδο; | Κεφ. 4 — Σχεδιασμός |
| ΕΡ-2 | Ποια μέθοδος πολυδιάστατης ευρετηρίασης είναι πιο αποδοτική για χωρικές ερωτήσεις; | Κεφ. 6 — Πείραμα 1 |
| ΕΡ-3 | Πώς υλοποιείται ένα recommendation engine για ανάθεση διαφημίσεων; | Κεφ. 5 |
| ΕΡ-4 | Πώς επιτυγχάνεται real-time επικοινωνία μεταξύ server και clients; | Κεφ. 3 + 5 |
| ΕΡ-5 | Πώς προστατεύονται τα HTTP και WebSocket endpoints με JWT; | Κεφ. 3 + 5 |
| ΕΡ-6 | Πώς ενσωματώνονται εικόνες διαφημίσεων στις οθόνες; | Κεφ. 5 |
| ΕΡ-7 | Γιατί PostgreSQL για real-time γεω-στοχευμένο σύστημα; | Κεφ. 4 |
| ΕΡ-8 | Πώς συσκευάζεται το σύστημα ως desktop εφαρμογή; | Κεφ. 5 |
| ΕΡ-9 | Πώς ανιχνεύονται απειλές σε πραγματικό χρόνο με υβριδική προσέγγιση; | Κεφ. 6 — Πείραμα 2 |

---

## ΜΕΡΟΣ Ε — ΚΥΡΙΑ ΕΡΕΥΝΗΤΙΚΑ ΕΥΡΗΜΑΤΑ

### Εύρημα 1: Σύγκριση Μεθόδων Χωρικής Ευρετηρίασης (ΕΡ-2)

Υλοποιήθηκαν και μετρήθηκαν 4 στρατηγικές για spatial range queries:

**Αλγοριθμική Πολυπλοκότητα:**

| Μέθοδος | Κατασκευή | Query | Αποθήκευση |
|---------|-----------|-------|-----------|
| Linear Scan | O(n) | O(n) | O(n) RAM |
| R-Tree | O(n log n) | O(log n + k) | O(n) RAM |
| PostGIS GIST | O(n log n) | O(log n) + I/O | O(n) Δίσκος |
| Distributed (k=3 shards) | O(n log n/k) | O(log n/k) parallel | O(n) RAM |

**Πειραματικά Αποτελέσματα (μετρήσεις σε ms):**

| N screens | Linear (ms) | R-Tree (ms) | Distributed (ms) | Speedup R-Tree | Speedup Dist |
|-----------|------------|-------------|-----------------|---------------|-------------|
| 28 | 0.004 | 0.008 | 0.444 | 0.54x | 0.01x |
| 100 | 0.018 | 0.012 | 0.435 | 1.45x | 0.04x |
| 1.000 | 0.148 | 0.035 | 0.455 | 4.25x | 0.32x |
| 10.000 | 1.475 | 0.200 | 0.616 | 7.36x | 2.4x |
| 100.000 | 14.551 | 1.799 | 2.414 | 8.09x | 6.03x |

**Συμπεράσματα:**
- Για n=28 (πραγματικό γήπεδο): Linear κερδίζει — R-Tree έχει overhead χωρίς όφελος
- Για n>100: R-Tree ξεπερνά το Linear σταθερά
- Distributed: σταθερό overhead ~0.44ms από thread spawning, δεν αξίζει για n<10.000
- **Επιλογή production:** R-Tree — επεκτάσιμο, αμελητέα διαφορά για n=28, O(log n) για μέλλον
- PostGIS GIST: χρησιμοποιείται για ακριβείς γεωγραφικές αποστάσεις σε μέτρα (WGS-84)

### Εύρημα 2: Υβριδική Ανίχνευση Απειλών — Rule-based vs Statistical (ΕΡ-9)

Υλοποιήθηκε υβριδικό σύστημα (ThreatEngine) που τρέχει **παράλληλα** δύο detectors σε κάθε event:

**Rule-based Detector:**

| Κανόνας | Συνθήκη | Severity |
|---------|---------|---------|
| brute_force | 5+ auth_failed από ίδια IP / 5 λεπτά | CRITICAL |
| credential_stuffing | 10+ μοναδικά usernames / 10 λεπτά | CRITICAL |
| replay_attack | 3+ replay attempts / 5 λεπτά | CRITICAL |
| rate_abuse | 20+ rate-limited requests / 10 λεπτά | WARNING |

**Statistical Detector (Z-score Anomaly Detection):**
- Παρακολουθεί event rate σε sliding windows: 5min, 15min, 1h
- Alert όταν: `z_score = (current_rate - mean) / std_dev > 2.0`
- Χρειάζεται ≥3 historical data points για υπολογισμό baseline
- Ανιχνεύει ανωμαλίες που **δεν καλύπτουν** οι hardcoded κανόνες

**Αποτελέσματα (τυπική εκτέλεση test_threat_detection.py):**
- Rule-based avg detection time: ~0.014 ms
- Statistical avg detection time: ~0.013 ms
- Για brute force simulation (6 failed logins): Rule detector ανιχνεύει πρώτος
- "Both detected": events που εντοπίστηκαν και από τους δύο detectors
- **Συμπέρασμα:** Υβριδική προσέγγιση καλύπτει περισσότερες περιπτώσεις — rule για γνωστά patterns, statistical για άγνωστες ανωμαλίες

---

## ΜΕΡΟΣ ΣΤ — ΤΕΧΝΟΛΟΓΙΕΣ & ΕΡΓΑΛΕΙΑ

### Backend (Python 3.11+)
- **FastAPI**: async REST + WebSocket framework
- **uvicorn**: ASGI server
- **PostgreSQL 16**: κύρια βάση δεδομένων
- **PostGIS**: γεωγραφική επέκταση (ST_DWithin, ST_MakePoint, GIST index)
- **psycopg2**: PostgreSQL driver
- **python-jose**: JWT generation/verification (HS256)
- **slowapi**: rate limiting (10/min login, 5/min token)
- **rtree** (libspatialindex): in-memory R-Tree spatial index
- **hmac, hashlib**: HMAC-SHA256 / SHA3-256 για WS message signing

### Frontend (React 18)
- **React 18**: SPA framework
- **WebSocket API**: native browser WebSockets
- **CSS Grid/Flexbox**: responsive layout

### Desktop
- **Electron**: packaging React + backend σε desktop app
- **cross-env**: cross-platform environment variables
- **npm scripts**: automated build pipeline (build:ui → electron .)

### Database Schema

```sql
-- Κύριοι πίνακες
advertisements(id, name, image_url, zone, created_at)
zones(id, name, type)
screens(id, zone_id, row_idx, col_idx, screen_type,
        location GEOGRAPHY(POINT, 4326))

-- Χωρικό ευρετήριο
CREATE INDEX idx_screens_location ON screens USING GIST(location);

-- Placements: in-memory (γνωστό limitation — δεν persist στο restart)
```

---

## ΜΕΡΟΣ Ζ — ΕΠΙΠΕΔΑ ΑΣΦΑΛΕΙΑΣ (6 στρώματα)

| Επίπεδο | Μηχανισμός | Λεπτομέρεια |
|---------|-----------|-------------|
| v1 | JWT Bearer Tokens | HS256, scoped, 1h TTL access + 24h refresh |
| v2 | HMAC-SHA256 | Υπογραφή WS μηνυμάτων, SHA-256 ή SHA3-256 (env CRYPTO_MODE) |
| v3 | Anti-Replay | Timestamp window 60s + nonce deduplication in-memory |
| v4 | Rate Limiting | slowapi: 10/min login, 5/min /auth/token, 10/min refresh |
| v5 | Audit Logging | JSON middleware → audit.log (time, method, path, user, status, ms) |
| v6 | Threat Detection | ThreatEngine singleton: Rule-based + Z-score Statistical, real-time WS push |

**JWT Token Scopes:**
`ads:read`, `placements:read`, `placements:write`, `layout:read`, `recommendation:read`, `security:read`

---

## ΜΕΡΟΣ Η — ΠΛΗΡΗΣ ΔΟΜΗ ΚΕΦΑΛΑΙΩΝ

```
ΠΡΟΚΑΤΑΡΚΤΙΚΑ
  Εξώφυλλο
  Τριμελής Επιτροπή
  Υπεύθυνη Δήλωση
  Περίληψη (Ελληνικά) — 200-300 λέξεις
  Abstract (Αγγλικά) — 200-300 λέξεις
  Ευχαριστίες
  Πίνακας Περιεχομένων
  Ευρετήριο Εικόνων
  Ευρετήριο Πινάκων

ΚΕΦΑΛΑΙΟ 1: ΕΙΣΑΓΩΓΗ (~2.000–2.500 λέξεις)
  1.1 Κίνητρο & Πρόβλημα
      - Αύξηση ψηφιακής διαφήμισης σε αθλητικές εγκαταστάσεις
      - Ανάγκη real-time, geo-targeted λύσης
      - Πρόβλημα: έλλειψη ολοκληρωμένου συστήματος με ασφάλεια
  1.2 Στόχοι Διπλωματικής
      - Σχεδιασμός και υλοποίηση GEO-ADS
      - Σύγκριση μεθόδων χωρικής ευρετηρίασης
      - Υβριδική ανίχνευση απειλών
  1.3 Ερευνητικές Ερωτήσεις (ΕΡ-1 έως ΕΡ-9)
  1.4 Συνεισφορά Εργασίας
  1.5 Δομή Εργασίας (τι περιέχει κάθε κεφάλαιο)

ΚΕΦΑΛΑΙΟ 2: ΒΙΒΛΙΟΓΡΑΦΙΚΗ ΑΝΑΣΚΟΠΗΣΗ (~4.500–5.500 λέξεις)
  2.1 Ψηφιακή Διαφήμιση & Γεω-Στόχευση
      - Programmatic advertising, location-based advertising
      - Υπάρχουσες λύσεις και περιορισμοί τους
  2.2 Χωρικά Ευρετήρια
      - R-Tree (Guttman 1984) και παραλλαγές
      - PostGIS / GIST indexes
      - Distributed spatial indexes
  2.3 Real-time Συστήματα & WebSocket
      - WebSocket protocol (RFC 6455)
      - Server-Sent Events vs WebSocket vs Polling
      - Real-time αρχιτεκτονικές σε web εφαρμογές
  2.4 Ασφάλεια Web Εφαρμογών
      - JWT (RFC 7519) — σχετική βιβλιογραφία
      - HMAC authentication
      - Anti-replay mechanisms
      - OWASP Top 10
  2.5 Ανίχνευση Ανωμαλιών (Anomaly Detection)
      - Rule-based IDS
      - Statistical anomaly detection (Z-score, μέση τιμή, τυπική απόκλιση)
      - Υβριδικές προσεγγίσεις

ΚΕΦΑΛΑΙΟ 3: ΘΕΩΡΗΤΙΚΟ ΠΛΑΙΣΙΟ (~5.000–6.000 λέξεις)
  3.1 Χωρικά Ευρετήρια — Αλγοριθμική Ανάλυση
      3.1.1 Linear Scan — O(n)
      3.1.2 R-Tree — O(log n + k), δομή MBR
      3.1.3 PostGIS GIST — σφαιρικό μοντέλο WGS-84
      3.1.4 Distributed Index — MapReduce pattern, k shards
      3.1.5 Σύγκριση πολυπλοκότητας (πίνακας)
  3.2 WebSocket Protocol
      - Handshake, frames, full-duplex επικοινωνία
      - Σύγκριση με HTTP polling
  3.3 JWT & HMAC
      - Δομή JWT (header.payload.signature)
      - HMAC-SHA256: κατακερματισμός + HMAC
      - Token scopes & authorization
  3.4 Ανίχνευση Απειλών
      - Z-score: ορισμός, τύπος, sliding windows
      - Rule-based: threshold-based detection
      - Υβριδική: πλεονεκτήματα συνδυασμού

ΚΕΦΑΛΑΙΟ 4: ΣΧΕΔΙΑΣΜΟΣ ΣΥΣΤΗΜΑΤΟΣ (~3.000–4.000 λέξεις)
  4.1 Αρχιτεκτονική Συστήματος
      - Διάγραμμα: Electron → React → FastAPI → PostgreSQL
      - Επικοινωνία HTTP REST + WebSocket
  4.2 Ζώνες Γηπέδου & Μοντέλο Οθονών
      - GlassFloor (4×4), Surrounding (2×4), Megatron (2×2)
      - Αιτιολόγηση επιλογής 3 ζωνών
  4.3 Σχεδιασμός Βάσης Δεδομένων
      - ER Διάγραμμα
      - Πίνακες: advertisements, zones, screens
      - PostGIS GEOGRAPHY type για spatial data
  4.4 Σχεδιασμός Real-time Επικοινωνίας
      - /ws/ads: polling DB ανά hash change
      - /ws/placements: snapshot + placement_assigned events
      - /ws/security: real-time alert push
  4.5 Σχεδιασμός Ασφάλειας
      - Διάγραμμα 6 επιπέδων
      - Auth flow: login → access_token + refresh_token
      - Token scopes ανά endpoint

ΚΕΦΑΛΑΙΟ 5: ΥΛΟΠΟΙΗΣΗ ΣΥΣΤΗΜΑΤΟΣ (~4.500–5.500 λέξεις)
  5.1 Εργαλεία & Τεχνολογίες
      - Αιτιολόγηση επιλογής FastAPI, React, PostgreSQL, Electron
  5.2 Backend: REST API
      - Δομή κώδικα (app/main.py, models, services, security)
      - Κύρια endpoints με παράδειγμα request/response
  5.3 Χωρική Ευρετηρίαση: MultiDimScreenIndex
      - Υλοποίηση Linear, R-Tree, PostGIS, Distributed
      - Κώδικας (αποσπάσματα)
  5.4 Recommendation Engine
      - Αλγόριθμος: χωρική αναζήτηση → scoring → ανάθεση
  5.5 WebSocket Handlers
      - /ws/ads, /ws/placements, /ws/security
      - JWT authentication στο WS handshake
  5.6 Σύστημα Ασφάλειας
      - JWT service (mint_token, decode_and_verify)
      - HMAC signing (CryptoEngine)
      - Anti-replay (nonce store, timestamp window)
      - Rate limiting (slowapi decorators)
      - Audit middleware
      - ThreatEngine (rule + statistical detectors)
  5.7 Frontend: VisualBoard & SecurityDashboard
      - Στιγμιότυπα οθόνης (screenshots)
      - WebSocket client logic
      - Token auto-refresh
  5.8 Desktop Εφαρμογή (Electron)
      - Εκκίνηση backend process
      - Build pipeline: npm run desktop

ΚΕΦΑΛΑΙΟ 6: ΠΕΙΡΑΜΑΤΑ & ΑΞΙΟΛΟΓΗΣΗ (~4.000–5.000 λέξεις)
  6.1 Μεθοδολογία Αξιολόγησης
      - Περιβάλλον εκτέλεσης (hardware, OS, Python version)
      - Μετρικές: χρόνος εκτέλεσης σε ms, speedup ratio
      - Αριθμός επαναλήψεων ανά μέτρηση

  6.2 Πείραμα 1 — Σύγκριση Μεθόδων Χωρικής Ευρετηρίασης (ΕΡ-2)
      6.2.1 Στόχος & Υπόθεση
            "Το R-Tree υπερτερεί του Linear για n > 100,
             αλλά για n=28 (πραγματικό γήπεδο) η διαφορά είναι αμελητέα."
      6.2.2 Μεθοδολογία
            - benchmark_rtree.py, benchmark_all.py scripts
            - N = {28, 100, 1.000, 10.000, 100.000}
            - 1000 επαναλήψεις ανά N, μέση τιμή
      6.2.3 Αποτελέσματα
            - Πίνακας με τα ακριβή νούμερα από benchmark_all_results.csv
            - Γράφημα: χρόνος εκτέλεσης vs N (log scale)
            - Γράφημα: speedup ratio vs N
      6.2.4 Ανάλυση
            - Ερμηνεία αποτελεσμάτων βάσει θεωρίας O(n) vs O(log n)
            - Γιατί Linear κερδίζει για n=28
            - Γιατί Distributed έχει σταθερό overhead
            - Επιλογή R-Tree για production

  6.3 Πείραμα 2 — Υβριδική Ανίχνευση Απειλών (ΕΡ-9)
      6.3.1 Στόχος & Υπόθεση
            "Η υβριδική προσέγγιση (rule + statistical) ανιχνεύει
             περισσότερες απειλές από κάθε μέθοδο μόνη της."
      6.3.2 Μεθοδολογία
            - test_threat_detection.py: 8 κατηγορίες δοκιμών
            - Σενάριο brute force: 6 failed logins σε <1 δευτερόλεπτο
            - Μέτρηση: χρόνος ανίχνευσης (ms), τύπος detector
      6.3.3 Αποτελέσματα
            - Πίνακας: rule_only, statistical_only, both_detected, neither
            - Rule avg detection time: ~0.014 ms
            - Statistical avg detection time: ~0.013 ms
            - Screenshot Security Dashboard με active alerts
      6.3.4 Ανάλυση
            - Rule detector: γρήγορος για γνωστά patterns
            - Statistical: ανιχνεύει ανωμαλίες χωρίς hardcoded κανόνες
            - Υβριδισμός: καλύτερη κάλυψη και από τους δύο

  6.4 Συζήτηση Αποτελεσμάτων
      - Σύνδεση με ερευνητικές ερωτήσεις ΕΡ-2, ΕΡ-9
      - Limitations αξιολόγησης

ΚΕΦΑΛΑΙΟ 7: ΣΥΜΠΕΡΑΣΜΑΤΑ & ΜΕΛΛΟΝΤΙΚΕΣ ΠΡΟΕΚΤΑΣΕΙΣ (~1.500–2.000 λέξεις)
  7.1 Ανακεφαλαίωση
  7.2 Απαντήσεις στις Ερευνητικές Ερωτήσεις ΕΡ-1 έως ΕΡ-9
  7.3 Συνεισφορά στη Βιβλιογραφία
  7.4 Limitations
      - Placements in-memory (χάνονται στο restart)
      - Benchmark σε τοπικό μηχάνημα (όχι production server)
      - Dataset n=28 (μικρό γήπεδο — τα n>100 είναι προσομοίωση)
      - Statistical detector χρειάζεται warm-up period
  7.5 Μελλοντικές Προεκτάσεις
      - Persistence placements στη DB
      - Machine Learning για threat detection (αντί Z-score)
      - Multi-venue support (πολλαπλά γήπεδα)
      - Mobile app για advertisers
      - Kubernetes deployment για horizontal scaling

ΚΕΦΑΛΑΙΟ 8: ΒΙΒΛΙΟΓΡΑΦΙΑ (ανά κεφάλαιο)
```

---

## ΜΕΡΟΣ Θ — ΠΡΟΤΕΙΝΟΜΕΝΗ ΒΙΒΛΙΟΓΡΑΦΙΑ (Σημεία Εκκίνησης)

Χρησιμοποίησε αυτές τις πηγές ως βάση — ζήτα από το AI να βρει DOI links:

1. Guttman, A. (1984). R-Trees: A Dynamic Index Structure for Spatial Searching. *ACM SIGMOD*
2. RFC 6455 — The WebSocket Protocol (2011)
3. RFC 7519 — JSON Web Tokens (JWT) (2015)
4. PostGIS Documentation — ST_DWithin, GIST Index
5. OWASP Top 10 (2021)
6. Chandola, V., Banerjee, A., Kumar, V. (2009). Anomaly Detection: A Survey. *ACM Computing Surveys*
7. Sellis, T., Roussopoulos, N., Faloutsos, C. (1987). The R+-Tree. *VLDB*
8. Tikhonenko, O. (2015). FastAPI documentation
9. Electron Documentation — Main Process, IPC

---

## ΜΕΡΟΣ Ι — ΠΑΡΑΔΕΙΓΜΑΤΑ PROMPT ΓΙΑ ΧΡΗΣΗ

### Για να ξεκινήσεις νέα συνομιλία:
```
Διαβάσε προσεκτικά όλο το παρακάτω context για τη διπλωματική μου εργασία
GEO-ADS. Μετά θα σου ζητήσω να γράψεις συγκεκριμένα κεφάλαια.

[ΕΠΙΚΟΛΛΑ ΟΛΟ ΤΟ ΑΡΧΕΙΟ ΕΔΩ]

Επιβεβαίωσε ότι κατάλαβες το project και είσαι έτοιμος.
```

### Για να γράψεις κεφάλαιο:
```
Γράψε το Κεφάλαιο 1 (Εισαγωγή) της διπλωματικής μου.
Στόχος: 2.000–2.500 λέξεις.
Συμπεριέλαβε όλες τις υποενότητες 1.1 έως 1.5 από τη δομή.
Γράψε στα Ελληνικά, ακαδημαϊκό ύφος, τρίτο πρόσωπο.
Κάθε ισχυρισμός να συνοδεύεται από [Χ] placeholder για βιβλιογραφία.
```

### Για βιβλιογραφία:
```
Για το Κεφάλαιο 2 (Βιβλιογραφική Ανασκόπηση), βρες 8-10 επιστημονικές
αναφορές για [ΘΕΜΑ] με DOI links. Μορφή: [Ν] Συγγραφέας, Τίτλος,
Περιοδικό, Χρονολογία. doi: https://doi.org/...
```

### Για εξήγηση αποτελεσμάτων:
```
Ερμήνευσε τα παρακάτω benchmark αποτελέσματα για το Κεφάλαιο 6.2.4.
Χρησιμοποίησε θεωρία πολυπλοκότητας O(n) vs O(log n).
Αποτελέσματα: [ΒΑΛΕ ΤΟΝ ΠΙΝΑΚΑ ΕΔΩ]
```
