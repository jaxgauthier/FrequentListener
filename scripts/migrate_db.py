#!/usr/bin/env python3
"""
Database migration script for the Audio Frequency Game
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import User, Song, UserStats, SongStats, SongHistory, UserPlayerState

def migrate_database():
    """Create all database tables"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        from app.utils.db_upgrade import ensure_schema_upgrades

        ensure_schema_upgrades()
        print("Database tables created successfully!")
        
        from app.utils.dev_seed import ensure_admin_user

        ensure_admin_user()
        db.session.commit()
        print("Admin user ready (password from ADMIN_PASSWORD in .env)")

if __name__ == '__main__':
    migrate_database() 