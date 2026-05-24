# GEO-ADS — Real-Time Geo-Targeted Ad Management System

<div align="center">

![Type](https://img.shields.io/badge/Type-Diploma%20Thesis-blue?style=for-the-badge)
![Backend](https://img.shields.io/badge/Backend-FastAPI-green?style=for-the-badge&logo=fastapi)
![DB](https://img.shields.io/badge/Database-PostgreSQL%20%2B%20PostGIS-336791?style=for-the-badge&logo=postgresql)
![Frontend](https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react)
![Desktop](https://img.shields.io/badge/Desktop-Electron-47848F?style=for-the-badge&logo=electron)

</div>

---

## Project Overview

GEO-ADS is a real-time advertisement management system built for a smart stadium environment. The idea is to automatically assign ads to the right screen at the right time based on spatial proximity — using multiple indexing strategies and comparing their performance.

The stadium has three screen zones: a glass floor, surrounding perimeter banners, and a megatron. The system receives ad requests, finds the best matching screen using spatial queries, assigns the ad, and broadcasts the placement live to all connected clients via WebSocket.

On top of the core placement logic, the system includes a full security layer: JWT authentication with fine-grained scopes, rate limiting, HMAC-signed WebSocket messages with anti-replay protection, and a hybrid threat detection engine that runs rule-based and statistical (Z-score) detectors in parallel.

### What This Project Covers

- Spatial indexing with R-Tree, KD-Tree, Grid, PostGIS GIST, and a Distributed (MapReduce-style) index
- Real-time ad placement via spatial recommendation + WebSocket broadcast
- JWT authentication with OAuth2-style scopes for both HTTP and WebSocket
- Hybrid threat detection: rule-based thresholds vs. Z-score statistical anomaly detection
- Audit logging of every HTTP request with timing and user identity
- Live benchmark endpoint comparing all spatial index methods head-to-head
- React frontend with a visual board, login page, and security dashboard
- Electron desktop wrapper that runs the whole system locally

---

## Architecture

```
                    ┌──────────────────────────────────┐
                    │        Electron Desktop App       │
                    │  (wraps React UI + starts backend)│
                    └───────────────┬──────────────────┘
                                    │
                    ┌───────────────▼──────────────────┐
                    │          React Frontend           │
                    │  VisualBoard / SecurityDashboard  │
                    └───────────────┬──────────────────┘
                               HTTP │ WebSocket
                    ┌───────────────▼──────────────────┐
                    │          FastAPI Backend          │
                    │                                  │
                    │  ┌──────────────────────────┐    │
                    │  │   Spatial Index Engine   │    │
                    │  │  R-Tree · KD-Tree · Grid │    │
                    │  │  PostGIS · Distributed   │    │
                    │  └──────────────────────────┘    │
                    │                                  │
                    │  ┌──────────────────────────┐    │
                    │  │      Security Layer      │    │
                    │  │  JWT · Rate Limit · HMAC │    │
                    │  │  ThreatEngine(Rule+Zscore)│   │
                    │  └──────────────────────────┘    │
                    │                                  │
                    │  ┌──────────────────────────┐    │
                    │  │    Placement Service     │    │
                    │  │ in-memory · WS broadcast │    │
                    │  └──────────────────────────┘    │
                    └───────────────┬──────────────────┘
                                    │
                    ┌───────────────▼──────────────────┐
                    │      PostgreSQL + PostGIS         │
                    │   advertisements · screens        │
                    └──────────────────────────────────┘
```

---

## Components

```
Core Placement          (Completed)
         ↓
Spatial Index Engine    (Completed)
         ↓
JWT Auth + WS Security  (Completed)
         ↓
Threat Detection Engine (Completed)
         ↓
React UI + Electron     (Completed)
```

---

## Core Placement

### `placement_service.py`
In-memory ad assignment engine. Receives a spatial recommendation (screen + zone), creates a placement record, and triggers a WebSocket broadcast so all connected clients see the new assignment in real time.

### `websockets.py`
WebSocket manager that handles client connections and broadcasts `placement_assigned` events. All WS connections require a signed JWT token validated on handshake.

---

## Spatial Index Engine

Five indexing strategies are implemented and can be benchmarked live via `/benchmark/spatial`.

### R-Tree (`rtree` library)
In-memory spatial index. O(log n) range queries. Used as the default for ad screen recommendation.

### KD-Tree (`scipy.spatial.KDTree`)
Alternative in-memory index. Efficient for nearest-neighbour lookups in low-dimensional space.

### Grid Index
The venue is divided into fixed-size cells. Queries check only the relevant cells — O(1) cell lookup, then linear scan within the cell.

### PostGIS GIST (`ST_DWithin`)
Database-level spatial query using a GIST index on WGS-84 coordinates. Comparable to the R-Tree but runs inside PostgreSQL.

### Distributed Index (MapReduce simulation)
Simulates a distributed system by partitioning screens across virtual nodes and fanning out queries in parallel. Results are merged and deduplicated.

---

## Security Layer

### JWT Authentication
All HTTP endpoints and WebSocket connections require a Bearer token. Tokens carry fine-grained scopes (`ads:read`, `placements:write`, `security:read`, etc.). The `/auth/token` endpoint issues access + refresh tokens.

### Rate Limiting
Login endpoint and sensitive routes are rate-limited via `slowapi`. Rate-limit violations are automatically forwarded to the threat engine as events.

### HMAC + Anti-Replay (WebSocket)
Each WS message is signed with HMAC-SHA256. The server validates the signature and rejects replayed messages using a timestamp + nonce window.

### Threat Detection Engine (`threat_engine.py`)
A hybrid detector running two strategies in parallel on every security event:

| Strategy | Method | Trigger |
|----------|--------|---------|
| Rule-Based | Fixed thresholds per IP per time window | `auth_failed ≥ 5 / 60s` → brute_force alert |
| Statistical | Z-score on rolling event rate | Rate deviates > 2σ from baseline → anomaly alert |

Both detectors process the same event stream. The `/security/comparison` endpoint exposes a side-by-side comparison of which detector fired and how fast.

### Audit Log
Every HTTP request is logged as a JSON line to `audit.log`: timestamp, method, path, authenticated user, status code, and response time in ms.

---

## API Endpoints

| Method | Path | Scope |
|--------|------|-------|
| POST | `/auth/token` | — |
| GET | `/advertisements` | `ads:read` |
| GET | `/advertisements/zone/{zone_id}` | `ads:read` |
| GET | `/layout` | `layout:read` |
| GET | `/layout/query/near` | `layout:read` |
| GET | `/layout/postgis/near` | `layout:read` |
| GET | `/layout/distributed/near` | `layout:read` |
| GET | `/layout/recommendation/screen` | `recommendation:read` |
| GET | `/benchmark/spatial` | `layout:read` |
| GET | `/placements` | `placements:read` |
| POST | `/placements/recommend_and_assign/advertisements/{id}` | `placements:write` |
| GET | `/security/alerts` | `security:read` |
| GET | `/security/events` | `security:read` |
| GET | `/security/comparison` | `security:read` |
| WS | `/ws/placements` | JWT required |
| WS | `/ws/recommendation` | JWT + HMAC + Anti-Replay |

---

## Stadium Zones

| Zone | Grid | Screen Type |
|------|------|-------------|
| GlassFloor | 4 × 4 | `glassfloor_tile` |
| Surrounding | 2 × 4 | `surrounding_banner` |
| Megatron | 2 × 2 | `megatron_panel` |

---

## How to Run

**Prerequisites:** Docker, Python 3.11+, Node.js 18+

**1. Start the database**

```bash
docker-compose up -d
```

**2. Set up environment**

```bash
cp backend/.env.example backend/.env
# Edit backend/.env — set a real JWT_SECRET
```

**3. Run the backend**

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs at `http://localhost:8000/docs`

**4. Run the frontend**

```bash
cd frontend/geo-ads-frontend
npm install
npm start
```

Frontend at `http://localhost:3000`

**5. (Optional) Run the desktop app**

```bash
cd desktop/geo-ads-desktop
npm install
npm start
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, Uvicorn |
| Spatial | rtree, scipy, PostGIS ST_DWithin |
| Auth | PyJWT, slowapi |
| Database | PostgreSQL 16 + PostGIS 3.4 (Docker) |
| Frontend | React 18 |
| Desktop | Electron |
| Infrastructure | Docker, Docker Compose |
