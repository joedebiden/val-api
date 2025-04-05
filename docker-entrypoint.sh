#!/bin/bash

echo "Waiting for database..."
sleep 5

falsk db upgrade

# Only generate new migrations if explicitly requested
if [ "$GENERATE_MIGRATIONS" = "true" ]; then
    flask db migrate -m "Auto-generated migration"
    flask db upgrade
fi

exec "$@"