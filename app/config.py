"""
Configuration management for the Audio Frequency Game
"""

import os
import logging
from datetime import timedelta
from logging.handlers import RotatingFileHandler
from urllib.parse import urlparse

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        # Railway uses postgres:// but SQLAlchemy expects postgresql://
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///data/game.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'audio/uploads'
    AUDIO_OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'audio', 'OutputWAVS')
    
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
    
    # Railway Configuration
    PORT = int(os.environ.get('PORT', 5001))
    
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
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        # Development-specific logging
        app.logger.info('Development mode enabled')

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Production-specific settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is required for production")
    
    # Enable CDN in production if configured
    USE_CDN = os.environ.get('USE_CDN', 'True').lower() == 'true'
    
    @classmethod
    def init_app(cls, app):
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