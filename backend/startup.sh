#!/bin/bash
set -e

echo "Running database migrations..."
python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()"

echo "Starting gunicorn server..."
exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 "app:create_app('production')"
