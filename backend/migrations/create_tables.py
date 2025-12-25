"""
Database migration script to create all tables.
Run this script to initialize the database schema.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Tower, Flat, Amenity, Booking, Lease


def create_tables():
    """Create all database tables."""
    app = create_app()
    with app.app_context():
        db.create_all()
        print("All tables created successfully!")


def drop_tables():
    """Drop all database tables."""
    app = create_app()
    with app.app_context():
        db.drop_all()
        print("All tables dropped successfully!")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--drop':
        drop_tables()
    else:
        create_tables()
