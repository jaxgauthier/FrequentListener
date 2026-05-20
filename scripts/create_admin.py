#!/usr/bin/env python3
"""
Script to create an admin user for the Audio Frequency Game
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv(project_root / '.env')

from app import create_app, db
from app.utils.dev_seed import DEFAULT_ADMIN_USERNAME, ensure_admin_user, ensure_default_song_works, get_admin_password


def create_admin():
    app = create_app()
    with app.app_context():
        ensure_admin_user()
        ensure_default_song_works()
        db.session.commit()
        print(f"Admin '{DEFAULT_ADMIN_USERNAME}' ready.")
        print(f"  Password synced from ADMIN_PASSWORD in .env")
        print(f"  Login at: http://127.0.0.1:{app.config.get('PORT', 5001)}/admin/login")

if __name__ == "__main__":
    create_admin() 