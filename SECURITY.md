# Security

This is a diploma-thesis project, not a supported product. It is public so the design and the tests can be read, and so the limits are on record.

## Reporting

If you find something, open a GitHub issue with the steps to reproduce. There is no bounty and no SLA. The known limits are listed in [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md); please read that before reporting one of them.

## What is checked on every push

- `pytest` over the security layer: JWT, scopes, rate limiting, WebSocket auth, HMAC, anti-replay, both detectors.
- Semgrep (`p/python`, `p/security-audit`, `p/secrets`) and Bandit over `backend/app`, blocking on any finding.
- An OWASP ZAP baseline scan against the running API, informational.

## Secrets

No secret is committed. The app refuses to start without `JWT_SECRET`, `ADMIN_TOKEN_SECRET`, `ADMIN_USER`, `ADMIN_PASS` and `DB_PASSWORD`, and Docker Compose refuses to start the database without `POSTGRES_PASSWORD`. Copy the two `.env.example` files and fill them in.
