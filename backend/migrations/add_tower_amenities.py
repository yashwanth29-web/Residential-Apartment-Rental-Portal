"""
Database migration script to create tower_amenities association table.
Run this script to add the many-to-many relationship between towers and amenities.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text


def create_tower_amenities_table():
    """Create tower_amenities association table."""
    app = create_app()
    with app.app_context():
        try:
            # Check if table already exists
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'tower_amenities'
            """))
            if result.fetchone():
                print("Table 'tower_amenities' already exists.")
                return
            
            # Create the association table
            db.session.execute(text("""
                CREATE TABLE tower_amenities (
                    tower_id INTEGER NOT NULL REFERENCES towers(id) ON DELETE CASCADE,
                    amenity_id INTEGER NOT NULL REFERENCES amenities(id) ON DELETE CASCADE,
                    PRIMARY KEY (tower_id, amenity_id)
                )
            """))
            db.session.commit()
            print("Table 'tower_amenities' created successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating table: {e}")
            # Try using SQLAlchemy's create_all as fallback
            try:
                db.create_all()
                print("Tables created using SQLAlchemy create_all()")
            except Exception as e2:
                print(f"Fallback also failed: {e2}")


if __name__ == '__main__':
    create_tower_amenities_table()
