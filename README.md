# GEO-ADS

Real-time ad placement for a smart stadium, with the security layer I built on top of it for my diploma thesis at the University of Patras (graded 10/10).

![Backend](https://img.shields.io/badge/backend-FastAPI-green) ![DB](https://img.shields.io/badge/database-PostgreSQL%20%2B%20PostGIS-336791) ![Frontend](https://img.shields.io/badge/frontend-React-61DAFB) ![CI](https://github.com/mikedemis1/geo-ads-security-platform/actions/workflows/ci.yml/badge.svg)

## What it does

A stadium has three kinds of screen: a glass floor in the centre, banners around the perimeter, and a megatron. An ad request comes in with a position, the backend finds the best screen near that position, assigns the ad, and pushes the placement to every connected client over WebSocket.

The thesis had two questions. First, which spatial index answers "what is near this point" fastest: an R-Tree, a KD-Tree, a hashed grid, PostGIS, or a fan-out over simulated shards. Second, when the system is attacked, which detector notices first: fixed threshold rules or a Z-score anomaly detector. Both questions have live endpoints you can hit to see the numbers.

Everything in the security layer exists because the first version of this API was wide open: no login, no signing on the WebSocket, nothing recorded. The sections below describe what was added and, just as important, what it does not cover.

## Architecture

```
Electron desktop app  (wraps the React UI, starts the backend)
        |
React operator console  (VisualBoard, SecurityDashboard, Login)
        |  HTTP + WebSocket
FastAPI backend
   |-- spatial index engine   R-Tree, KD-Tree, grid, PostGIS, distributed
   |-- security layer         JWT scopes, rate limits, HMAC + anti-replay, threat engine
   |-- placement service      in-memory, broadcasts over WebSocket
        |
PostgreSQL 16 + PostGIS 3.4   (advertisements, screens with WGS-84 coordinates)
```

## Spatial index engine

Five ways to answer the same query, so they can be compared on the same data at `/benchmark/spatial`:

- **R-Tree** (`rtree`), the default for recommendations. Bounding-box query, then an exact circular check.
- **KD-Tree** (`scipy.spatial.KDTree`). Same complexity, different partitioning.
- **Grid**. The venue is split into fixed cells; a query touches only the cells that intersect the search box.
- **PostGIS `ST_DWithin`** with a GIST index, on real latitude and longitude, inside the database.
- **Distributed**. One shard per zone, each with its own R-Tree, queried in parallel and merged by distance. A MapReduce shape simulated in one process.

## Security layer

Several independent controls, each covering a different way in. The details, the threat model and the limits are in [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md); this is the short version.

**Authentication and scopes.** Every HTTP route except `/health` and `/` needs a Bearer JWT (HS256, issuer and audience pinned, expiry required). Tokens carry OAuth2-style scopes such as `ads:read`, `placements:write`, `security:read`. A token without the scope a route needs gets a 403 before the handler runs. `/auth/login` issues a one-hour access token and a 24-hour refresh token; `/auth/token` mints a token with chosen scopes for whoever holds the admin secret.

**Rate limiting.** Per source IP, with `slowapi`: 10 per minute on `/auth/login` and `/auth/refresh`, 5 per minute on `/auth/token`. A 429 is also recorded as a `rate_limited` security event so the detectors can correlate it.

**WebSocket handshake.** Every socket needs a JWT with the right scope on connect, or it is closed with 4401 (no or bad token) or 4403 (wrong scope).

**Message integrity and anti-replay.** Controller messages on `/ws/recommendation` are signed with HMAC-SHA256 over header plus payload and verified in constant time. Each message carries a timestamp and a nonce; anything older than 60 seconds, from the future, or with a nonce already seen is rejected. The hash can be switched to SHA3-256 with `CRYPTO_MODE` without touching the code.

**Threat detection.** Two detectors run on every security event:

| Detector | How it works | Catches |
|---|---|---|
| Rule-based | Per-IP counts inside a time window: 10 distinct usernames in 10 minutes, 5 failed logins in 5 minutes, 3 replays in 5 minutes, 20 rate-limit hits in 10 minutes | Credential stuffing, brute force, replay bursts, rate abuse |
| Statistical | Z-score of the current event rate against a rolling baseline over 5, 15 and 60 minute windows; alerts above 2 standard deviations | Bursts that match no rule |

Rules are fast and precise but only know the patterns you wrote down. The statistical path needs no rules and pays for that with false positives, including one right after startup that the tests document. `/security/comparison` shows detection counts and latency for both side by side.

**Headers, CORS, audit.** Every response carries `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, a Content-Security-Policy, `Referrer-Policy` and the legacy `X-XSS-Protection`. CORS is an explicit allow-list from `ALLOWED_ORIGINS`. Every request is written as one JSON line to `audit.log` with method, path, status, timing and the token subject.

## Tests

`backend/tests/` holds 65 tests over the security layer. They run against the real app without a database, because none of the routes they use touch PostgreSQL.

```
cd backend
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest
```

What they cover: token minting and every way a token can be wrong; missing, malformed and under-scoped bearer headers; the admin secret; refresh tokens used as access tokens; the sixth request in a minute; the security headers on success and error responses; WebSocket close codes; tampered, wrongly signed, replayed, stale and future-dated messages; SHA-2 versus SHA-3 signatures; both detectors; event eviction; that a refresh token is refused wherever an access token is expected, that a malformed zone id is rejected before it reaches the database, and that the app refuses to start without a database password or with a short JWT secret.

## What the tests found

Four things, and the order they were found in says something about how to look.

**A refresh token worked as an access token.** Both kinds are signed with the
same key and carry the same scopes; the `type` claim is the only thing that
separates them, and nothing was reading it. So a refresh token, valid for 24
hours, was accepted on every protected route and on the WebSocket handshake,
where an access token lasts one hour. Anyone holding one had a day of access
instead of an hour.

My own suite missed this. I had written the test for the direction I had thought
about — an access token presented at `/auth/refresh`, which was already
rejected — and never wrote the mirror image. It was found on 11 September 2026
by an independent review of this repository, and the fix is a single
`require_token_type` check applied everywhere a token is accepted. The
WebSocket test output is the clearest record of the bug: with a refresh token
the socket opened as `sub=admin`, the message signature verified, the replay
check passed, and the recommendation flow ran.

**Credential stuffing was hidden behind brute force.** Both rules watch failed
logins, the detector returns the first rule that matches, and brute force was
listed first with the lower threshold. Ten different usernames from one address
came back as brute force.

I first wrote that the stuffing rule "could never fire". That was wrong, and the
same review asked for proof. The two rules have different windows, five minutes
against ten, so a slow attacker whose recent rate had dropped below five still
reached the stuffing rule under the old order. What the old order actually broke
is the common case, because ten attempts inside ten minutes almost always put
five inside some five-minute window. Both shapes now have a test, including the
one that disproves the original claim.

**A null byte reached the database driver.** An authenticated ZAP scan driven by
the OpenAPI definition sent `zone_id=%00` to `/layout/postgis/near`. It travelled
through the service layer into psycopg2 and came back as a 500. Zone ids are
plain identifiers, so the shape is now pinned at the boundary and the request is
a 422.

**Two smaller ones.** The old README said login was limited to 5 requests a
minute; the code says 10. And a default database password sat in `config.py` and
in `docker-compose.yml`. Both now refuse to start without one, and a test guards
against it coming back.

## Scanners

Every push runs Semgrep (`p/python`, `p/security-audit`, `p/secrets`) and Bandit over the backend, blocking on any finding, and an OWASP ZAP baseline scan against the live API with a real PostGIS container. The ZAP job is informational; its findings and their triage are in [docs/security/zap-baseline.md](docs/security/zap-baseline.md). Bandit's first run found four places that swallowed exceptions silently; they now log a warning instead.

## API

| Method | Path | Scope |
|---|---|---|
| POST | `/auth/login` | none |
| POST | `/auth/refresh` | none |
| POST | `/auth/token` | admin secret header |
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
| GET | `/security/alerts`, `/security/events`, `/security/stats`, `/security/comparison` | `security:read` |
| WS | `/ws/placements` | JWT, `placements:read` |
| WS | `/ws/recommendation` | JWT, `recommendation:read`, HMAC, anti-replay |
| WS | `/ws/security` | JWT, `security:read` |

Interactive docs are at `http://localhost:8000/docs` when the backend is running.

## Stadium zones

| Zone | Grid | Screen type |
|---|---|---|
| GlassFloor | 4 x 4 | `glassfloor_tile` |
| Surrounding | 2 x 4 | `surrounding_banner` |
| Megatron | 2 x 2 | `megatron_panel` |

## Running it

You need Docker, Python 3.11 or newer, and Node 18 or newer.

1. Secrets. Copy `.env.example` to `.env` and `backend/.env.example` to `backend/.env`, then replace every `CHANGE_ME`. The database password must be the same in both. The app and Compose both refuse to start if anything required is missing.
2. Database: `docker compose up -d`
3. Backend: `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000`
4. Frontend: `cd frontend/geo-ads-frontend && npm install && npm start`, then open `http://localhost:3000`
5. Desktop, optional: `cd desktop/geo-ads-desktop && npm install && npm start`

## Limits

The short list; the full one is in the threat model.

- One shared HMAC secret for all controller nodes, and it is the same value as the admin token secret.
- HS256 means whoever can verify a token can also mint one.
- Refresh tokens cannot be revoked before they expire.
- Rate limits are per IP, so everyone behind one NAT shares a quota.
- Events, alerts, nonces and placements live in memory; a restart clears them and a second instance would not share them.
- The CSP allows `unsafe-inline`.
- No TLS in the app itself; it expects a reverse proxy on a private network.

## Stack

Python 3.11, FastAPI, Uvicorn, PyJWT, slowapi, rtree, scipy, psycopg2; PostgreSQL 16 with PostGIS 3.4 in Docker; React 19; Electron; pytest, Semgrep, Bandit, OWASP ZAP in GitHub Actions.
