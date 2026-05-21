"""
Configuration management for the Audio Frequency Game
"""

import os
import logging
from datetime import timedelta
from logging.handlers import RotatingFileHandler
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_SQLITE_PATH = os.path.abspath(os.path.join(_PROJECT_ROOT, 'data', 'game.db'))
# Absolute path so SQLite works regardless of cwd (e.g. running scripts from scripts/)
_DEFAULT_SQLITE_URI = 'sqlite:///' + _DEFAULT_SQLITE_PATH.replace('\\', '/')


class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        # Railway uses postgres:// but SQLAlchemy expects postgresql://
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or _DEFAULT_SQLITE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    _PROJECT_AUDIO = os.path.join(_PROJECT_ROOT, 'audio')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(_PROJECT_AUDIO, 'uploads')
    AUDIO_OUTPUT_FOLDER = os.environ.get('AUDIO_OUTPUT_FOLDER') or os.path.join(
        _PROJECT_AUDIO, 'OutputWAVS'
    )
    
    # Spotify API Configuration
    SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    
    # Audio Processing Configuration
    AUDIO_SAMPLE_RATE = 44100
    AUDIO_DURATION = 10  # seconds
    FREQUENCY_LEVELS = [500, 1000, 1500, 2000, 2500, 3500, 5000, 7500]
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    
    # CDN Configuration
    CDN_URL = os.environ.get('CDN_URL')  # e.g., 'https://cdn.yourdomain.com'
    USE_CDN = os.environ.get('USE_CDN', 'False').lower() == 'true'
    
    # Static Asset Configuration
    STATIC_FOLDER = 'static'
    STATIC_URL_PATH = '/static'
    
    PORT = int(os.environ.get('PORT', 5001))

    # If set, the public game uses this Song.base_filename (folder under audio/OutputWAVS)
    # instead of whichever row has is_active=True. None = follow the database.
    FORCED_PLAYBACK_BASE_FILENAME = None
    
    @staticmethod
    def init_app(app):
        """Initialize application with logging configuration"""
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(Config.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configure logging
        if not app.debug and not app.testing:
            # File handler for production
            file_handler = RotatingFileHandler(
                Config.LOG_FILE, 
                maxBytes=10240000,  # 10MB
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
            app.logger.addHandler(file_handler)
            
            # Console handler for production
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s'
            ))
            app.logger.addHandler(console_handler)
            
            app.logger.setLevel(getattr(logging, Config.LOG_LEVEL))
            app.logger.info('Audio Frequency Game startup')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'
    # Follow DB is_active + dev_seed auto-pick. Override only via .env for debugging:
    FORCED_PLAYBACK_BASE_FILENAME = (
        os.environ.get('FORCE_PLAYBACK_BASE_FILENAME', '').strip() or None
    )
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        if not os.environ.get('SECRET_KEY'):
            app.logger.warning(
                'SECRET_KEY is not set; using insecure dev default. '
                'Set SECRET_KEY in .env before deploying.'
            )
        os.makedirs(os.path.join(_PROJECT_ROOT, 'data'), exist_ok=True)
        upload = app.config['UPLOAD_FOLDER']
        if not os.path.isabs(upload):
            upload = os.path.join(_PROJECT_ROOT, upload)
        os.makedirs(upload, exist_ok=True)
        os.makedirs(app.config['AUDIO_OUTPUT_FOLDER'], exist_ok=True)
        app.logger.info('Development mode enabled')

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'

    # Only use CDN when explicitly configured (see CDN_URL)
    USE_CDN = os.environ.get('USE_CDN', 'false').lower() == 'true'

    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'true').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    @classmethod
    def init_app(cls, app):
        secret = os.environ.get('SECRET_KEY', '').strip()
        if not secret or secret == 'dev-secret-key-change-in-production':
            raise ValueError(
                'SECRET_KEY must be set to a strong random value in production'
            )
        app.config['SECRET_KEY'] = secret

        uri = os.environ.get('DATABASE_URL')
        if not uri:
            raise ValueError("DATABASE_URL environment variable is required for production")
        if uri.startswith('postgres://'):
            uri = uri.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = uri

        upload = app.config['UPLOAD_FOLDER']
        if not os.path.isabs(upload):
            upload = os.path.join(_PROJECT_ROOT, upload)
            app.config['UPLOAD_FOLDER'] = upload
        audio_out = app.config['AUDIO_OUTPUT_FOLDER']
        if not os.path.isabs(audio_out):
            audio_out = os.path.join(_PROJECT_ROOT, audio_out)
            app.config['AUDIO_OUTPUT_FOLDER'] = audio_out

        os.makedirs(upload, exist_ok=True)
        os.makedirs(audio_out, exist_ok=True)
        log_dir = os.path.dirname(app.config.get('LOG_FILE') or '')
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        Config.init_app(app)

        # Production security headers
        @app.after_request
        def add_security_headers(response):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            return response

        app.logger.info('Production mode enabled')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    FORCED_PLAYBACK_BASE_FILENAME = None 