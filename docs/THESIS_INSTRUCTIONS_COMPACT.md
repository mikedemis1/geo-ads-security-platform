# ΟΔΗΓΙΕΣ ΣΥΓΓΡΑΦΗΣ ΔΙΠΛΩΜΑΤΙΚΗΣ — GEO-ADS
# Επικόλλησε αυτό στο ChatGPT πριν ζητήσεις οτιδήποτε.

---

## 1. ΤΑΥΤΟΤΗΤΑ

**Τίτλος (ΕΛ):** Σύστημα Διαχείρισης Γεω-Στοχευμένων Διαφημίσεων Αθλητικών Εγκαταστάσεων σε Πραγματικό Χρόνο
**Τίτλος (EN):** Real-Time Geo-Targeted Advertising Management System for Sports Facilities
**Φοιτητής:** Μιχάλης Δέμης, ΑΜ 1080958
**Ίδρυμα:** Πανεπιστήμιο Πατρών, ΤΗΜΜΥ — Ακαδ. Έτος 2024–2025

---

## 2. ΓΕΝΙΚΕΣ ΟΔΗΓΙΕΣ ΣΥΓΓΡΑΦΗΣ

- **Γλώσσα:** Ελληνικά, ακαδημαϊκό ύφος, τρίτο πρόσωπο ("υλοποιήθηκε", "παρατηρείται") — εκτός Ευχαριστιών
- **Έκταση:** ~25.000–30.000 λέξεις (100–120 σελίδες)
- **Σχήματα/Πίνακες:** υψηλής ποιότητας, με λεζάντα, αναφέρονται τουλάχιστον μία φορά στο κείμενο
- **Βιβλιογραφία:** αριθμητικό σύστημα [1],[2]... ανά κεφάλαιο, με DOI links όπου διαθέσιμο
- **Κώδικας:** μόνο αποσπάσματα 5–15 γραμμών για απεικόνιση έννοιας — όχι πλήρης κώδικας
- **Κάθε κεφάλαιο:** ανοίγει με εισαγωγή, κλείνει με σύνοψη
- **Κάθε ισχυρισμός:** συνοδεύεται από βιβλιογραφική αναφορά ή πειραματικό αποτέλεσμα

**Κατανομή λέξεων:**

| Κεφάλαιο | Λέξεις |
|----------|--------|
| Περίληψη + Abstract | 400–600 |
| Κεφ. 1 Εισαγωγή | 2.000–2.500 |
| Κεφ. 2 Βιβλιογραφική Ανασκόπηση | 4.500–5.500 |
| Κεφ. 3 Θεωρητικό Πλαίσιο | 5.000–6.000 |
| Κεφ. 4 Σχεδιασμός Συστήματος | 3.000–4.000 |
| Κεφ. 5 Υλοποίηση Συστήματος | 4.500–5.500 |
| Κεφ. 6 Πειράματα & Αξιολόγηση | 4.000–5.000 |
| Κεφ. 7 Συμπεράσματα | 1.500–2.000 |

---

## 3. ΤΙ ΕΙΝΑΙ ΤΟ ΣΥΣΤΗΜΑ

Το **GEO-ADS** είναι real-time σύστημα διαχείρισης στοχευμένων διαφημίσεων σε αθλητικές εγκαταστάσεις. Αναθέτει διαφημίσεις σε οθόνες γηπέδου βάσει γεωγραφικής θέσης θεατή, σε πραγματικό χρόνο, με 6 επίπεδα ασφάλειας.

**Αρχιτεκτονική:**

| Στρώμα | Τεχνολογία | Σκοπός |
|--------|-----------|--------|
| Backend | FastAPI (Python 3.11+) | REST API + WebSocket, port 8000 |
| Database | PostgreSQL 16 + PostGIS | Αποθήκευση, χωρικά ευρετήρια |
| Frontend | React 18 | VisualBoard + SecurityDashboard, port 3000 |
| Desktop | Electron | All-in-one app (εκκινεί backend + UI) |
| Real-time | WebSockets | Live updates διαφημίσεων & alerts |
| Security | JWT+HMAC+Anti-Replay+RateLimit+AuditLog+ThreatEngine | 6 επίπεδα |

**Ζώνες Γηπέδου (3 ζώνες, 28 οθόνες):**

| Ζώνη | Grid | Οθόνες |
|------|------|--------|
| GlassFloor | 4×4 | 16 tiles |
| Surrounding Screens | 2×4 | 8 banners |
| Megatron | 2×2 | 4 panels |

---

## 4. ΕΡΕΥΝΗΤΙΚΕΣ ΕΡΩΤΗΣΕΙΣ (ΕΡ-1 έως ΕΡ-9)

