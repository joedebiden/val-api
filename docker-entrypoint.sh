#!/bin/sh

echo "Waiting for database..."
sleep 5

flask db init

echo "Applying migrations..."
flask db migrate

echo "Applying upgrade..."
flask db upgrade

echo "Creating admin user"
psql -h val-db -U val -d val -f /home/app/sql/init-admin.sql

exec "$@"