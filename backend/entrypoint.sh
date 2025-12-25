#!/bin/bash
set -e

echo "Waiting for database to be ready..."
sleep 5

echo "Running database migrations..."
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

echo "Seeding database with demo data..."
python seed.py

echo "Starting Flask application..."
exec python run.py
