#!/bin/sh
set -e

echo "Waiting for PostgreSQL at ${DB_HOST:-db}:${DB_PORT:-5432}..."
until nc -z "${DB_HOST:-db}" "${DB_PORT:-5432}" 2>/dev/null; do
  sleep 0.5
done
echo "PostgreSQL is up."

echo "Running migrations..."
python manage.py migrate --noinput

if [ "${RUN_SEED:-0}" = "1" ]; then
  echo "Seeding catalog data..."
  python manage.py seed
fi

if [ "${DJANGO_SUPERUSER_USERNAME:-}" ]; then
  echo "Creating superuser if missing..."
  python manage.py createsuperuser --noinput || true
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn on :8000..."
exec gunicorn qortex.wsgi:application --bind 0.0.0.0:8000 --workers 3
