# ChatGPT Prompts — GEO-ADS Διπλωματική (κεφάλαιο-κεφάλαιο)
# Χρήση: Κόπιαρε ΕΝΑ prompt κάθε φορά στο ChatGPT

---

## ΒΗΜΑ 0 — ΑΡΧΙΚΟΠΟΙΗΣΗ (στείλε πρώτα αυτό, μια φορά)

```
Είσαι βοηθός συγγραφής ακαδημαϊκής διπλωματικής εργασίας.
Θα σου στέλνω prompts ένα-ένα για κάθε υποενότητα.
Κάθε prompt περιέχει όλο το context που χρειάζεσαι.
Κανόνες:
- Γλώσσα: Ελληνικά, ακαδημαϊκό ύφος, τρίτο πρόσωπο
- Βιβλιογραφία: [1], [2]... ενδοκειμενικά, placeholder αν δεν ξέρεις DOI
- ΜΗΝ εφευρίσκεις αριθμούς — χρησιμοποίησε μόνο όσα σου δίνω
- ΜΗΝ γράφεις πλήρη κώδικα — μόνο αποσπάσματα 5-10 γραμμών
Απάντησε "Έτοιμος" για να ξεκινήσουμε.
```

---

## ΠΕΡΙΛΗΨΗ + ABSTRACT

### PROMPT P-1: Περίληψη (Ελληνικά)

```
CONTEXT:
Τίτλος διπλωματικής: "Σύστημα Διαχείρισης Γεω-Στοχευμένων Διαφημίσεων Αθλητικών Εγκαταστάσεων σε Πραγματικό Χρόνο"
Φοιτητής: Μιχάλης Δέμης, ΑΜ 1080958, Πανεπιστήμιο Πατρών, ΤΗΜΜΥ, 2024-2025.

ΤΙ ΕΙΝΑΙ ΤΟ ΣΥΣΤΗΜΑ:
Το GEO-ADS είναι πλατφόρμα real-time διαχείρισης γεω-στοχευμένων διαφημίσεων για αθλητικές εγκαταστάσεις.
Αναθέτει διαφημίσεις σε 28 ψηφιακές οθόνες γηπέδου βάσει γεωγραφικής θέσης θεατή.
Αρχιτεκτονική: FastAPI (Python) + PostgreSQL/PostGIS backend, React frontend, Electron desktop.
Real-time επικοινωνία μέσω WebSocket. 6 επίπεδα ασφάλειας (JWT, HMAC, Anti-Replay, Rate Limiting, Audit Log, Threat Engine).

ΠΕΙΡΑΜΑΤΙΚΑ ΑΠΟΤΕΛΕΣΜΑΤΑ (χρησιμοποίησε ΑΚΡΙΒΩΣ):
- Πείραμα 1: R-Tree 8.09x ταχύτερο από Linear Scan για n=100.000 screens (1.799ms vs 14.551ms)
- Πείραμα 2: Υβριδικό threat detection (rule-based + Z-score statistical): ~0.014ms ανίχνευση

ΖΗΤΟΥΜΕΝΟ:
Γράψε Περίληψη στα Ελληνικά, 200-300 λέξεις.
Κάλυψε: (α) πρόβλημα που λύνει, (β) στόχοι, (γ) μέθοδοι, (δ) αποτελέσματα, (ε) συμπέρασμα.
ΜΗΝ βάλεις βιβλιογραφία στην περίληψη.
```

---

### PROMPT P-2: Abstract (English)

```
CONTEXT (same system as P-1):
Title: "Real-Time Geo-Targeted Advertising Management System for Sports Facilities"
Student: Michalis Demis, University of Patras, ECE Department, 2024-2025.

System: GEO-ADS — real-time geo-targeted advertising platform for sports venues.
Assigns ads to 28 digital screens based on spectator geolocation.
Stack: FastAPI + PostgreSQL/PostGIS + React + Electron. 6 security layers.

Results:
- R-Tree index: 8.09x speedup vs Linear Scan at n=100,000 (1.799ms vs 14.551ms)
- Hybrid threat detection (rule-based + Z-score): ~0.014ms detection latency

TASK:
Write Abstract in English, 200-300 words.
Cover: (a) problem, (b) objectives, (c) methods, (d) results, (e) conclusion.
No bibliography in abstract.
Academic register, passive voice preferred.
```

---

## ΚΕΦΑΛΑΙΟ 1 — ΕΙΣΑΓΩΓΗ

### PROMPT 1.1: Κίνητρο & Πρόβλημα (~500 λέξεις)

```
CONTEXT — GEO-ADS Διπλωματική:
Τίτλος: "Σύστημα Διαχείρισης Γεω-Στοχευμένων Διαφημίσεων Αθλητικών Εγκαταστάσεων σε Πραγματικό Χρόνο"

ΠΡΟΒΛΗΜΑ ΠΟΥ ΑΝΤΙΜΕΤΩΠΙΖΕΤΑΙ:
Τα σύγχρονα αθλητικά γήπεδα διαθέτουν δεκάδες ψηφιακές οθόνες (LED, megatron, glazed floors).
Σήμερα οι διαφημίσεις προβάλλονται τυχαία ή με σταθερό πρόγραμμα — χωρίς γνώση ποιος θεατής βλέπει ποια οθόνη.
Αποτέλεσμα: κακή στόχευση, χαμηλό ROI διαφημιστών, μη βέλτιστη χρήση χώρου.

Η ΛΥΣΗ (GEO-ADS):
Real-time σύστημα που:
1. Γνωρίζει τη γεωγραφική θέση κάθε θεατή (GPS/WiFi/BLE)
2. Αναθέτει στοχευμένες διαφημίσεις στις κοντινότερες οθόνες
3. Ενημερώνει όλα τα clients ταυτόχρονα μέσω WebSocket
4. Προστατεύει τις επικοινωνίες με 6 επίπεδα ασφάλειας

ΖΗΤΟΥΜΕΝΟ:
Γράψε την υποενότητα 1.1 "Κίνητρο και Πρόβλημα" (~500 λέξεις).
Ξεκίνα με το γενικό πρόβλημα της στοχευμένης διαφήμισης σε αθλητικές εγκαταστάσεις.
Αναφέρσου στη σημασία της real-time επεξεργασίας και της γεω-πληροφορίας.
Κλείσε με σύντομη εισαγωγή της λύσης GEO-ADS.
Βάλε placeholders [1], [2], [3] για βιβλιογραφία (αργότερα θα τα συμπληρώσουμε).
Ελληνικά, ακαδημαϊκό ύφος, τρίτο πρόσωπο.

ΒΙΒΛΙΟΓΡΑΦΙΑ: Ψάξε πηγές για:
- "location-based advertising sports venues"
- "digital signage stadiums real-time"
- "geo-targeted advertising ROI effectiveness"
```

---

### PROMPT 1.2: Στόχοι Διπλωματικής (~300 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 1.2 "Στόχοι Διπλωματικής"

ΣΤΟΧΟΙ ΤΟΥ ΣΥΣΤΗΜΑΤΟΣ (αυτούς να αναπτύξεις):
1. Σχεδιασμός και υλοποίηση πλατφόρμας real-time γεω-στοχευμένης διαφήμισης
2. Υλοποίηση και σύγκριση 4 μεθόδων χωρικής ευρετηρίασης (Linear, R-Tree, PostGIS, Distributed)
3. Ανάπτυξη recommendation engine για αυτόματη ανάθεση διαφημίσεων σε οθόνες
4. Επίτευξη real-time ενημέρωσης clients μέσω WebSocket protocol
5. Υλοποίηση 6 επιπέδων ασφάλειας (JWT, HMAC, Anti-Replay, Rate Limiting, Audit Log, ThreatEngine)
6. Πειραματική αξιολόγηση απόδοσης χωρικής ευρετηρίασης και ανίχνευσης απειλών
7. Συσκευασία ως all-in-one desktop εφαρμογή (Electron)

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 1.2 (~300 λέξεις).
Παρουσίασε τους στόχους ως αριθμημένη λίστα με σύντομη επεξήγηση κάθε στόχου.
Συνδέσε κάθε στόχο με την ερευνητική του σημασία.
Ελληνικά, ακαδημαϊκό ύφος.
```

---

### PROMPT 1.3: Ερευνητικές Ερωτήσεις ΕΡ-1 έως ΕΡ-9 (~400 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 1.3 "Ερευνητικές Ερωτήσεις"

ΟΙ 9 ΕΡΕΥΝΗΤΙΚΕΣ ΕΡΩΤΗΣΕΙΣ (χρησιμοποίησε ΑΚΡΙΒΩΣ):
ΕΡ-1: Πώς οργανώνονται ζώνες ψηφιακών οθονών σε γήπεδο; (3 ζώνες, 28 οθόνες)
ΕΡ-2: Ποια μέθοδος χωρικής ευρετηρίασης είναι πιο αποδοτική για εύρεση οθονών εντός ακτίνας;
ΕΡ-3: Πώς υλοποιείται recommendation engine για αυτόματη ανάθεση διαφημίσεων;
ΕΡ-4: Πώς επιτυγχάνεται real-time επικοινωνία server–clients σε αθλητικό γήπεδο;
ΕΡ-5: Πώς προστατεύονται HTTP και WebSocket endpoints με JWT scopes;
ΕΡ-6: Πώς ενσωματώνονται εικόνες διαφημίσεων στις ψηφιακές οθόνες;
ΕΡ-7: Γιατί η PostgreSQL επιλέγεται για real-time γεω-στοχευμένο σύστημα;
ΕΡ-8: Πώς συσκευάζεται το σύστημα ως all-in-one desktop εφαρμογή με Electron;
ΕΡ-9: Πώς ανιχνεύονται απειλές ασφάλειας με υβριδική rule-based + statistical προσέγγιση;

ΠΟΥ ΑΠΑΝΤΙΟΥΝΤΑΙ:
ΕΡ-1,4,5,6,7,8 → Κεφ. 4+5 (Σχεδιασμός + Υλοποίηση)
ΕΡ-2 → Κεφ. 6, Πείραμα 1
ΕΡ-9 → Κεφ. 6, Πείραμα 2
ΕΡ-3 → Κεφ. 5

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 1.3 (~400 λέξεις).
Παρουσίασε τις 9 ΕΡ σε πίνακα ή αριθμημένη λίστα.
Για κάθε ΕΡ: 1 πρόταση επεξήγησης + σε ποιο κεφάλαιο απαντάται.
Εισαγωγικό παράγραφο που εξηγεί γιατί διατυπώθηκαν αυτές οι ΕΡ.
Ελληνικά, ακαδημαϊκό ύφος.
```

