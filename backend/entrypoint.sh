#!/bin/sh
set -e

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
MAX_RETRIES=60

echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."
retry=0
until nc -z "${DB_HOST}" "${DB_PORT}" 2>/dev/null; do
  retry=$((retry + 1))
  if [ "$retry" -ge "$MAX_RETRIES" ]; then
    echo "ERROR: PostgreSQL not available after ${MAX_RETRIES} retries. Exiting."
    exit 1
  fi
  sleep 0.5
done
echo "PostgreSQL is up."

echo "Running migrations..."
python manage.py migrate --noinput

if [ "${RUN_SEED:-0}" = "1" ]; then
  echo "Seeding catalog data (skips if already populated)..."
  python manage.py seed
fi

if [ "${DJANGO_SUPERUSER_USERNAME:-}" ]; then
  echo "Creating superuser if missing..."
  python manage.py createsuperuser --noinput || true
fi

echo "Starting Gunicorn on :8000..."
exec gunicorn qortex.wsgi:application --bind 0.0.0.0:8000 --workers "${GUNICORN_WORKERS:-3}"
