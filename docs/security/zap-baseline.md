# OWASP ZAP results

Two scans, both run on 2026-09-11 against the API on `localhost:8000` with the database up, using the `zaproxy/zap-stable` image. Raw JSON reports sit next to this file. The same baseline runs in CI on every push (`.github/workflows/ci.yml`, job `dast`), informational, with the triage below encoded in `.zap/rules.tsv`.

## Baseline scan (passive, unauthenticated)

`zap-baseline.py -t http://host.docker.internal:8000`

Result: 0 failures, 2 warnings, 65 rules passed. The baseline has no credentials and nothing to spider, so it only saw `/`, `/robots.txt` and `/sitemap.xml`. Every data route answers 401 without a token, which is the point, but it also means this scan says little about the API itself. That is what the API scan below is for.

| Rule | Where | Verdict |
|---|---|---|
| 10049 Storable and Cacheable Content | `/`, `/robots.txt`, `/sitemap.xml` | **Fixed.** Every non-static response now carries `Cache-Control: no-store`. Tokens and security events must not sit in a browser or proxy cache. `test_api_responses_are_not_cacheable` guards it. The ad images under `/static/` stay cacheable on purpose. |
| 90004 Cross-Origin-Resource-Policy missing | `/` | **Accepted.** The React console on port 3000 and the Electron app (a `file://` origin) load ad images from `/static/` cross-origin. A `same-site` or `same-origin` policy would make Chromium block those images. The right fix is a nonce-based CSP plus CORP on everything except `/static/`, and that is out of scope here. |

## API scan (OpenAPI-driven, active)

See the section appended below once the run completes. If it is missing, the run did not complete and nothing is claimed for it.