---

### PROMPT 1.4: Συνεισφορά Εργασίας (~400 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 1.4 "Συνεισφορά Εργασίας"

ΠΡΑΓΜΑΤΙΚΗ ΣΥΝΕΙΣΦΟΡΑ ΤΟΥ ΣΥΣΤΗΜΑΤΟΣ:
1. Ολοκληρωμένο real-time σύστημα γεω-στοχευμένης διαφήμισης (end-to-end, production-ready)
2. Πειραματική σύγκριση 4 μεθόδων χωρικής ευρετηρίασης με benchmark αποτελέσματα:
   - R-Tree αποδεικνύεται 8.09x ταχύτερο από Linear για n=100.000
   - Distributed: σταθερό overhead ~0.44ms από thread spawning
3. Υβριδικό σύστημα ανίχνευσης απειλών (rule-based + Z-score statistical) — πρωτότυπο για αθλητικές πλατφόρμες
4. 6-επίπεδη αρχιτεκτονική ασφάλειας (JWT + HMAC + Anti-Replay + RateLimit + AuditLog + ThreatEngine)
5. All-in-one desktop εφαρμογή (Electron) — χωρίς εξαρτήσεις εγκατάστασης
6. Ανοιχτή, επεκτάσιμη αρχιτεκτονική (FastAPI + PostgreSQL/PostGIS) για multi-venue υποστήριξη

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 1.4 (~400 λέξεις).
Παρουσίασε τι προσφέρει η εργασία που δεν υπάρχει ήδη στη βιβλιογραφία.
Έμφαση στον συνδυασμό real-time + geo-targeting + security σε αθλητική εγκατάσταση.
Βάλε placeholders [1], [2] για βιβλιογραφία.
Ελληνικά, ακαδημαϊκό ύφος.
```

---

### PROMPT 1.5: Δομή Εργασίας (~300 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 1.5 "Δομή Εργασίας"

ΔΟΜΗ ΤΗΣ ΔΙΠΛΩΜΑΤΙΚΗΣ:
Κεφ. 1: Εισαγωγή — κίνητρο, στόχοι, ΕΡ, συνεισφορά
Κεφ. 2: Βιβλιογραφική Ανασκόπηση — ψηφιακή διαφήμιση, χωρικά ευρετήρια, WebSocket, JWT/HMAC, ανίχνευση ανωμαλιών
Κεφ. 3: Θεωρητικό Πλαίσιο — αλγόριθμοι χωρικής ευρετηρίασης, WebSocket, JWT, Z-score
Κεφ. 4: Σχεδιασμός Συστήματος — αρχιτεκτονική, ζώνες γηπέδου, βάση δεδομένων, real-time, ασφάλεια
Κεφ. 5: Υλοποίηση — backend/frontend/desktop, spatial indexing, recommendation engine, security
Κεφ. 6: Πειράματα & Αξιολόγηση — benchmark χωρικής ευρετηρίασης, threat detection
Κεφ. 7: Συμπεράσματα — απαντήσεις στις ΕΡ, limitations, μελλοντικές προεκτάσεις

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 1.5 (~300 λέξεις).
Παρουσίασε τα κεφάλαια σε 1-2 προτάσεις το καθένα.
Τόνισε τη λογική ροή: θεωρία → σχεδιασμός → υλοποίηση → αξιολόγηση.
Ελληνικά, ακαδημαϊκό ύφος.
```

---

## ΚΕΦΑΛΑΙΟ 2 — ΒΙΒΛΙΟΓΡΑΦΙΚΗ ΑΝΑΣΚΟΠΗΣΗ

### PROMPT 2.0: Εισαγωγική παράγραφος Κεφ. 2 (~150 λέξεις)

```
CONTEXT — GEO-ADS Βιβλιογραφική Ανασκόπηση

ΖΗΤΟΥΜΕΝΟ:
Γράψε την εισαγωγική παράγραφο του Κεφαλαίου 2 (~150 λέξεις).
Εξήγησε γιατί η βιβλιογραφική ανασκόπηση καλύπτει 5 θεματικές:
(α) ψηφιακή διαφήμιση & γεω-στόχευση, (β) χωρικά ευρετήρια,
(γ) real-time αρχιτεκτονικές & WebSocket, (δ) ασφάλεια web εφαρμογών,
(ε) ανίχνευση ανωμαλιών.
Κάθε θεματική συνδέεται με ερευνητικές ερωτήσεις ΕΡ-1 έως ΕΡ-9.
Ελληνικά, ακαδημαϊκό ύφος.
```

---

### PROMPT 2.1: Ψηφιακή Διαφήμιση & Γεω-Στόχευση (~1.000 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 2.1 "Ψηφιακή Διαφήμιση & Γεω-Στόχευση"

ΣΧΕΣΗ ΜΕ ΤΟ ΕΡΓΟ:
Το GEO-ADS χρησιμοποιεί γεωγραφική θέση θεατή για ανάθεση διαφημίσεων σε 28 οθόνες αθλητικού γηπέδου.
3 ζώνες: GlassFloor (4×4=16 tiles), Surrounding Screens (2×4=8 banners), Megatron (2×2=4 panels).
Στόχος: ο κοντινότερος θεατής βλέπει τη διαφήμιση που του ταιριάζει.

ΘΕΜΑΤΑ ΠΟΥ ΠΡΕΠΕΙ ΝΑ ΚΑΛΥΦΘΟΥΝ:
1. Εξέλιξη digital advertising: από static displays σε programmatic/real-time
2. Location-based advertising (LBA): ορισμός, κατηγορίες (geofencing, proximity)
3. Digital signage σε αθλητικές εγκαταστάσεις: παραδείγματα, πρακτικές
4. Out-of-Home (OOH) advertising → Programmatic Digital OOH (pDOOH)
5. Σύγκριση προσεγγίσεων στη βιβλιογραφία (τι λείπει / κενό γνώσης)

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 2.1 (~1.000 λέξεις).
Θεματική οργάνωση, σύγκριση μεθόδων, σύνθεση συμπερασμάτων.
Κλείσε με παράγραφο "Κενό Γνώσης" — τι δεν καλύπτει η βιβλιογραφία (που καλύπτει το GEO-ADS).
Βιβλιογραφία: χρησιμοποίησε [1]-[6] ως placeholders.

ΒΙΒΛΙΟΓΡΑΦΙΑ (ψάξε για αυτές τις πηγές):
- "programmatic digital out-of-home advertising" (2019-2024)
- "location-based advertising mobile" journal articles
- "digital signage sports stadiums" case studies
- "geo-targeted advertising effectiveness ROI"
- Βιβλίο: Kotler "Marketing Management" για βασική θεωρία
```

---

### PROMPT 2.2: Χωρικά Ευρετήρια (~1.000 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 2.2 "Χωρικά Ευρετήρια (R-Tree, PostGIS)"

ΣΧΕΣΗ ΜΕ ΤΟ ΕΡΓΟ:
Για εύρεση οθονών εντός ακτίνας r από θεατή, υλοποιήθηκαν 4 μέθοδοι:
- Linear Scan: O(n) — διατρέχει όλες τις οθόνες
- R-Tree: O(log n + k) — ιεραρχικό δέντρο Minimum Bounding Rectangles (MBR)
- PostGIS GIST index: O(log n) + disk I/O — εντός PostgreSQL
- Distributed (3 shards): O(log n/k) παράλληλα — κατανεμημένη επεξεργασία

BENCHMARK ΑΠΟΤΕΛΕΣΜΑΤΑ (χρησιμοποίησε αυτά):
n=28: Linear 0.004ms, R-Tree 0.008ms (Linear κερδίζει λόγω μικρού dataset)
n=100: Linear 0.018ms, R-Tree 0.012ms (R-Tree αρχίζει να υπερτερεί)
n=10.000: Linear 1.475ms, R-Tree 0.200ms (7.36x speedup)
n=100.000: Linear 14.551ms, R-Tree 1.799ms (8.09x speedup)

ΘΕΜΑΤΑ ΠΟΥ ΠΡΕΠΕΙ ΝΑ ΚΑΛΥΦΘΟΥΝ:
1. Ιστορία χωρικών ευρετηρίων: από B-Tree στο R-Tree (Guttman, 1984)
2. R-Tree παραλλαγές στη βιβλιογραφία: R*-Tree, R+-Tree, Hilbert R-Tree
3. PostGIS και GiST ευρετήρια: βιβλιογραφική ανασκόπηση
4. Κατανεμημένη χωρική επεξεργασία: sharding, parallel query
5. Σύγκριση υπαρχουσών προσεγγίσεων

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 2.2 (~1.000 λέξεις).
Θεματική οργάνωση, εξέλιξη μεθόδων, σύγκριση, κενό γνώσης.
Βιβλιογραφία: [1]-[7] placeholders.

ΒΙΒΛΙΟΓΡΑΦΙΑ (ψάξε για):
- Guttman, A. (1984). "R-Trees: A Dynamic Index Structure for Spatial Searching" — SIGMOD
- Beckmann et al. (1990). "R*-Tree" — SIGMOD
- PostGIS documentation και βιβλιογραφία
- "spatial database indexing comparison" survey papers
- "GiST index PostgreSQL" papers
```

---

### PROMPT 2.3: Real-time Αρχιτεκτονικές & WebSocket (~1.000 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 2.3 "Real-time Αρχιτεκτονικές & WebSocket"

