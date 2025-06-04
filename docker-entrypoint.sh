#!/bin/sh
set -e 
echo "⏳ Waiting for PostgreSQL to be ready..."
while ! nc -z val-db 5432; do
  sleep 1
done
echo "✅ PostgreSQL is ready!"

echo "🔧 Initializing Flask-Migrate..."
flask db init

echo "⬆️  Applying database upgrade..."
flask db upgrade

echo "🚀 Starting application..."
exec "$@"