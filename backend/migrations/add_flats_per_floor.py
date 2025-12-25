"""
Database migration script to add flats_per_floor column to towers table.
Run this script to add the new column to existing databases.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text


def add_flats_per_floor_column():
    """Add flats_per_floor column to towers table."""
    app = create_app()
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'towers' AND column_name = 'flats_per_floor'
            """))
            if result.fetchone():
                print("Column 'flats_per_floor' already exists in towers table.")
                return
            
            # Add the column with default value
            db.session.execute(text("""
                ALTER TABLE towers 
                ADD COLUMN flats_per_floor INTEGER NOT NULL DEFAULT 4
            """))
            db.session.commit()
            print("Column 'flats_per_floor' added successfully to towers table!")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding column: {e}")
            # Try alternative approach for SQLite
            try:
                db.session.execute(text("""
                    ALTER TABLE towers ADD COLUMN flats_per_floor INTEGER DEFAULT 4
                """))
                db.session.commit()
                print("Column 'flats_per_floor' added successfully to towers table!")
            except Exception as e2:
                print(f"Alternative approach also failed: {e2}")


if __name__ == '__main__':
    add_flats_per_floor_column()