ΣΧΕΣΗ ΜΕ ΤΟ ΕΡΓΟ:
Το GEO-ADS χρησιμοποιεί WebSocket για real-time ενημέρωση clients:
- /ws/placements: live ανάθεση διαφημίσεων σε οθόνες
- /ws/layout: ενημέρωση layout γηπέδου
- /ws/security: real-time security alerts (threat detection)
Backend: FastAPI με asyncio, πολλαπλοί concurrent clients.
Frontend: React με native WebSocket API, αυτόματο reconnect.

ΘΕΜΑΤΑ ΠΟΥ ΠΡΕΠΕΙ ΝΑ ΚΑΛΥΦΘΟΥΝ:
1. Εξέλιξη real-time τεχνολογιών: polling → long-polling → SSE → WebSocket
2. WebSocket protocol (RFC 6455): handshake, frames, full-duplex
3. Σύγκριση WebSocket vs REST για real-time σενάρια
4. Event-driven αρχιτεκτονικές: publish-subscribe, message brokers
5. Χρήση WebSocket σε διαφημιστικές πλατφόρμες / digital signage
6. ASGI frameworks (FastAPI/Starlette) για async WebSocket

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 2.3 (~1.000 λέξεις).
Θεματική οργάνωση, σύγκριση τεχνολογιών, κενό γνώσης.
Βιβλιογραφία: [1]-[6] placeholders.

ΒΙΒΛΙΟΓΡΑΦΙΑ (ψάξε για):
- RFC 6455 (WebSocket Protocol) — IETF, 2011
- "WebSocket performance comparison polling SSE" papers
- "real-time web applications architecture" surveys
- "FastAPI async WebSocket" documentation + papers
- "event-driven architecture digital signage" papers
```

---

### PROMPT 2.4: Ασφάλεια Web Εφαρμογών (~1.000 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 2.4 "Ασφάλεια Web Εφαρμογών (JWT, HMAC, OWASP)"

ΣΧΕΣΗ ΜΕ ΤΟ ΕΡΓΟ:
6 επίπεδα ασφάλειας του GEO-ADS:
v1: JWT Bearer tokens (HS256, 1h access + 24h refresh, scoped)
    Scopes: ads:read, placements:read, placements:write, layout:read, recommendation:read, security:read
v2: HMAC-SHA256 υπογραφή WebSocket μηνυμάτων
v3: Anti-Replay (60s timestamp window + nonce deduplication)
v4: Rate Limiting (10/min login, 5/min token endpoint)
v5: Audit Log (JSON format, middleware level)
v6: Threat Engine (rule-based + Z-score statistical)

ΘΕΜΑΤΑ ΠΟΥ ΠΡΕΠΕΙ ΝΑ ΚΑΛΥΦΘΟΥΝ:
1. JWT (RFC 7519): δομή (header.payload.signature), HMAC vs RSA, scopes
2. HMAC (RFC 2104): αρχή, χρήση σε API authentication
3. Replay attacks και αντίμετρα (nonces, timestamps)
4. Rate limiting: Token Bucket vs Sliding Window αλγόριθμοι
5. OWASP Top 10: σχετικά με αυτή την εργασία (Broken Authentication, Injection, etc.)
6. WebSocket security: authentication challenges (no CORS protection native)
7. JWT σε real-time συστήματα: βιβλιογραφική ανασκόπηση

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 2.4 (~1.000 λέξεις).
Θεματική οργάνωση, σύγκριση μηχανισμών, κενό γνώσης.
Βιβλιογραφία: [1]-[7] placeholders.

ΒΙΒΛΙΟΓΡΑΦΙΑ (ψάξε για):
- Jones et al. RFC 7519 JWT (2015) — IETF
- RFC 2104 HMAC (Krawczyk et al., 1997)
- OWASP Foundation — "OWASP Top Ten 2021"
- "JSON Web Token security vulnerabilities" survey papers
- "rate limiting algorithms token bucket sliding window" papers
- "WebSocket security authentication" papers
```

---

### PROMPT 2.5: Ανίχνευση Ανωμαλιών (~1.000 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 2.5 "Ανίχνευση Ανωμαλιών (Rule-based, Statistical)"

ΣΧΕΣΗ ΜΕ ΤΟ ΕΡΓΟ:
ThreatEngine (GEO-ADS): υβριδικό σύστημα που τρέχει παράλληλα:

Rule-based (4 κανόνες):
- brute_force: 5+ αποτυχημένες συνδέσεις / 5min / ίδια IP → CRITICAL
- credential_stuffing: 10+ μοναδικά usernames / 10min → CRITICAL
- replay_attack: 3+ replay attempts / 5min → CRITICAL
- rate_abuse: 20+ rate-limited requests / 10min → WARNING

Statistical (Z-score):
- Υπολογίζει z = (rate - mean) / std σε sliding windows: 5min, 15min, 1h
- Alert αν z > 2.0 (σημαντική απόκλιση από κανονική κατανομή)
- Ανιχνεύει ανωμαλίες ΧΩΡΙΣ hardcoded κανόνες

Αποτελέσματα: Rule ~0.014ms, Statistical ~0.013ms ανίχνευση.

ΘΕΜΑΤΑ ΠΟΥ ΠΡΕΠΕΙ ΝΑ ΚΑΛΥΦΘΟΥΝ:
1. Intrusion Detection Systems (IDS): taxonomy (signature vs anomaly-based)
2. Rule-based systems: πλεονεκτήματα (ταχύτητα, ερμηνευσιμότητα), μειονεκτήματα (false negatives σε 0-day)
3. Statistical anomaly detection: Z-score, μέθοδοι baseline, sliding windows
4. Machine Learning για ανίχνευση απειλών: σύγκριση με rule-based
5. Υβριδικές προσεγγίσεις στη βιβλιογραφία
6. Real-time threat detection σε web APIs

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 2.5 (~1.000 λέξεις).
Θεματική οργάνωση, σύγκριση rule-based vs statistical vs ML, κενό γνώσης.
Τόνισε γιατί ο υβριδισμός (που υλοποιείται στο GEO-ADS) είναι βέλτιστος.
Βιβλιογραφία: [1]-[7] placeholders.

ΒΙΒΛΙΟΓΡΑΦΙΑ (ψάξε για):
- "anomaly detection intrusion detection survey" (2020-2024)
- "Z-score statistical anomaly detection web applications"
- "rule-based vs machine learning intrusion detection comparison"
- "brute force detection sliding window algorithms"
- "real-time security monitoring API rate limiting"
```

---

### PROMPT 2.6: Σύνοψη Κεφ. 2 (~200 λέξεις)

```
CONTEXT — GEO-ADS, Σύνοψη Κεφ. 2

ΖΗΤΟΥΜΕΝΟ:
Γράψε σύντομη σύνοψη (~200 λέξεις) για το τέλος του Κεφ. 2.
Συνόψισε τα κυριότερα ευρήματα από κάθε υποενότητα (2.1-2.5).
Τόνισε το "κενό γνώσης" που καλύπτει το GEO-ADS.
Κάνε μετάβαση στο Κεφ. 3 (Θεωρητικό Πλαίσιο).
Ελληνικά, ακαδημαϊκό ύφος.
```

---

## ΚΕΦΑΛΑΙΟ 3 — ΘΕΩΡΗΤΙΚΟ ΠΛΑΙΣΙΟ

### PROMPT 3.0: Εισαγωγή Κεφ. 3 (~150 λέξεις)

```
CONTEXT — GEO-ADS, εισαγωγή Κεφ. 3 "Θεωρητικό Πλαίσιο"

ΖΗΤΟΥΜΕΝΟ:
Γράψε εισαγωγική παράγραφο (~150 λέξεις).
Εξήγησε ότι το Κεφ. 3 παρέχει την αλγοριθμική και θεωρητική βάση για τις επιλογές σχεδιασμού του GEO-ADS.
Καλύπτει: χωρικά ευρετήρια (Linear, R-Tree, PostGIS, Distributed), WebSocket protocol, JWT & HMAC, Z-score ανίχνευση απειλών.
Ελληνικά, ακαδημαϊκό ύφος.
```

---

### PROMPT 3.1.1: Linear Scan O(n) (~300 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 3.1.1 "Linear Scan — Γραμμική Αναζήτηση O(n)"

ΤΙ ΥΛΟΠΟΙΗΘΗΚΕ:
Η απλούστερη μέθοδος: για κάθε query (θέση θεατή, ακτίνα r), διατρέχει ΟΛΑ τα n screens.
Για κάθε screen υπολογίζει Haversine distance. Επιστρέφει screens εντός r.
Πολυπλοκότητα: O(n) — γραμμική αύξηση με τον αριθμό οθονών.

ΑΠΟΤΕΛΕΣΜΑΤΑ ΣΤΟ BENCHMARK:
n=28: 0.004ms (ταχύτερο λόγω μικρού n, χωρίς overhead)
n=100: 0.018ms
n=10.000: 1.475ms
n=100.000: 14.551ms (8.09x αργότερο από R-Tree)

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 3.1.1 (~300 λέξεις).
Περιέγραψε τον αλγόριθμο, πολυπλοκότητα χρόνου και χώρου, πότε είναι κατάλληλος.
Αναφέρσου στο Haversine formula για γεωγραφικές αποστάσεις.
Βιβλιογραφία: [1]-[2] placeholders.
Ελληνικά, ακαδημαϊκό ύφος.
```

---

### PROMPT 3.1.2: R-Tree O(log n + k) (~500 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 3.1.2 "R-Tree — Ιεραρχική Δομή O(log n + k)"

ΤΙ ΥΛΟΠΟΙΗΘΗΚΕ:
In-memory R-Tree μέσω Python rtree/libspatialindex library.
Κάθε screen αντιπροσωπεύεται από MBR (Minimum Bounding Rectangle).
Query: spatial range query για ακτίνα r γύρω από θέση θεατή.
Η δομή επιτρέπει prune μη-σχετικών κλάδων → O(log n + k) όπου k=αποτελέσματα.

ΚΡΙΣΙΜΕΣ ΛΕΠΤΟΜΕΡΕΙΕΣ:
- Guttman (1984): R-Tree ως επέκταση B-Tree σε 2D/3D χώρο
- MBR: ελάχιστο ορθογώνιο που περιέχει ομάδα αντικειμένων
- Splitting strategies: LinearSplit, QuadraticSplit, R*-Tree (βέλτιστο)
- Insertion: O(log n), Deletion: O(log n), Range Query: O(log n + k)

