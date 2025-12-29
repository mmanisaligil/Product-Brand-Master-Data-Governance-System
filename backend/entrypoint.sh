#!/bin/sh
set -e

echo "Starting migrations..."
if ! alembic upgrade head; then
  echo "ERROR: Alembic migrations failed."
  exit 1
fi
echo "Migrations complete."

echo "Seeding data..."
if ! python -m app.seed; then
  echo "ERROR: Seed data failed."
  exit 1
fi
echo "Seed data complete."

echo "Starting API on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
