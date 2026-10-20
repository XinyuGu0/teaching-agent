"""
Initialize database
Run this script to create database tables
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db

def init_db():
    """Initialize database"""
    app = create_app('development')

    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created successfully!")

        # Print table names
        print("\nCreated tables:")
        for table in db.metadata.sorted_tables:
            print(f"  - {table.name}")

if __name__ == '__main__':
    init_db()