ΑΠΟΤΕΛΕΣΜΑΤΑ ΣΤΟ BENCHMARK:
n=28: 0.008ms (ελαφρά αργότερο από Linear λόγω overhead δομής)
n=100: 0.012ms (1.45x ταχύτερο από Linear)
n=10.000: 0.200ms (7.36x ταχύτερο)
n=100.000: 1.799ms (8.09x ταχύτερο)

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 3.1.2 (~500 λέξεις).
Περιέγραψε: (α) δομή R-Tree, MBR, κόμβοι, (β) αλγόριθμοι εισαγωγής/διαγραφής/query,
(γ) πολυπλοκότητα, (δ) γιατί υπερτερεί έναντι Linear για μεγάλα n.
Συμπεριέλαβε ένα σχεδιάγραμμα/εικόνα description (θα φτιαχτεί ξεχωριστά).
Βιβλιογραφία: [1] Guttman 1984, [2] Beckmann 1990 (R*-Tree), [3]-[4] placeholders.
```

---

### PROMPT 3.1.3: PostGIS GIST (~400 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 3.1.3 "PostGIS GIST Index — O(log n) + I/O"

ΤΙ ΥΛΟΠΟΙΗΘΗΚΕ:
Τα screens αποθηκεύονται στη PostgreSQL με column τύπου GEOGRAPHY(Point, 4326) (WGS-84).
CREATE INDEX idx_screens_location ON screens USING GIST(location);
Query: ST_DWithin(location, ST_MakePoint(lon, lat)::geography, radius_meters)

ΛΕΠΤΟΜΕΡΕΙΕΣ:
- GiST (Generalized Search Tree): επεκτάσιμη δομή ευρετηρίου στην PostgreSQL
- PostGIS: επέκταση PostgreSQL για γεωχωρικά δεδομένα (ST_* functions)
- WGS-84 (EPSG:4326): παγκόσμιο γεωδαιτικό σύστημα αναφοράς
- Haversine formula (σφαιρικός υπολογισμός) vs Vincenty (ελλειψοειδής)
- Disk I/O overhead: pages του B-Tree, buffer cache

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 3.1.3 (~400 λέξεις).
Περιέγραψε: (α) GiST index, (β) PostGIS spatial functions, (γ) WGS-84,
(δ) πώς η SQL query χρησιμοποιεί το index.
Σημείωσε το disk I/O overhead σε σύγκριση με in-memory R-Tree.
Βιβλιογραφία: [1] PostGIS docs, [2] GiST paper, [3]-[4] placeholders.
```

---

### PROMPT 3.1.4: Distributed (3 shards) (~400 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 3.1.4 "Distributed Spatial Index — MapReduce Pattern"

ΤΙ ΥΛΟΠΟΙΗΘΗΚΕ:
Προσομοίωση κατανεμημένης επεξεργασίας με Python ThreadPoolExecutor:
- 3 shards: κάθε shard έχει ⅓ των screens
- Παράλληλη εκτέλεση R-Tree query σε κάθε shard (3 threads)
- Συγχώνευση αποτελεσμάτων (reduce step)
- Pattern: MapReduce — map(query per shard) + reduce(merge results)

ΚΡΙΣΙΜΟ ΕΎΡΗΜΑ:
Σταθερό overhead ~0.44ms από thread spawning (Python GIL + OS thread creation).
Για n=28: 0.444ms (113x αργότερο από Linear!) — overhead dominates
Για n=100.000: 2.414ms (ταχύτερο από Linear αλλά αργότερο από single R-Tree)
→ Distributed αξίζει μόνο σε πραγματικά distributed systems (πολλαπλά machines)

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 3.1.4 (~400 λέξεις).
Περιέγραψε: (α) MapReduce pattern για spatial queries, (β) sharding strategies,
(γ) γιατί το Python thread overhead είναι εμπόδιο στη συγκεκριμένη υλοποίηση,
(δ) πότε αξίζει πραγματικά το distributed approach.
Βιβλιογραφία: [1] MapReduce paper (Dean & Ghemawat 2004), [2]-[3] placeholders.
```

---

### PROMPT 3.1.5: Σύγκριση Μεθόδων (~300 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 3.1.5 "Σύγκριση Πολυπλοκότητας Χωρικής Ευρετηρίασης"

ΔΕΔΟΜΕΝΑ ΣΥΓΚΡΙΣΗΣ (χρησιμοποίησε ΑΚΡΙΒΩΣ):
| Μέθοδος     | Time Complexity | Space | Κατάλληλο για |
|-------------|-----------------|-------|----------------|
| Linear Scan | O(n)            | O(n)  | n < 100        |
| R-Tree      | O(log n + k)    | O(n)  | 100 < n < 1M   |
| PostGIS GIST| O(log n) + I/O  | O(n)  | Persistent data|
| Distributed | O(log n/k) par. | O(n)  | n > 10M, multi-machine |

BENCHMARK (ms):
n=28: Linear 0.004, R-Tree 0.008, Distributed 0.444
n=100.000: Linear 14.551, R-Tree 1.799, Distributed 2.414

ΕΠΙΛΟΓΗ PRODUCTION:
R-Tree — επειδή: O(log n), in-memory, επεκτάσιμο, χωρίς I/O overhead.
Για n=28 (πραγματικό γήπεδο) η Linear είναι ταχύτερη αλλά μη επεκτάσιμη.

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 3.1.5 (~300 λέξεις).
Παρουσίασε πίνακα σύγκρισης και αναλυτική ερμηνεία.
Αιτιολόγησε την επιλογή R-Tree για production χρήση.
Ελληνικά, ακαδημαϊκό ύφος.
```

---

### PROMPT 3.2: WebSocket Protocol (~500 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 3.2 "WebSocket Protocol"

ΧΡΗΣΗ ΣΤΟ ΕΡΓΟ:
3 WebSocket channels:
- ws://host:8000/ws/placements?token=... → live placement updates
- ws://host:8000/ws/layout?token=... → layout changes
- ws://host:8000/ws/security?token=... → real-time threat alerts
Auth: JWT token ως query parameter (WebSocket δεν υποστηρίζει Authorization header).
HMAC-SHA256 υπογραφή μηνυμάτων (v2 security layer).

ΘΕΩΡΗΤΙΚΑ ΣΤΟΙΧΕΙΑ:
- RFC 6455: WebSocket handshake (HTTP Upgrade), frames, opcodes
- Full-duplex: αμφίδρομη επικοινωνία σε ένα TCP connection
- Frame structure: FIN bit, opcode, mask, payload
- Keep-alive: ping/pong frames
- Σύγκριση με HTTP polling (overhead) και SSE (unidirectional)

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 3.2 (~500 λέξεις).
Περιέγραψε: (α) handshake, (β) frame structure, (γ) full-duplex, (δ) authentication challenges.
Σύγκριση WebSocket vs REST/polling για real-time σενάρια.
Ελληνικά, ακαδημαϊκό ύφος.
Βιβλιογραφία: [1] RFC 6455, [2]-[4] placeholders.
```

---

### PROMPT 3.3: JWT & HMAC (~500 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 3.3 "JWT & HMAC — Θεωρητική Ανάλυση"

ΧΡΗΣΗ ΣΤΟ ΕΡΓΟ:
JWT (HS256):
- Access token: 1h TTL, scoped (ads:read, placements:read, placements:write, layout:read, recommendation:read, security:read)
- Refresh token: 24h TTL
- Secret: >= 32 bytes (enforced, crash on startup if shorter)
- Auth flow: POST /auth/login → {access_token, refresh_token}

HMAC:
- HMAC-SHA256 υπογραφή κάθε WebSocket μηνύματος
- Αποτρέπει message tampering (man-in-the-middle)
- Κλειδί: διαμοιράζεται μεταξύ server και authorized clients

Anti-Replay:
- Timestamp window: 60 seconds (message rejected if older)
- Nonce deduplication: κάθε nonce αποθηκεύεται και απορρίπτεται αν ξαναχρησιμοποιηθεί

ΘΕΩΡΗΤΙΚΑ ΣΤΟΙΧΕΙΑ:
- JWT RFC 7519: δομή (header.payload.signature), claims, HS256 vs RS256
- HMAC RFC 2104: HMAC(K, m) = H((K⊕opad) || H((K⊕ipad) || m))
- Replay attacks: ορισμός, παραδείγματα, αντίμετρα
- Token scopes: principle of least privilege

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 3.3 (~500 λέξεις).
Περιέγραψε: (α) JWT δομή και claims, (β) HS256 αλγόριθμος, (γ) HMAC φόρμουλα,
(δ) Anti-Replay μηχανισμός, (ε) scopes και αρχή minimum privilege.
Βιβλιογραφία: [1] RFC 7519, [2] RFC 2104, [3]-[4] placeholders.
```

---

### PROMPT 3.4: Z-score & Ανίχνευση Απειλών (~400 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 3.4 "Ανίχνευση Απειλών — Z-score & Sliding Windows"

ΧΡΗΣΗ ΣΤΟ ΕΡΓΟ:
Statistical detector:
- Sliding windows: 5min, 15min, 1h
- Για κάθε window: z = (current_rate - mean) / std
- Alert αν z > 2.0
- Warm-up: χρειάζεται >= 3 data points

Rule-based detector:
- brute_force: 5+ auth_failed / 5min / ίδια IP → CRITICAL
- credential_stuffing: 10+ unique usernames / 10min → CRITICAL
- replay_attack: 3+ replays / 5min → CRITICAL
- rate_abuse: 20+ rate-limited / 10min → WARNING

Υβριδισμός: τρέχουν ΠΑΡΑΛΛΗΛΑ, ανεξάρτητα — κάθε event αναλύεται από αμφότερους.

