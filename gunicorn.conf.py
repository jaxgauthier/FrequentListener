"""Gunicorn settings — override via env: GUNICORN_WORKERS, GUNICORN_TIMEOUT."""

import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = int(os.environ.get('GUNICORN_WORKERS', '2'))
threads = int(os.environ.get('GUNICORN_THREADS', '4'))
timeout = int(os.environ.get('GUNICORN_TIMEOUT', '120'))
keepalive = 5
accesslog = '-'
errorlog = '-'
loglevel = os.environ.get('LOG_LEVEL', 'info').lower()
preload_app = False
