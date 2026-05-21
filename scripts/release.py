#!/usr/bin/env python3
"""
Run on each deploy (Render releaseCommand, Railway pre-deploy, manual).

  FLASK_ENV=production DATABASE_URL=... ADMIN_PASSWORD=... python scripts/release.py
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app, db


def main():
    if not os.environ.get('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'production'

    app = create_app()

    with app.app_context():
        print('Running release: create tables + ensure admin user...')
        db.create_all()

        from app.utils.db_upgrade import ensure_schema_upgrades

        ensure_schema_upgrades()

        from app.utils.dev_seed import ensure_admin_user

        ensure_admin_user()
        db.session.commit()
        print('Release complete.')


if __name__ == '__main__':
    main()