| Κωδικός | Ερώτηση | Κεφάλαιο |
|---------|---------|----------|
| ΕΡ-1 | Πώς οργανώνονται ζώνες οθονών σε γήπεδο; | Κεφ. 4 |
| ΕΡ-2 | Ποια μέθοδος χωρικής ευρετηρίασης είναι πιο αποδοτική; | Κεφ. 6 — Πείραμα 1 |
| ΕΡ-3 | Πώς υλοποιείται recommendation engine για ανάθεση διαφημίσεων; | Κεφ. 5 |
| ΕΡ-4 | Πώς επιτυγχάνεται real-time επικοινωνία server–clients; | Κεφ. 3 + 5 |
| ΕΡ-5 | Πώς προστατεύονται HTTP και WebSocket endpoints με JWT; | Κεφ. 3 + 5 |
| ΕΡ-6 | Πώς ενσωματώνονται εικόνες διαφημίσεων στις οθόνες; | Κεφ. 5 |
| ΕΡ-7 | Γιατί PostgreSQL για real-time γεω-στοχευμένο σύστημα; | Κεφ. 4 |
| ΕΡ-8 | Πώς συσκευάζεται το σύστημα ως desktop εφαρμογή; | Κεφ. 5 |
| ΕΡ-9 | Πώς ανιχνεύονται απειλές με υβριδική προσέγγιση; | Κεφ. 6 — Πείραμα 2 |

---

## 5. ΠΕΙΡΑΜΑΤΙΚΑ ΑΠΟΤΕΛΕΣΜΑΤΑ (χρησιμοποίησε ΑΚΡΙΒΩΣ αυτά τα νούμερα)

### Πείραμα 1: Σύγκριση Μεθόδων Χωρικής Ευρετηρίασης

Μετρήθηκαν 4 μέθοδοι για spatial range query ("βρες οθόνες εντός ακτίνας r"):

| Μέθοδος | Πολυπλοκότητα Query |
|---------|-------------------|
| Linear Scan | O(n) |
| R-Tree | O(log n + k) |
| PostGIS GIST | O(log n) + I/O |
| Distributed (3 shards) | O(log n/k) παράλληλα |

**Αποτελέσματα (ms, μέση τιμή 1000 επαναλήψεων):**

| N | Linear (ms) | R-Tree (ms) | Distributed (ms) | Speedup R-Tree |
|---|------------|-------------|-----------------|---------------|
| 28 | 0.004 | 0.008 | 0.444 | 0.54x |
| 100 | 0.018 | 0.012 | 0.435 | 1.45x |
| 1.000 | 0.148 | 0.035 | 0.455 | 4.25x |
| 10.000 | 1.475 | 0.200 | 0.616 | 7.36x |
| 100.000 | 14.551 | 1.799 | 2.414 | 8.09x |

**Συμπέρασμα:** Για n=28 (πραγματικό γήπεδο) Linear κερδίζει λόγω απουσίας overhead. Για n>100 R-Tree υπερτερεί. Distributed έχει σταθερό overhead ~0.44ms από thread spawning. Επιλογή production: R-Tree (επεκτάσιμο, O(log n)).

### Πείραμα 2: Rule-based vs Statistical Threat Detection

Τρέχουν παράλληλα σε κάθε security event:

**Rule-based κανόνες:**

| Κανόνας | Συνθήκη | Severity |
|---------|---------|---------|
| brute_force | 5+ auth_failed / 5min / ίδια IP | CRITICAL |
| credential_stuffing | 10+ μοναδικά usernames / 10min | CRITICAL |
| replay_attack | 3+ replays / 5min | CRITICAL |
| rate_abuse | 20+ rate-limited / 10min | WARNING |

**Statistical (Z-score):** Alert όταν `z = (rate - mean) / std > 2.0` σε windows 5min/15min/1h

**Αποτελέσματα:**
- Rule avg detection: ~0.014 ms
- Statistical avg detection: ~0.013 ms
- Brute force (6 logins): Rule ανιχνεύει πρώτος
- Statistical: ανιχνεύει ανωμαλίες χωρίς hardcoded κανόνες
- Συμπέρασμα: Υβριδισμός = καλύτερη κάλυψη και από τους δύο

---

## 6. ΤΕΧΝΟΛΟΓΙΕΣ

**Backend:** FastAPI, PostgreSQL 16, PostGIS, psycopg2, python-jose (JWT), slowapi (rate limiting), rtree/libspatialindex (R-Tree), uvicorn

**Frontend:** React 18, native WebSocket API

**Desktop:** Electron, cross-env

