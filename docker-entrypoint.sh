#!/bin/sh
set -e 
echo "⏳ Waiting for PostgreSQL to be ready..."
while ! nc -z val-db 5432; do
  sleep 5
done
echo "✅ PostgreSQL is ready!"
sleep 2

# check if db already init 
# start the compose without migrations 
if [ ! -d "/app/migrations" ]; then
  echo "❎ No migrations found, starting the first process..."
  echo "🔧 Initializing Flask-Migrate..."
  flask db init
  echo "🏎️ Create migration..."
  flask db migrate
  echo "⬆️ Applying database upgrade..."
  flask db upgrade
  echo "🚀 Starting application..."
  exec "$@"
else 
  echo "✅ Migrations directory already exists, skipping initialization."
  echo "🚀 Starting application..."
  exec "$@"
fi