ΘΕΩΡΗΤΙΚΑ ΣΤΟΙΧΕΙΑ:
- Z-score: μέτρο τυπικής απόκλισης από τη μέση τιμή
- Κανονική κατανομή: z > 2.0 → ~2.3% πιθανότητα natural variation
- Sliding window: πλεονεκτήματα έναντι fixed window (recency)
- False positive / false negative tradeoff
- Rule-based: deterministic, fast, interpretable
- Statistical: catches novel attacks without hardcoded rules

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 3.4 (~400 λέξεις).
Περιέγραψε: (α) Z-score ορισμός και ερμηνεία, (β) sliding windows, (γ) threshold επιλογή (z=2.0),
(δ) πλεονεκτήματα/μειονεκτήματα rule-based vs statistical, (ε) σκεπτικό υβριδισμού.
Βιβλιογραφία: [1]-[4] placeholders.
```

---

## ΚΕΦΑΛΑΙΟ 4 — ΣΧΕΔΙΑΣΜΟΣ ΣΥΣΤΗΜΑΤΟΣ

### PROMPT 4.1: Αρχιτεκτονική Συστήματος (~600 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 4.1 "Αρχιτεκτονική Συστήματος"

ΑΡΧΙΤΕΚΤΟΝΙΚΗ (4-επίπεδη):
Επίπεδο 1 — Presentation: Electron (Desktop shell) → React 18 (port 3000)
  - VisualBoard.js: 28 οθόνες γηπέδου real-time
  - SecurityDashboard.js: 4 panels (alerts, timeline, comparison, event log)
Επίπεδο 2 — Application: FastAPI (Python 3.11+, port 8000)
  - REST API: /ads, /placements, /layout, /auth, /security
  - WebSocket: /ws/placements, /ws/layout, /ws/security
Επίπεδο 3 — Data: PostgreSQL 16 + PostGIS (port 5433, Docker)
  - GIST index σε screens.location
  - In-memory placements (γνωστό limitation)
Επίπεδο 4 — Security: JWT + HMAC + Anti-Replay + Rate Limit + Audit + ThreatEngine

ΔΙΑΓΡΑΜΜΑ ΡΟΗΣ:
Θεατής check-in → FastAPI → Spatial Query (R-Tree) → Recommendation Engine → WebSocket broadcast → React update

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 4.1 (~600 λέξεις).
Περιέγραψε τα 4 επίπεδα, τις ροές δεδομένων, τα protocols μεταξύ components.
Αναφέρσου σε σχήμα αρχιτεκτονικής (Σχήμα 4.1 — θα φτιαχτεί ξεχωριστά).
Αιτιολόγησε κάθε επιλογή τεχνολογίας.
Βιβλιογραφία: [1]-[4] placeholders.
```

---

### PROMPT 4.2: Ζώνες Γηπέδου & Μοντέλο Οθονών (~500 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 4.2 "Ζώνες Γηπέδου & Μοντέλο Οθονών"

ΖΩΝΕΣ (3 ζώνες, 28 οθόνες συνολικά):
1. GlassFloor (γυάλινο δάπεδο): 4×4 grid = 16 tiles, τύπος: glassfloor_tile
   - Ορατές από θεατές στις κερκίδες γύρω από το δάπεδο
   - Υψηλή ανάλυση, ανθεκτικές σε πίεση
2. Surrounding Screens (περιμετρικές οθόνες): 2×4 grid = 8 banners, τύπος: surrounding_banner
   - Κατανεμημένες στις 4 πλευρές του γηπέδου
3. Megatron (κεντρική οθόνη): 2×2 grid = 4 panels, τύπος: megatron_panel
   - Μεγάλη οθόνη ορατή από όλες τις θέσεις

DB SCHEMA:
screens(id, zone_id, row_idx, col_idx, screen_type, location GEOGRAPHY(Point,4326))
zones(id, name, type)
CREATE INDEX idx_screens_location ON screens USING GIST(location);

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 4.2 (~500 λέξεις).
Περιέγραψε κάθε ζώνη (θέση, χαρακτηριστικά, ορατότητα).
Παρουσίασε το data model (πίνακες screens, zones).
Αιτιολόγησε τη χρήση GEOGRAPHY αντί GEOMETRY (μέτρα αντί μοίρες).
Αναφέρσου σε διάγραμμα γηπέδου (Σχήμα 4.2).
Ελληνικά, ακαδημαϊκό ύφος.
```

---

### PROMPT 4.3: Σχεδιασμός Βάσης Δεδομένων (~500 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 4.3 "Σχεδιασμός Βάσης Δεδομένων"

ΠΛΗΡΕΣ DB SCHEMA:
advertisements(id SERIAL PK, name VARCHAR, image_url TEXT, zone VARCHAR, created_at TIMESTAMP)
zones(id SERIAL PK, name VARCHAR, type VARCHAR)
screens(id SERIAL PK, zone_id FK→zones, row_idx INT, col_idx INT,
        screen_type VARCHAR, location GEOGRAPHY(Point,4326))
CREATE INDEX idx_screens_location ON screens USING GIST(location);

-- Placements: in-memory (δεν αποθηκεύονται σε DB — γνωστό limitation)
-- 28 screens προεγκατεστημένα με αναλογικές GPS συντεταγμένες

ΕΠΙΛΟΓΕΣ ΣΧΕΔΙΑΣΜΟΥ:
- PostgreSQL 16: ACID, PostGIS extension, mature, open-source
- PostGIS GEOGRAPHY type: WGS-84, Haversine distance, ST_DWithin
- GIST index: R-Tree implementation inside PostgreSQL
- Docker: αναπαραγωγιμότητα, port mapping 5433→5432
- In-memory placements: απόφαση για απλότητα (TODO: persistence)

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 4.3 (~500 λέξεις).
Παρουσίασε ER diagram description (θα φτιαχτεί ξεχωριστά).
Αναλυσε κάθε πίνακα και τις σχέσεις του.
Αιτιολόγησε τις επιλογές (PostgreSQL vs NoSQL, GEOGRAPHY vs GEOMETRY).
Αναφέρσου στο in-memory limitation.
Βιβλιογραφία: [1]-[3] placeholders.
```

---

### PROMPT 4.4: Σχεδιασμός Real-time Επικοινωνίας (~400 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 4.4 "Σχεδιασμός Real-time Επικοινωνίας"

3 WEBSOCKET CHANNELS:
Channel 1: /ws/placements?token=JWT
  - Σκοπός: live broadcast κάθε placement assignment
  - Payload: {screen_id, ad_id, image_url, zone, timestamp}
  - Listeners: VisualBoard.js (ενημερώνει χρώμα tiles)
Channel 2: /ws/layout?token=JWT
  - Σκοπός: αλλαγές στο layout γηπέδου (προσθαφαίρεση οθονών)
Channel 3: /ws/security?token=JWT (scope: security:read)
  - Σκοπός: real-time push threat alerts
  - Payload: {alert_id, type, severity, message, timestamp}
  - Listeners: SecurityDashboard.js

AUTH FLOW WS:
JWT token → query parameter (WebSocket δεν υποστηρίζει Authorization header)
Validation: ίδιος μηχανισμός με REST (python-jose, HS256)

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 4.4 (~400 λέξεις).
Περιέγραψε τους 3 channels, payloads, connection lifecycle.
Αιτιολόγησε γιατί WebSocket και όχι REST polling.
Εξήγησε το JWT-in-query-parameter pattern και τις security implications.
Ελληνικά, ακαδημαϊκό ύφος.
```

---

### PROMPT 4.5: Σχεδιασμός Ασφάλειας — 6 Επίπεδα (~500 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 4.5 "Σχεδιασμός Ασφάλειας"

6 ΕΠΙΠΕΔΑ ΑΣΦΑΛΕΙΑΣ (χρησιμοποίησε ΑΚΡΙΒΩΣ):
v1 — JWT Bearer: HS256, access token 1h TTL, refresh 24h TTL
     Scopes: ads:read, placements:read, placements:write, layout:read, recommendation:read, security:read
v2 — HMAC-SHA256: υπογραφή κάθε WebSocket μηνύματος (node-to-node)
v3 — Anti-Replay: 60s timestamp window + nonce deduplication
v4 — Rate Limiting: 10/min login, 5/min /auth/token, 10/min refresh (slowapi)
v5 — Audit Log: JSON middleware → audit.log, κάθε request καταγράφεται
v6 — Threat Engine: rule-based (4 κανόνες) + Z-score statistical, WS push alerts

AUTH FLOW:
POST /auth/login {username, password} → {access_token (1h), refresh_token (24h)}
POST /auth/refresh {refresh_token} → {access_token (1h)}
POST /auth/token (X-Admin-Secret header) → JWT (internal use)

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 4.5 (~500 λέξεις).
Παρουσίασε τα 6 επίπεδα ως defense-in-depth αρχιτεκτονική.
Για κάθε επίπεδο: σκοπός, μηχανισμός, ποιες επιθέσεις αντιμετωπίζει.
Αναφέρσου στον auth flow diagram (Σχήμα 4.5).
Σχετίσε με OWASP threats.
Βιβλιογραφία: [1]-[4] placeholders.
```

---

## ΚΕΦΑΛΑΙΟ 5 — ΥΛΟΠΟΙΗΣΗ ΣΥΣΤΗΜΑΤΟΣ

### PROMPT 5.1: Εργαλεία & Αιτιολόγηση Επιλογών (~400 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 5.1 "Εργαλεία & Αιτιολόγηση Επιλογών"

ΤΕΧΝΟΛΟΓΙΕΣ ΠΟΥ ΧΡΗΣΙΜΟΠΟΙΗΘΗΚΑΝ:
Backend: FastAPI (Python 3.11+), psycopg2, python-jose, slowapi, rtree/libspatialindex, uvicorn
Database: PostgreSQL 16 + PostGIS, Docker
Frontend: React 18, native WebSocket API
Desktop: Electron, cross-env
Security: JWT HS256, HMAC-SHA256, hmac (stdlib), threading.Lock

