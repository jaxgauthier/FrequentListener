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
        print("Database tables created successfully!")
        
        # Check if admin user exists
        from app.models import AdminUser
        admin_user = AdminUser.query.filter_by(username='admin').first()
        if not admin_user:
            print("Creating admin user...")
            admin_user = AdminUser(
                username='admin',
                email='admin@example.com'
            )
            admin_user.set_password('MadJax195')
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists.")

if __name__ == '__main__':
    migrate_database() 