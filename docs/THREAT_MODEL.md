# Threat model

What GEO-ADS protects, who it protects it from, and where the protection stops. Written after the code, which is the wrong order, and it shows: several of the limits below were found by writing the tests in `backend/tests/`, not by design.

## What the system is

A FastAPI backend that decides which stadium screen shows which advertisement, a React operator console, and an Electron wrapper that runs both on one machine. Screens connect over WebSocket and receive placements in real time. One operator role exists. The whole thing runs on a stadium's internal network; nothing here was designed to face the public internet.

## Assets

1. **The placement decision.** If an attacker can assign ads, they control what a stadium full of people sees. This is the asset everything else exists for.
2. **The operator credentials and tokens.** Whoever holds them holds asset 1.
3. **The recommendation channel.** Signed WebSocket messages from controller nodes drive placements. A forged or replayed message is an indirect route to asset 1.
4. **The security event log and the audit log.** The record of who did what. Weakening it is how everything else goes unnoticed.
5. **Availability.** A stadium screen that shows nothing during a match is a failure even when nothing was stolen.

## Who the attacker is

- **Someone on the stadium network** with no credentials: a contractor's laptop, a compromised kiosk, a phone on the venue Wi-Fi if it is bridged. They can reach the API and the WebSocket endpoints and can see traffic if TLS is not terminated in front of the app.
- **Someone holding a captured message**: a recorded WebSocket frame they want to send again.
- **Someone holding a leaked token**: an access token copied from a log, a browser, or a screenshot.

Not modelled: a malicious operator, a compromised host running the backend, and supply-chain compromise of the Python or npm dependencies. These matter; they are simply outside what this project set out to test.

## Controls, and what each one stops

| Threat | Control | Where | Tested by |
|---|---|---|---|
| Calling the API without logging in | Bearer JWT required on every route except `/health` and `/` | `security/deps.py` | `test_http_auth.py` |
| Using a token for something it was not issued for | OAuth2-style scopes in the token, checked before the handler runs | `security/jwt_service.py` | `test_http_auth.py`, `test_jwt_service.py` |
| Forged or altered tokens | HS256 signature, issuer and audience pinned, required claims, expiry | `security/jwt_service.py` | `test_jwt_service.py` |
| Using a refresh token as an access token | `type` claim checked wherever a token is accepted | `security/jwt_service.py`, `security/deps.py`, `websockets/websockets.py` | `test_http_auth.py`, `test_ws_security.py` |
| Guessing the operator password | 10 login attempts per minute per IP, 5 token-mint attempts per minute per IP | `security/auth_routes.py` | `test_http_auth.py` |
| Opening a WebSocket without a token or with the wrong scope | JWT checked on the handshake, connection closed with 4401 or 4403 | `websockets/websockets.py` | `test_ws_security.py` |
| Tampering with a controller message in flight | HMAC-SHA256 (or SHA3-256) over header plus payload, constant-time compare | `security/message_schema.py`, `security/crypto_engine.py` | `test_ws_security.py` |
| Replaying a captured controller message | Timestamp window of 60 seconds plus a nonce store | `websockets/websockets.py` | `test_ws_security.py` |
| Brute force, credential stuffing, replay bursts, rate-limit abuse going unnoticed | Rule-based detector with per-IP thresholds | `security/threat_engine.py` | `test_threat_engine.py` |
| Novel bursts that match no rule | Z-score detector over 5, 15 and 60 minute windows | `security/threat_engine.py` | `test_threat_engine.py` |
| Clickjacking, MIME sniffing, referrer leakage | Security headers on every response | `main.py` | `test_http_auth.py` |
| Browser calls from unexpected origins | CORS allow-list from `ALLOWED_ORIGINS` | `main.py` | not tested |
| Losing the record of what happened | JSON audit line per request with the token subject | `main.py` | not tested |

## Limits

Stated here so nobody reads more into the controls than they deliver.

- **One shared HMAC secret for every controller node**, and it is the same value as the admin token secret. Any node can impersonate any other node, and leaking the admin secret also breaks message integrity. Per-node keys are the fix; they were out of scope for the thesis.
- **HS256 with a shared secret** means the verifier can also mint. Fine while one backend both issues and checks tokens. Not fine the day a second service needs to verify tokens; that day the answer is RS256 or ES256.
- **Refresh tokens cannot be revoked.** There is no server-side session store, so a leaked refresh token is valid for its full 24 hours.
- **Rate limits are per source IP.** Behind a proxy or NAT every client shares one address, so one noisy client can lock out everyone, and a client with many addresses gets many quotas.
- **All security state is in memory**: events, alerts, nonces, placements. A restart empties it, and a second backend instance would not share it. This is a single-process design.
- **The statistical detector alerts on cold start.** It seeds its baseline from the first three events it sees, all within the same burst, so the third failed login after startup raises an anomaly regardless of who sent it. This is the false-positive cost the thesis measured against the rule-based path. It is documented by `test_statistical_detector_alerts_on_cold_start_after_three_events` and left as designed.
- **The Content-Security-Policy allows `unsafe-inline`** for scripts and styles because the React build emits inline styles. It blunts most of what a CSP is for. A nonce-based policy is the fix.
- **No TLS in the application.** The app speaks plain HTTP and `ws://`. On the intended internal network a reverse proxy would terminate TLS; without one, tokens and HMAC secrets are visible to anyone who can capture traffic.
- **The audit log is a local file** with no integrity protection. Anyone who can write to the host can edit it.
- **The nonce store caps at 5,000 entries** and rejects new messages when full. That is a deliberate anti-flood choice, and it means an attacker who can send 5,000 valid messages in two minutes can deny service to real controllers.

## Findings, and where they came from

- **A refresh token was accepted as an access token.** `decode_and_verify` did
  not read the `type` claim and neither did `require_scope`, so a 24-hour
  refresh token passed as a bearer credential on every protected route and on
  the WebSocket handshake. Found on 2026-09-11 by an independent review, not by
  this project's own tests, which had only covered the opposite direction.
  Fixed with a `require_token_type` check at every point a token is accepted,
  and pinned by tests on both the HTTP and the WebSocket path.
- **Credential stuffing was masked by brute force.** Both rules watch
  `auth_failed`, the detector returns the first match, and brute force was
  listed first with the lower threshold. An earlier version of this document
  said the stuffing rule could never fire; that was too strong, and the same
  review asked for proof. Because the windows differ, five minutes against ten,
  a slow run whose recent rate had dropped below five did reach the stuffing
  rule even under the old order. The reorder fixes the common case. Both shapes
  have tests.
- **A null byte in `zone_id` reached psycopg2.** An authenticated ZAP API scan
  on 2026-09-11 returned a 500 from `/layout/postgis/near`. Zone ids are plain
  identifiers and the shape is now validated at the boundary, so the request is
  a 422 and nothing unusual travels inward.
- **Responses were cacheable.** The ZAP baseline flagged it; every non-static
  response now carries `Cache-Control: no-store`.
- **The README claimed a login rate limit of 5 per minute.** The code says 10.
  The README was wrong and now matches.
- **A default database password lived in `config.py` and `docker-compose.yml`.**
  Removed; both refuse to start without one, and a test guards it.

The pattern worth noticing: the tests I wrote myself found the detector bug,
because I was reasoning about the detector. The auth bypass and the null byte
were found by someone and something looking from outside, at the boundary rather
than at the logic. That is the argument for having both.