ΓΙΑΤΙ ΑΥΤΕΣ ΟΙ ΕΠΙΛΟΓΕΣ:
- FastAPI: async/await, OpenAPI docs αυτόματα, WebSocket native support, type hints
- React: component-based, real-time friendly (state + hooks), npm ecosystem
- PostgreSQL + PostGIS: ACID, ST_DWithin, GIST, mature spatial support
- Electron: packages backend + frontend σε 1 executable, cross-platform
- python-jose: JWT industry standard για Python
- slowapi: rate limiting middleware για FastAPI (Starlette-based)
- rtree: Python wrapper για libspatialindex (C++), high-performance

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 5.1 (~400 λέξεις).
Παρουσίασε κάθε τεχνολογία σε πίνακα: [Τεχνολογία | Σκοπός | Εναλλακτική | Λόγος Επιλογής].
Βιβλιογραφία: [1]-[4] placeholders.
```

---

### PROMPT 5.2: Backend — REST API & WebSocket Handlers (~600 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 5.2 "Backend: REST API & WebSocket Handlers"

REST ENDPOINTS:
GET /ads — λίστα διαφημίσεων (scope: ads:read)
GET /layout — layout γηπέδου, οθόνες, zones (scope: layout:read)
POST /placements — ανάθεση διαφήμισης (scope: placements:write)
GET /placements — τρέχουσες αναθέσεις (scope: placements:read)
GET /recommendations?lat=&lon=&radius= — recommendation query (scope: recommendation:read)
GET /security/alerts — λίστα alerts (scope: security:read)
GET /security/stats — στατιστικά (scope: security:read)
GET /security/comparison — σύγκριση rule vs statistical (scope: security:read)
POST /auth/login — authentication
POST /auth/refresh — token refresh
POST /auth/token — admin token (X-Admin-Secret)

WEBSOCKET:
/ws/placements, /ws/layout, /ws/security (όλα με JWT auth)

ΚΩΔΙΚΑΣ ΑΠΟΣΠΑΣΜΑ (αυτό να βάλεις verbatim):
```python
@app.get("/recommendations")
async def get_recommendations(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius: float = Query(100.0, ge=1, le=50000),
    current_user: dict = Depends(require_scope("recommendation:read"))
):
    results = layout_service.find_screens_rtree(lat, lon, radius)
    return {"screens": results, "count": len(results)}
```

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 5.2 (~600 λέξεις).
Περιέγραψε τα endpoints, input validation (Pydantic ge/le), dependency injection.
Συμπεριέλαβε το παραπάνω απόσπασμα κώδικα ως παράδειγμα.
Αναφέρσου στην αρχή των scopes (principle of least privilege).
Ελληνικά, ακαδημαϊκό ύφος.
```

---

### PROMPT 5.3: Spatial Indexing — Υλοποίηση 4 Μεθόδων (~600 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 5.3 "Spatial Indexing: Υλοποίηση 4 Μεθόδων"

ΑΡΧΕΙΟ: backend/app/services/layout_service.py

4 ΜΕΘΟΔΟΙ:
1. find_screens_linear(lat, lon, radius):
   - Loop όλων των screens, Haversine distance, filter εντός radius
   - O(n), χωρίς index overhead

2. find_screens_rtree(lat, lon, radius):
   - In-memory R-Tree (rtree library), pre-built κατά startup
   - bbox query → φιλτράρισμα → Haversine validation
   - O(log n + k)

3. find_screens_postgis(lat, lon, radius):
   - SQL: SELECT * FROM screens WHERE ST_DWithin(location, ST_MakePoint(%s,%s)::geography, %s)
   - Χρησιμοποιεί GIST index αυτόματα
   - Parameterized queries (fix SQL injection)

4. find_screens_distributed(lat, lon, radius):
   - ThreadPoolExecutor, 3 shards
   - Κάθε shard: R-Tree query σε υποσύνολο screens
   - Reduce: merge + deduplicate αποτελέσματα

ΚΩΔΙΚΑΣ ΑΠΟΣΠΑΣΜΑ (βάλε verbatim):
```python
# R-Tree query
def find_screens_rtree(self, lat, lon, radius_m):
    bbox = self._expand_bbox(lat, lon, radius_m)
    candidates = list(self.rtree_idx.intersection(bbox, objects=True))
    return [s for s in candidates
            if haversine(lat, lon, s.object['lat'], s.object['lon']) <= radius_m]
```

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 5.3 (~600 λέξεις).
Περιέγραψε κάθε μέθοδο: υλοποίηση, κρίσιμες αποφάσεις, trade-offs.
Σχολίασε το parameterized query fix (SQL injection prevention).
Συμπεριέλαβε τα αποσπάσματα κώδικα.
Ελληνικά, ακαδημαϊκό ύφος.
```

---

### PROMPT 5.4: Recommendation Engine (~400 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 5.4 "Recommendation Engine"

ΤΙ ΚΑΝΕΙ:
1. Λαμβάνει θέση θεατή (lat, lon) + ακτίνα (radius_m)
2. Βρίσκει screens εντός ακτίνας (μέσω R-Tree)
3. Ταξινομεί screens κατά απόσταση (κοντινότερες πρώτα)
4. Επιστρέφει διαθέσιμες διαφημίσεις για τις κοντινότερες ζώνες
5. Broadcasts αποτέλεσμα μέσω /ws/placements σε όλους τους connected clients

ΛΟΓΙΚΗ ΑΝΑΘΕΣΗΣ:
- Κάθε screen μπορεί να εμφανίζει μία διαφήμιση τη φορά
- Διαφημίσεις έχουν zone affinity (π.χ. ορισμένες μόνο για GlassFloor)
- In-memory placements dictionary: {screen_id → ad_id}

ΠΕΡΙΟΡΙΣΜΟΙ (αναφέρονται ως limitations):
- Χωρίς ML — proximity-based μόνο
- Χωρίς personalization (δεν γνωρίζει ταυτότητα θεατή)
- In-memory: χάνεται στο restart

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 5.4 (~400 λέξεις).
Περιέγραψε τον αλγόριθμο recommendation, τη ροή από query μέχρι WS broadcast.
Αναφέρσου στους περιορισμούς και μελλοντικές βελτιώσεις (ML).
Ελληνικά, ακαδημαϊκό ύφος.
```

---

### PROMPT 5.5: Frontend — VisualBoard & SecurityDashboard (~500 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 5.5 "Frontend: VisualBoard & SecurityDashboard"

VISUALBOARD (frontend/geo-ads-frontend/src/VisualBoard.js):
- 3 γρίλιες οθονών: GlassFloor (4×4), Surrounding (2×4), Megatron (2×2)
- Κάθε tile: χρωματίζεται ανάλογα με assigned ad
- Real-time updates μέσω /ws/placements WebSocket
- Click σε tile → λεπτομέρειες ad + εικόνα
- Auto-reconnect αν διακοπεί το WebSocket
- JWT token auto-refresh 2 λεπτά πριν λήξη

SECURITYDASHBOARD (frontend/geo-ads-frontend/src/SecurityDashboard.js):
4 panels:
1. Live Alerts: τελευταία alerts με severity badge (CRITICAL/WARNING/INFO)
2. Event Timeline: χρονολογική λίστα security events
3. Method Comparison: rule vs statistical — ποιος ανίχνευσε τι
4. Event Log: raw events με timestamps

- Real-time updates μέσω /ws/security WebSocket
- Πολύχρωμα severity indicators

TAB NAVIGATION (App.js):
Tab 1: "Stadium" → VisualBoard
Tab 2: "Security" → SecurityDashboard

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 5.5 (~500 λέξεις).
Περιέγραψε κάθε component, real-time behavior, UI αποφάσεις.
Αναφέρσου σε screenshots (Σχήμα 5.5a VisualBoard, Σχήμα 5.5b SecurityDashboard).
Σχολίασε το token auto-refresh mechanism.
Ελληνικά, ακαδημαϊκό ύφος.
```

---

### PROMPT 5.6: Desktop Εφαρμογή — Electron (~300 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 5.6 "Desktop Εφαρμογή (Electron)"

ΤΙ ΚΑΝΕΙ ΤΟ ELECTRON WRAPPER:
- Εκκινεί αυτόματα το FastAPI backend (subprocess)
- Εκκινεί το React frontend (npm start)
- Παρουσιάζει τα πάντα σε native desktop window
- Διαχειρίζεται processes lifecycle (cleanup on exit)
- Cross-platform: Windows, macOS, Linux

ΕΝΤΟΛΗ ΕΚΚΙΝΗΣΗΣ: npm run desktop
(στον φάκελο desktop/geo-ads-desktop/)

ΑΡΧΕΙΟ: desktop/geo-ads-desktop/ (Electron main process)

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 5.6 (~300 λέξεις).
Περιέγραψε τον σκοπό του Electron wrapper, τι επιλύει (dependency management, easy deployment).
Αναφέρσου στο build pipeline.
Σύγκρινε με εναλλακτικές (web-only, Docker, native app).
Ελληνικά, ακαδημαϊκό ύφος.
```

---

### PROMPT 5.7: Σύστημα Ασφάλειας — Υλοποίηση (~700 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 5.7 "Σύστημα Ασφάλειας — Υλοποίηση"

ΑΡΧΕΙΑ:
- backend/app/security/auth_config.py — secrets (crash αν JWT_SECRET < 32 bytes)
- backend/app/security/auth_routes.py — /auth/login, /auth/refresh, /auth/token
- backend/app/security/jwt_service.py — create/verify tokens
- backend/app/security/deps.py — require_scope() dependency
- backend/app/security/threat_engine.py — ThreatEngine singleton
- backend/app/security/message_schema.py — HMAC validation

ΚΡΙΣΙΜΕΣ ΥΛΟΠΟΙΗΣΕΙΣ:

1. JWT scopes (deps.py):
```python
def require_scope(scope: str):
    def dependency(token: str = Depends(oauth2_scheme)):
        payload = verify_token(token)
        if scope not in payload.get("scopes", []):
            raise HTTPException(403, "Insufficient scope")
        return payload
    return dependency
```

2. HMAC validation (message_schema.py):
Κάθε WS μήνυμα φέρει signature = HMAC-SHA256(secret, payload).
Server επαληθεύει πριν επεξεργαστεί.

3. Rate Limiting (slowapi):
@limiter.limit("10/minute") στο /auth/login
@limiter.limit("5/minute") στο /auth/token
→ 429 Too Many Requests αν υπερβεί

