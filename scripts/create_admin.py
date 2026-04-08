#!/usr/bin/env python3
"""
Script to create an admin user for the Audio Frequency Game
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from app.utils.dev_seed import (
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_USERNAME,
    ensure_admin_user,
    ensure_default_song_works,
)
from app import db

ADMIN_USERNAME = DEFAULT_ADMIN_USERNAME
ADMIN_PASSWORD = DEFAULT_ADMIN_PASSWORD
ADMIN_EMAIL = 'admin@example.com'

def create_admin():
    app = create_app()
    with app.app_context():
        ensure_admin_user()
        ensure_default_song_works()
        db.session.commit()
        print(f"Admin '{ADMIN_USERNAME}' ready with password '{ADMIN_PASSWORD}'.")

if __name__ == "__main__":
    create_admin() 