#!/bin/sh

echo "⏳ Waiting for PostgreSQL to be ready..."
while ! nc -z val-db 5432; do
  sleep 1
done
echo "✅ PostgreSQL is ready!"

# Initialiser Flask-Migrate seulement si le dossier migrations n'existe pas
if [ ! -d "migrations" ]; then
    echo "🔧 Initializing Flask-Migrate..."
    flask db init
else
    echo "✅ Flask-Migrate already initialized"
fi

echo "🔄 Generating migration..."
flask db migrate -m "Auto migration" || echo "⚠️  No changes detected for migration"

echo "⬆️  Applying database upgrade..."
flask db upgrade

echo "👤 Creating admin user..."

export PGPASSWORD="${POSTGRES_PASSWORD:-val}"
psql -h val-db -U "${POSTGRES_USER:-val}" -d "${POSTGRES_DB:-val}" -f /app/sql/init-admin.sql

echo "🚀 Starting application..."
exec "$@"