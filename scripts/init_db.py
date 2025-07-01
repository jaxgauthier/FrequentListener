#!/usr/bin/env python3
"""
Database initialization script for the Audio Frequency Game
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import User, AdminUser, Song, UserStats, SongStats
from app.models.song import SongQueue, SongHistory

def init_database():
    """Initialize the database with tables and default data"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully")
        
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        print("✅ Data directory created")
        
        # Create audio directories
        audio_dir = Path("audio")
        uploads_dir = audio_dir / "uploads"
        output_dir = audio_dir / "OutputWAVS"
        
        audio_dir.mkdir(exist_ok=True)
        uploads_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)
        print("✅ Audio directories created")
        
        print("\n🎉 Database initialization complete!")
        print("\nNext steps:")
        print("1. Create an admin user: python scripts/create_admin.py")
        print("2. Set up environment variables in .env file")
        print("3. Run the application: python run.py")

if __name__ == "__main__":
    init_database() 