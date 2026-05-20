#!/usr/bin/env python3
"""
One-off helper: resolve admin vs regular user ID conflicts.

Does not set hardcoded passwords. After running, reset passwords via:
  ADMIN_PASSWORD=... python scripts/create_admin.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import create_app, db
from app.models.user import User, AdminUser
from app.utils.dev_seed import DEFAULT_ADMIN_USERNAME, ensure_admin_user


def fix_admin_id():
    app = create_app()
    with app.app_context():
        print("=== Fixing Admin User ID Conflict ===")

        regular_user = User.query.filter_by(username='JaxsonG05').first()
        admin_user = AdminUser.query.filter_by(username=DEFAULT_ADMIN_USERNAME).first()

        print(
            f"Regular user 'JaxsonG05': ID {regular_user.id if regular_user else 'Not found'}"
        )
        print(
            f"Admin user '{DEFAULT_ADMIN_USERNAME}': "
            f"ID {admin_user.id if admin_user else 'Not found'}"
        )

        if regular_user and admin_user and regular_user.id == admin_user.id:
            print("ID conflict detected — recreating admin user with a new ID")
            db.session.delete(admin_user)
            db.session.commit()
            ensure_admin_user()
            db.session.commit()
            admin_user = AdminUser.query.filter_by(username=DEFAULT_ADMIN_USERNAME).first()
            print(f"New admin user ID: {admin_user.id if admin_user else 'failed'}")
        else:
            print("No ID conflict — ensuring admin user exists")
            ensure_admin_user()
            db.session.commit()

        print("Done. Set ADMIN_PASSWORD in .env and run: python scripts/create_admin.py")


if __name__ == "__main__":
    fix_admin_id()
