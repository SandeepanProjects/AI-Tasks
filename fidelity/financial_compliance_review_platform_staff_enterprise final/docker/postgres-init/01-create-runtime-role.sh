#!/bin/sh
set -eu
: "${APP_DB_PASSWORD:=app_local}"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  -v app_password="$APP_DB_PASSWORD" <<'SQL'
CREATE ROLE app_user LOGIN PASSWORD :'app_password' NOSUPERUSER NOBYPASSRLS;
GRANT CONNECT, TEMPORARY ON DATABASE compliance TO app_user;
GRANT USAGE, CREATE ON SCHEMA public TO app_user;
CREATE EXTENSION IF NOT EXISTS vector;
SQL