4. Threat Engine (threat_engine.py):
ThreatEngine singleton — process_event(event_type, ip, username):
  - Rule check: ελέγχει sliding counters per IP
  - Statistical check: Z-score σε event windows
  - Αποτελέσματα: list of ThreatAlert objects
  - WS broadcast: αν alert → push σε /ws/security

5. Security Headers (main.py middleware):
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 5.7 (~700 λέξεις).
Περιέγραψε κάθε επίπεδο ασφάλειας με κώδικα αποσπάσματα.
Αναφέρσου στις security headers και γιατί σημαντικές.
Εξήγησε το ThreatEngine singleton pattern.
Ελληνικά, ακαδημαϊκό ύφος.
```

---

## ΚΕΦΑΛΑΙΟ 6 — ΠΕΙΡΑΜΑΤΑ & ΑΞΙΟΛΟΓΗΣΗ

### PROMPT 6.1: Μεθοδολογία Πειραμάτων (~300 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 6.1 "Μεθοδολογία Πειραμάτων"

ΠΕΙΡΑΜΑΤΙΚΟ ΠΛΑΙΣΙΟ:
Hardware: Windows 10 Pro, τοπικό μηχάνημα (όχι production server)
Software: Python 3.11+, PostgreSQL 16, React 18
Benchmark tool: backend/tools/benchmark_all.py
Αριθμός επαναλήψεων: 1.000 per N value (warm-up: 100 πρώτες απορρίπτονται)
Metrics: μέση τιμή (ms), τυπική απόκλιση, speedup ratio
Dataset: N = {28, 100, 1.000, 10.000, 100.000} screens (τυχαίες GPS συντεταγμένες)
Ακτίνα query: 500m σταθερή

Threat Detection test: backend/tools/test_threat_detection.py
36 tests σε 8 κατηγορίες:
1. Authentication (login success/fail)
2. JWT validation
3. Rate limiting (429 detection)
4. Replay attack simulation
5. Brute force simulation
6. Credential stuffing simulation
7. Security API
8. WebSocket security

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 6.1 (~300 λέξεις).
Περιέγραψε: hardware, software, παραμέτρους, metrics, δικαιολόγησε 1.000 επαναλήψεις.
Ανάφερε τους περιορισμούς: τοπικό μηχάνημα, προσομοιωμένα GPS.
Ελληνικά, ακαδημαϊκό ύφος.
```

---

### PROMPT 6.2: Πείραμα 1 — Χωρική Ευρετηρίαση (~800 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 6.2 "Πείραμα 1: Σύγκριση Μεθόδων Χωρικής Ευρετηρίασης (ΕΡ-2)"

ΣΤΟΧΟΣ: Απάντηση στην ΕΡ-2: "Ποια μέθοδος χωρικής ευρετηρίασης είναι πιο αποδοτική;"

ΑΠΟΤΕΛΕΣΜΑΤΑ (χρησιμοποίησε ΑΚΡΙΒΩΣ αυτά τα νούμερα):
| N       | Linear (ms) | R-Tree (ms) | Distributed (ms) | Speedup R-Tree |
|---------|-------------|-------------|-----------------|---------------|
| 28      | 0.004       | 0.008       | 0.444           | 0.54x         |
| 100     | 0.018       | 0.012       | 0.435           | 1.45x         |
| 1.000   | 0.148       | 0.035       | 0.455           | 4.25x         |
| 10.000  | 1.475       | 0.200       | 0.616           | 7.36x         |
| 100.000 | 14.551      | 1.799       | 2.414           | 8.09x         |

ΕΡΜΗΝΕΙΑ ΑΠΟΤΕΛΕΣΜΑΤΩΝ:
- n=28: Linear 0.004ms < R-Tree 0.008ms → μικρό dataset, overhead R-Tree index > benefit
- n>100: R-Tree κερδίζει συνεχώς, speedup αυξάνει από 1.45x → 8.09x
- n=100.000: R-Tree 1.799ms vs Linear 14.551ms = 8.09x speedup
- Distributed: σταθερό overhead ~0.44ms (thread spawning Python GIL)
  → Για n=28: Distributed 0.444ms = 111x αργότερο από Linear!
  → Για n=100.000: Distributed 2.414ms — μεταξύ Linear και R-Tree
- Crossover point Linear→R-Tree: περίπου n=50-80 screens
- Θεωρητική εξήγηση: O(n) vs O(log n) → για n=100.000: log₂(100.000)≈17 βήματα vs 100.000

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 6.2 (~800 λέξεις), 4 sub-sections:
6.2.1 Στόχος (~100 λέξεις)
6.2.2 Μεθοδολογία (~150 λέξεις)
6.2.3 Αποτελέσματα (~200 λέξεις) — πίνακας + περιγραφή
6.2.4 Ανάλυση (~350 λέξεις) — ερμηνεία βάσει O(n) vs O(log n), crossover, distributed overhead

Αναφέρσου σε Σχήμα 6.1 (γραφήμα χρόνου vs N) και Σχήμα 6.2 (speedup vs N).
Απάντησε στην ΕΡ-2 στο τέλος.
Ελληνικά, ακαδημαϊκό ύφος.
```

---

### PROMPT 6.3: Πείραμα 2 — Ανίχνευση Απειλών (~700 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 6.3 "Πείραμα 2: Rule-based vs Statistical Threat Detection (ΕΡ-9)"

ΣΤΟΧΟΣ: Απάντηση στην ΕΡ-9: "Πώς ανιχνεύονται απειλές με υβριδική προσέγγιση;"

ΑΠΟΤΕΛΕΣΜΑΤΑ (χρησιμοποίησε ΑΚΡΙΒΩΣ):
- Rule avg detection time: ~0.014 ms
- Statistical avg detection time: ~0.013 ms
- Brute force (6 consecutive login fails): Rule ανιχνεύει (5/5min rule triggered)
- Credential stuffing (10+ unique usernames): Rule ανιχνεύει
- Replay attack (3+ replays): Rule ανιχνεύει
- Gradual anomaly (αύξηση rate): Statistical ανιχνεύει (z > 2.0), Rule miss
- Low-and-slow attack: Statistical ανιχνεύει, Rule miss (δεν φτάνει threshold)
- False positives: Statistical ~15% higher FP rate vs Rule
- Rule: 100% TP για known patterns, 0% για novel
- Statistical: ~85% TP, ~15% FP, ανιχνεύει novel attacks

ΚΑΝΟΝΕΣ (verbatim):
brute_force: 5+ auth_failed / 5min / same IP → CRITICAL
credential_stuffing: 10+ unique usernames / 10min → CRITICAL
replay_attack: 3+ replays / 5min → CRITICAL
rate_abuse: 20+ rate-limited / 10min → WARNING

STATISTICAL:
z = (rate - mean) / std
Alert if z > 2.0, windows: 5min, 15min, 1h
Warm-up: min 3 data points

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 6.3 (~700 λέξεις), 4 sub-sections:
6.3.1 Στόχος (~100 λέξεις)
6.3.2 Μεθοδολογία (~150 λέξεις) — test_threat_detection.py, κατηγορίες
6.3.3 Αποτελέσματα (~200 λέξεις) — πίνακας TP/FP, χρόνοι ανίχνευσης
6.3.4 Ανάλυση (~250 λέξεις) — πότε κερδίζει κάθε μέθοδος, συμπληρωματικότητα υβριδισμού

Απάντησε στην ΕΡ-9 στο τέλος.
Ελληνικά, ακαδημαϊκό ύφος.
```

---

### PROMPT 6.4: Συζήτηση Αποτελεσμάτων (~400 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 6.4 "Συζήτηση Αποτελεσμάτων"

ΑΠΟΤΕΛΕΣΜΑΤΑ ΣΥΝΟΨΗ:
Πείραμα 1: R-Tree βέλτιστο για production (8.09x speedup, O(log n))
            Linear αρκετό για n=28 (πραγματικό γήπεδο)
            Distributed: overhead κυριαρχεί σε single-machine υλοποίηση
Πείραμα 2: Υβριδισμός υπερέχει αμφότερων αυτόνομων μεθόδων
            Rule: deterministic, 0ms TP για known patterns
            Statistical: ανιχνεύει novel/gradual attacks που Rule miss

ΠΕΡΙΟΡΙΣΜΟΙ:
- Benchmark σε Windows (τοπικό) — δεν αντιπροσωπεύει production server
- n>100 screen είναι προσομοίωση (πραγματικό γήπεδο: n=28)
- Threat scenarios: ελεγχόμενα, δεν υπάρχει "real attacker"
- Statistical warm-up: χρειάζεται ≥3 data points

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 6.4 (~400 λέξεις).
Συνδύασε τα ευρήματα από τα 2 πειράματα.
Σχολίασε τους περιορισμούς και validity των αποτελεσμάτων.
Σχέση ευρημάτων με βιβλιογραφία (Κεφ. 2).
Ελληνικά, ακαδημαϊκό ύφος.
```

---

## ΚΕΦΑΛΑΙΟ 7 — ΣΥΜΠΕΡΑΣΜΑΤΑ & ΜΕΛΛΟΝΤΙΚΕΣ ΠΡΟΕΚΤΑΣΕΙΣ

### PROMPT 7.1: Ανακεφαλαίωση (~300 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 7.1 "Ανακεφαλαίωση"

ΤΙ ΥΛΟΠΟΙΗΘΗΚΕ:
- Ολοκληρωμένο real-time γεω-στοχευμένο σύστημα διαφήμισης (GEO-ADS)
- 3 ζώνες, 28 οθόνες, FastAPI + PostgreSQL/PostGIS + React + Electron
- 4 μέθοδοι χωρικής ευρετηρίασης (σύγκριση πειραματικά)
- 6 επίπεδα ασφάλειας (JWT + HMAC + Anti-Replay + RateLimit + AuditLog + ThreatEngine)
- Υβριδικό threat detection (rule-based + Z-score statistical)
- WebSocket real-time για placements + security alerts

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 7.1 (~300 λέξεις).
Σύντομη ανακεφαλαίωση τι επιτεύχθηκε, συνδέοντας με τους στόχους του Κεφ. 1.
Ελληνικά, ακαδημαϊκό ύφος.
```

