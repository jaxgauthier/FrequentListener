#!/usr/bin/env python3
"""
Script to create an admin user for the Audio Frequency Game
"""

from app import create_app, db
from app.models.user import AdminUser
from werkzeug.security import generate_password_hash

ADMIN_USERNAME = 'admin'
ADMIN_EMAIL = 'admin@example.com'
ADMIN_PASSWORD = 'MadJax195'

def create_admin():
    app = create_app()
    with app.app_context():
        admin_user = AdminUser.query.filter_by(username=ADMIN_USERNAME).first()
        if admin_user:
            print(f"Admin user '{ADMIN_USERNAME}' already exists.")
        else:
            admin_user = AdminUser(
                username=ADMIN_USERNAME, # type: ignore
                email=ADMIN_EMAIL, # type: ignore
                password_hash=generate_password_hash(ADMIN_PASSWORD) # type: ignore
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"Admin user '{ADMIN_USERNAME}' created with password '{ADMIN_PASSWORD}'.")

if __name__ == "__main__":
    create_admin() 