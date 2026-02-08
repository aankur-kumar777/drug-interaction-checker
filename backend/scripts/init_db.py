#!/usr/bin/env python3
"""
Database initialization script
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine
from app.models.database import Base
from app.utils.config import settings

def init_database():
    """Initialize the database with all tables"""
    print("🗄️  Initializing database...")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Create all tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database initialized successfully!")
    print(f"Tables created: {', '.join(Base.metadata.tables.keys())}")

if __name__ == "__main__":
    init_database()
