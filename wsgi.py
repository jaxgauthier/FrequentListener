"""
WSGI entrypoint for production (gunicorn, Render, Railway, Fly, etc.).

  gunicorn -c gunicorn.conf.py wsgi:app
"""

import os

from dotenv import load_dotenv

load_dotenv()

from app import create_app

app = create_app()

if os.environ.get('FLASK_ENV', '').strip().lower() == 'production':
    from werkzeug.middleware.proxy_fix import ProxyFix

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