**Security:** JWT HS256 (1h access + 24h refresh), HMAC-SHA256/SHA3-256, nonce dedup, slowapi, JSON audit log, ThreatEngine (rule + Z-score)

**JWT Scopes:** `ads:read`, `placements:read`, `placements:write`, `layout:read`, `recommendation:read`, `security:read`

**DB Schema:**
```sql
advertisements(id, name, image_url, zone, created_at)
zones(id, name, type)
screens(id, zone_id, row_idx, col_idx, screen_type, location GEOGRAPHY)
CREATE INDEX idx_screens_location ON screens USING GIST(location);
-- Placements: in-memory μόνο (χάνονται στο restart — γνωστό limitation)
```

---

## 7. ΕΠΙΠΕΔΑ ΑΣΦΑΛΕΙΑΣ

| Επίπεδο | Μηχανισμός | Λεπτομέρεια |
|---------|-----------|-------------|
| v1 | JWT Bearer | HS256, scoped, 1h TTL |
| v2 | HMAC-SHA256 | Υπογραφή WS μηνυμάτων |
| v3 | Anti-Replay | Timestamp 60s window + nonce dedup |
| v4 | Rate Limiting | 10/min login, 5/min token, 10/min refresh |
| v5 | Audit Log | JSON middleware → audit.log |
| v6 | Threat Engine | Rule-based + Z-score, real-time WS alerts |

---

## 8. ΔΟΜΗ ΚΕΦΑΛΑΙΩΝ

```
ΠΡΟΚΑΤΑΡΚΤΙΚΑ
  Εξώφυλλο, Τριμελής Επιτροπή, Υπεύθυνη Δήλωση
  Περίληψη (ΕΛ, 200-300 λέξεις)
  Abstract (EN, 200-300 λέξεις)
  Ευχαριστίες, ΠΠ, Ευρετήριο Εικόνων/Πινάκων

ΚΕΦ. 1 — ΕΙΣΑΓΩΓΗ (2.000–2.500 λέξεις)
  1.1 Κίνητρο & Πρόβλημα
  1.2 Στόχοι Διπλωματικής
  1.3 Ερευνητικές Ερωτήσεις ΕΡ-1 έως ΕΡ-9
  1.4 Συνεισφορά Εργασίας
  1.5 Δομή Εργασίας

ΚΕΦ. 2 — ΒΙΒΛΙΟΓΡΑΦΙΚΗ ΑΝΑΣΚΟΠΗΣΗ (4.500–5.500 λέξεις)
  2.1 Ψηφιακή Διαφήμιση & Γεω-Στόχευση
  2.2 Χωρικά Ευρετήρια (R-Tree, PostGIS)
  2.3 Real-time Αρχιτεκτονικές & WebSocket
  2.4 Ασφάλεια Web Εφαρμογών (JWT, HMAC, OWASP)
  2.5 Ανίχνευση Ανωμαλιών (Rule-based, Statistical)

ΚΕΦ. 3 — ΘΕΩΡΗΤΙΚΟ ΠΛΑΙΣΙΟ (5.000–6.000 λέξεις)
  3.1 Χωρικά Ευρετήρια — Αλγοριθμική Ανάλυση
      3.1.1 Linear Scan O(n)
      3.1.2 R-Tree O(log n + k), δομή MBR
      3.1.3 PostGIS GIST, WGS-84
      3.1.4 Distributed, MapReduce pattern
      3.1.5 Σύγκριση πολυπλοκότητας
  3.2 WebSocket Protocol (handshake, frames, full-duplex)
  3.3 JWT & HMAC (δομή, HS256, scopes)
  3.4 Ανίχνευση Απειλών (Z-score ορισμός, sliding windows, rule-based)

ΚΕΦ. 4 — ΣΧΕΔΙΑΣΜΟΣ ΣΥΣΤΗΜΑΤΟΣ (3.000–4.000 λέξεις)
  4.1 Αρχιτεκτονική (διάγραμμα Electron→React→FastAPI→PostgreSQL)
  4.2 Ζώνες Γηπέδου & Μοντέλο Οθονών
  4.3 Σχεδιασμός Βάσης Δεδομένων (ER, PostGIS)
  4.4 Σχεδιασμός Real-time Επικοινωνίας (3 WS channels)
  4.5 Σχεδιασμός Ασφάλειας (6 επίπεδα, auth flow)

ΚΕΦ. 5 — ΥΛΟΠΟΙΗΣΗ ΣΥΣΤΗΜΑΤΟΣ (4.500–5.500 λέξεις)
  5.1 Εργαλεία & Αιτιολόγηση Επιλογών
  5.2 Backend: REST API & WebSocket Handlers
  5.3 Spatial Indexing: Υλοποίηση 4 μεθόδων
  5.4 Recommendation Engine
  5.5 Frontend: VisualBoard & SecurityDashboard (screenshots)
  5.6 Desktop Εφαρμογή (Electron build pipeline)
  5.7 Σύστημα Ασφάλειας (JWT, HMAC, Anti-Replay, ThreatEngine)

ΚΕΦ. 6 — ΠΕΙΡΑΜΑΤΑ & ΑΞΙΟΛΟΓΗΣΗ (4.000–5.000 λέξεις)
  6.1 Μεθοδολογία (hardware, OS, αριθμός επαναλήψεων)
  6.2 Πείραμα 1: Χωρική Ευρετηρίαση (ΕΡ-2)
      6.2.1 Στόχος: "R-Tree vs Linear για διάφορα n"
      6.2.2 Μεθοδολογία: benchmark_all.py, N={28,100,1K,10K,100K}
      6.2.3 Αποτελέσματα: πίνακας + γραφήματα (χρόνος vs N, speedup)
      6.2.4 Ανάλυση: ερμηνεία βάσει O(n) vs O(log n)
  6.3 Πείραμα 2: Ανίχνευση Απειλών (ΕΡ-9)
      6.3.1 Στόχος: "Rule vs Statistical — ποιος ανιχνεύει τι"
      6.3.2 Μεθοδολογία: test_threat_detection.py, 8 κατηγορίες
      6.3.3 Αποτελέσματα: χρόνοι ανίχνευσης, rule_only/stat_only/both
      6.3.4 Ανάλυση: πότε κερδίζει κάθε μέθοδος
  6.4 Συζήτηση Αποτελεσμάτων

ΚΕΦ. 7 — ΣΥΜΠΕΡΑΣΜΑΤΑ & ΜΕΛΛΟΝΤΙΚΕΣ ΠΡΟΕΚΤΑΣΕΙΣ (1.500–2.000 λέξεις)
  7.1 Ανακεφαλαίωση
  7.2 Απαντήσεις στις ΕΡ-1 έως ΕΡ-9
  7.3 Limitations (placements in-memory, τοπικό benchmark, n=28)
  7.4 Μελλοντικές Προεκτάσεις
      - Persistence placements στη DB
      - ML για threat detection
      - Multi-venue support
      - Mobile app

ΚΕΦ. 8 — ΒΙΒΛΙΟΓΡΑΦΙΑ (ανά κεφάλαιο, με DOI)
```

