#!/usr/bin/env bash
# Generates the two .env files if they are missing, then hands over to
# docker compose. Nothing else: compose owns the startup order and the health
# checks. Stop everything with `docker compose down`.
#
# Secrets are generated per clone instead of shipped in the repository, which
# is why this wrapper exists at all. Run it again any time; it will not
# overwrite an .env that is already there.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

rand_hex() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex 32
  else
    python3 -c "import secrets; print(secrets.token_hex(32))"
  fi
}

if [ ! -f .env ]; then
  echo "Generating .env"
  echo "POSTGRES_PASSWORD=$(rand_hex)" > .env
fi

DB_PASS="$(grep '^POSTGRES_PASSWORD=' .env | cut -d= -f2-)"

if [ ! -f backend/.env ]; then
  ADMIN_PASS="$(rand_hex | cut -c1-24)"
  echo "Generating backend/.env"
  cat > backend/.env <<EOF
JWT_SECRET=$(rand_hex)
ADMIN_TOKEN_SECRET=$(rand_hex)
ADMIN_USER=admin
ADMIN_PASS=${ADMIN_PASS}
DB_PASSWORD=${DB_PASS}
DB_NAME=geo_ads
DB_USER=geo_ads_user
JWT_ISSUER=geo-ads
JWT_AUDIENCE=geo-ads-ui
JWT_DEFAULT_TTL_SECONDS=3600
REFRESH_TOKEN_TTL_SECONDS=86400
CRYPTO_MODE=HMAC_SHA256
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:8080
EOF
  echo "Admin login: admin / ${ADMIN_PASS}"
  echo "It is also in backend/.env, which is gitignored."
fi

BACKEND_DB_PASS="$(grep '^DB_PASSWORD=' backend/.env | cut -d= -f2-)"
if [ "$BACKEND_DB_PASS" != "$DB_PASS" ]; then
  cat >&2 <<EOF
POSTGRES_PASSWORD in .env and DB_PASSWORD in backend/.env are different.
The database is created with the first and the backend authenticates with the
second, so the backend will fail to connect.

Make them equal, or delete both files and re-run this script to generate a
matching pair. Deleting them means the existing database volume no longer
matches either, so also run: docker compose down -v
EOF
  exit 1
fi

exec docker compose up --build "$@"