---

### PROMPT 7.2: Απαντήσεις στις ΕΡ-1 έως ΕΡ-9 (~600 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 7.2 "Απαντήσεις στις Ερευνητικές Ερωτήσεις"

ΑΠΑΝΤΗΣΕΙΣ (χρησιμοποίησε ΑΚΡΙΒΩΣ):
ΕΡ-1: Οι 28 οθόνες οργανώνονται σε 3 ζώνες: GlassFloor (4×4), Surrounding (2×4), Megatron (2×2). Κάθε ζώνη έχει ξεχωριστό screen_type και GPS συντεταγμένες.
ΕΡ-2: Η R-Tree επιτυγχάνει 8.09x speedup έναντι Linear Scan για n=100.000 (1.799ms vs 14.551ms). Για n=28 (πραγματικό), η Linear είναι ταχύτερη (0.004ms vs 0.008ms).
ΕΡ-3: Proximity-based recommendation engine: βρίσκει screens εντός radius μέσω R-Tree, ταξινομεί κατά απόσταση, αναθέτει διαφημίσεις ανά zone affinity.
ΕΡ-4: WebSocket full-duplex (RFC 6455) με 3 channels (/ws/placements, /ws/layout, /ws/security) — <1ms latency για broadcasts.
ΕΡ-5: JWT Bearer (HS256, 6 scopes) για HTTP. WebSocket: JWT ως query parameter + HMAC-SHA256 message signing.
ΕΡ-6: Εικόνες αποθηκεύονται ως URL στη DB (advertisements.image_url). Frontend φορτώνει και εμφανίζει σε tile κατά assignment.
ΕΡ-7: PostgreSQL επιλέχθηκε για ACID εγγυήσεις, PostGIS extension (ST_DWithin, GIST index), και ωριμότητα για production.
ΕΡ-8: Electron wrapper εκκινεί FastAPI + React ως subprocess — all-in-one desktop executable χωρίς εξαρτήσεις εγκατάστασης.
ΕΡ-9: Υβριδικό σύστημα: Rule-based (4 κανόνες, ~0.014ms) για known attacks + Z-score statistical (z>2.0, sliding windows 5m/15m/1h, ~0.013ms) για novel attacks. Ο συνδυασμός καλύπτει αμφότερα.

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 7.2 (~600 λέξεις).
Παρουσίασε κάθε ΕΡ με σαφή, τεκμηριωμένη απάντηση.
Αναφέρσου στα πειραματικά αποτελέσματα για ΕΡ-2 και ΕΡ-9.
Ελληνικά, ακαδημαϊκό ύφος.
```

---

### PROMPT 7.3: Limitations (~300 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 7.3 "Περιορισμοί"

ΓΝΩΣΤΟΙ ΠΕΡΙΟΡΙΣΜΟΙ:
1. Placements in-memory: χάνονται κατά restart — δεν υπάρχει persistence στη DB
2. Benchmark σε τοπικό μηχάνημα (Windows 10) — αποτελέσματα μη αντιπροσωπευτικά production
3. Dataset n=28 (πραγματικό) — n>100 είναι τεχνητή προσομοίωση επεκτασιμότητας
4. Statistical detector χρειάζεται ≥3 data points warm-up — νωχελικός στην εκκίνηση
5. Χωρίς real GPS — συντεταγμένες προσομοιωμένες (mock data)
6. Χωρίς personalization — recommendation βασισμένο μόνο σε proximity
7. Single-instance deployment — δεν υποστηρίζει load balancing ή failover

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 7.3 (~300 λέξεις).
Ειλικρινής παρουσίαση όλων των limitations.
Εξήγησε γιατί κάθε limitation δεν αναιρεί τα ευρήματα.
Ελληνικά, ακαδημαϊκό ύφος.
```

---

### PROMPT 7.4: Μελλοντικές Προεκτάσεις (~400 λέξεις)

```
CONTEXT — GEO-ADS, υποενότητα 7.4 "Μελλοντικές Προεκτάσεις"

ΠΡΟΤΕΙΝΟΜΕΝΕΣ ΕΠΕΚΤΑΣΕΙΣ:
1. Persistence placements: αποθήκευση assignments στη PostgreSQL
2. ML Recommendation: χρήση collaborative filtering ή reinforcement learning
3. ML Threat Detection: αντικατάσταση Z-score με LSTM/Isolation Forest
4. Multi-venue: υποστήριξη πολλαπλών γηπέδων (multi-tenant αρχιτεκτονική)
5. Mobile app: React Native — εμφάνιση personalized ads σε smartphone θεατή
6. Real GPS integration: BLE beacons, WiFi positioning, UWB
7. Horizontal scaling: Redis pub/sub για WS broadcasting σε πολλαπλά instances
8. A/B Testing: σύγκριση αποδοτικότητας διαφορετικών ad strategies
9. Dashboard analytics: CTR (click-through rate), impressions, heatmaps

ΖΗΤΟΥΜΕΝΟ:
Γράψε υποενότητα 7.4 (~400 λέξεις).
Παρουσίασε τις προεκτάσεις ομαδοποιημένα (βραχυπρόθεσμες / μακροπρόθεσμες).
Αιτιολόγησε γιατί κάθε επέκταση είναι σημαντική.
Ελληνικά, ακαδημαϊκό ύφος.
```

---

## ΒΙΒΛΙΟΓΡΑΦΙΑ — Αιτήματα ανά Κεφάλαιο

### PROMPT BIB-2: Βιβλιογραφία Κεφ. 2

```
Ψάξε και μου δώσε 20-25 επιστημονικές αναφορές για τη βιβλιογραφία του Κεφαλαίου 2
της διπλωματικής μου για το GEO-ADS (real-time geo-targeted advertising, αθλητικές εγκαταστάσεις).

Κατηγορίες:
1. Digital advertising & geo-targeting (5 πηγές, 2019-2024)
2. Spatial indexing & R-Tree (5 πηγές, classic + modern)
3. WebSocket & real-time architectures (4 πηγές)
4. Web security: JWT, HMAC, OWASP (4 πηγές)
5. Anomaly detection & intrusion detection (5 πηγές, 2020-2024)

Μορφή κάθε αναφοράς:
[N] Συγγραφέας(ες). "Τίτλος." Περιοδικό/Συνέδριο, Χρονολογία. doi: https://doi.org/...

Σημείωσε ποιες είναι unavailable DOI (π.χ. RFC, books).
```

---

### PROMPT BIB-3: Βιβλιογραφία Κεφ. 3

```
Ψάξε και μου δώσε 15 επιστημονικές αναφορές για τη βιβλιογραφία του Κεφαλαίου 3
(Θεωρητικό Πλαίσιο) της διπλωματικής GEO-ADS.

Κατηγορίες:
1. Guttman R-Tree (1984) + R*-Tree + B-Tree + spatial complexity
2. WebSocket RFC 6455 + ASGI
3. JWT RFC 7519 + HMAC RFC 2104
4. Z-score anomaly detection, statistical methods, sliding windows

Μορφή: [N] Συγγραφέας. "Τίτλος." Περιοδικό, Χρονολογία. doi: ...
```

---

### PROMPT BIB-6: Βιβλιογραφία Κεφ. 6

```
Ψάξε 8-10 αναφορές για τη βιβλιογραφία του Κεφαλαίου 6 (Πειράματα & Αξιολόγηση):

1. Benchmark methodology για spatial databases
2. R-Tree performance evaluation papers
3. Intrusion detection system evaluation metrics (TP/FP/FN)
4. Statistical anomaly detection benchmarking

Μορφή: [N] Συγγραφέας. "Τίτλος." Περιοδικό, Χρονολογία. doi: ...
```

---

## EXTRA PROMPTS

### PROMPT E-1: Πίνακας Περιεχομένων

```
Βάσει της παρακάτω δομής διπλωματικής GEO-ADS, γράψε Πίνακα Περιεχομένων
στο μορφή Word/LaTeX (εκτιμώμενες σελίδες κάθε κεφαλαίου):

[ΕΠΙΚΟΛΛΑ ΤΗ ΔΟΜΗ ΑΠΟ MEMORY.MD ΚΕΦΑΛΑΙΑ 1-7]

Κάθε entry: Αριθμός κεφαλαίου | Τίτλος | Σελίδα (εκτιμώμενη)
Στόχος συνόλου: 100-120 σελίδες.
```

---

### PROMPT E-2: Ευρετήριο Εικόνων & Πινάκων

```
Δημιούργησε λίστα όλων των Σχημάτων και Πινάκων για τη διπλωματική GEO-ADS.
Βάσει αυτής της δομής:

Σχήμα 1.1: [Ζητείται — αρχιτεκτονική overview]
Σχήμα 3.1: [Ζητείται — R-Tree δομή με MBR]
Σχήμα 3.2: [Ζητείται — WebSocket handshake]
Σχήμα 4.1: [Ζητείται — System architecture diagram]
Σχήμα 4.2: [Ζητείται — Stadium zone layout]
Σχήμα 4.3: [Ζητείται — ER diagram]
Σχήμα 4.5: [Ζητείται — Auth flow diagram]
Σχήμα 5.5a: [Screenshot VisualBoard — θα παρασχεθεί]
Σχήμα 5.5b: [Screenshot SecurityDashboard — θα παρασχεθεί]
Σχήμα 6.1: [Ζητείται — Γράφημα χρόνου vs N]
Σχήμα 6.2: [Ζητείται — Speedup vs N]
Πίνακας 3.1: Σύγκριση πολυπλοκότητας χωρικών ευρετηρίων
Πίνακας 5.1: Τεχνολογίες & αιτιολόγηση
Πίνακας 6.1: Benchmark αποτελέσματα (ms)
Πίνακας 6.2: Threat detection αποτελέσματα

Για κάθε Σχήμα/Πίνακα: πρότεινε λεζάντα (15-20 λέξεις) ελληνικά.
```

---

*Τέλος αρχείου. Σύνολο prompts: 35+ (per section + bibliography + extras)*
*Χρήση: ένα prompt κάθε φορά στο ChatGPT.*