---

## 9. ΓΝΩΣΤΑ LIMITATIONS (αναφέρονται στο Κεφ. 7)

- Placements **in-memory** — χάνονται στο restart
- Benchmark σε **τοπικό μηχάνημα** (Windows), όχι production server
- Dataset **n=28** (πραγματικό) — τα n>100 είναι προσομοίωση επεκτασιμότητας
- Statistical detector χρειάζεται **≥3 data points** warm-up
- Χωρίς real GPS data — συντεταγμένες προσομοιωμένες

---

## 10. ΠΑΡΑΔΕΙΓΜΑΤΑ PROMPT

**Για εκκίνηση:**
```
Διαβάσε το παρακάτω context για τη διπλωματική μου GEO-ADS.
Επιβεβαίωσε ότι κατάλαβες και είσαι έτοιμος να βοηθήσεις στη συγγραφή.
[ΕΠΙΚΟΛΛΑ ΤΟ ΑΡΧΕΙΟ]
```

**Για κεφάλαιο:**
```
Γράψε το Κεφάλαιο [Χ] "[ΤΙΤΛΟΣ]" της διπλωματικής μου GEO-ADS.
Στόχος: [Χ.ΧΧΧ–Χ.ΧΧΧ] λέξεις.
Συμπεριέλαβε υποενότητες [Χ.Χ έως Χ.Χ].
Ελληνικά, ακαδημαϊκό ύφος, τρίτο πρόσωπο.
Placeholder [Χ] για βιβλιογραφικές αναφορές.
```

**Για βιβλιογραφία:**
```
Βρες 8-10 επιστημονικές αναφορές για [ΘΕΜΑ] με DOI links.
Μορφή: [Ν] Συγγραφέας. Τίτλος. Περιοδικό, Χρονολογία. doi: ...
```

**Για ανάλυση αποτελεσμάτων:**
```
Ερμήνευσε τα benchmark αποτελέσματα του Κεφ. 6.2 βάσει θεωρίας
O(n) vs O(log n). Χρησιμοποίησε τα νούμερα από τον πίνακα του context.
Γράψε 400-500 λέξεις, ακαδημαϊκό ύφος.
```
