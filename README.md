# GEO-ADS — Σύστημα Στοχευμένων Διαφημίσεων Γηπέδου

Διπλωματική εργασία — Μιχάλης Δεμής (ΑΜ 1080958)  
Πανεπιστήμιο Πατρών, Τμήμα Ηλεκτρολόγων Μηχανικών & Τεχνολογίας Υπολογιστών

---

## Τι είναι

Real-time σύστημα διαχείρισης και προβολής στοχευμένων διαφημίσεων σε αθλητικές εγκαταστάσεις.  
Υποστηρίζει τρεις ζώνες οθονών (GlassFloor, Surrounding, Megatron) με πολυδιάστατο σύστημα ευρετηρίασης, recommendation engine, και πλήρες επίπεδο ασφάλειας.

---

## Αρχιτεκτονική

| Στρώμα | Τεχνολογία |
|---|---|
| Backend | FastAPI + uvicorn (Python 3.11+) |
| Database | PostgreSQL 16 (Docker Compose) |
| Frontend | React 18 (VisualBoard SPA) |
| Desktop | Electron (auto-start backend + load UI) |
| Real-time | WebSockets (FastAPI native) |
| Security | JWT + HMAC + Anti-Replay + Rate Limiting + Audit Log |

---

## Ζώνες Γηπέδου

| Ζώνη | Grid | Οθόνες | Screen Type |
|---|---|---|---|
| GlassFloor | 4×4 | 16 tiles | glassfloor_tile |
| Surrounding | 2×4 | 8 banners | surrounding_banner |
| Megatron | 2×2 | 4 panels | megatron_panel |

---

## Setup

### 1. Database
```bash
docker-compose up -d
cd backend && python tools/db_check.py
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend
```bash
cd frontend/geo-ads-frontend
npm install && npm start
```

### 4. Desktop (all-in-one)
```bash
cd desktop/geo-ads-desktop
npm install && npm run desktop
```

---

## Security

| Layer | Μηχανισμός |
|---|---|
| HTTP Auth | JWT Bearer tokens (HS256, scoped) |
| WS Auth | JWT via query param → close 4401/4403 |
| WS Integrity | HMAC-SHA256 signed messages (CryptoEngine) |
| Anti-Replay | Timestamp window 60s + nonce deduplication |
| Rate Limiting | 5 req/min on POST /auth/token (slowapi) |
| Audit Logging | JSON middleware → audit.log |
| Crypto Agility | SHA-256 / SHA3-256 via CRYPTO_MODE env var |

---

## API Endpoints

| Method | Path | Scope |
|---|---|---|
| GET | /health | — |
| GET | /advertisements | ads:read |
| GET | /advertisements/zone/{zone_id} | ads:read |
| GET | /layout | layout:read |
| GET | /layout/zones/{zone_id}/screens | layout:read |
| GET | /layout/query/near | layout:read |
| GET | /layout/multiindex | layout:read |
| GET | /layout/recommendation/screen | recommendation:read |
| GET | /recommendation/advertisements/{ad_id}/screen | recommendation:read |
| GET | /placements | placements:read |
| POST | /placements/recommend_and_assign/advertisements/{ad_id} | placements:write |
| POST | /auth/token | X-Admin-Secret header |
| WS | /ws/ads | ads:read |
| WS | /ws/placements | placements:read |
| WS | /ws/recommendation | JWT + HMAC + Anti-Replay |
| WS | /ws/recommendation-simple | JWT only (React frontend) |

---

## Acceptance Tests

```bash
cd backend

# 1. Database
python tools/db_check.py

# 2. JWT WS auth (4401/4403/200)
python tools/ws_proof_v1.py

# 3. WS recommendation-simple (plain JSON + JWT)
python tools/ws_proof_v1b_simple.py

# 4. HMAC message signing
python tools/ws_proof_v2.py

# 5. Anti-replay protection
python tools/ws_proof_v3.py

# 6. Rate limiting (PowerShell)
.\tools\test_ratelimit.ps1

# 7. REST auth
python tools/test_auth_rest.py
```

---

## Environment Variables

Βλ. `backend/.env.example`