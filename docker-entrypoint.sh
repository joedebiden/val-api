#!/bin/bash

echo "Waiting for database..."
sleep 5

if [ ! -d "/home/app/migrations/versions" ] || [ -z "$(ls -A /home/app/migrations/versions)" ]; then
  echo "Initializing migrations..."
  flask db init
  flask db migrate -m "Initial migration"
fi

echo "Applying migrations..."
flask db upgrade

# Only generate new migrations if explicitly requested
if [ "$GENERATE_MIGRATIONS" = "true" ]; then
    flask db migrate -m "Auto-generated migration"
    flask db upgrade
fi

echo "Creating admin user"
psql -h val-db -U val -d val -f /home/app/sql/init-admin.sql

exec "$@"