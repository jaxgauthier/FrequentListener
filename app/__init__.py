"""
Audio Frequency Game - Flask Application Factory
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development').strip().lower() or 'development'
    
    if config_name == 'production':
        config_class = 'app.config.ProductionConfig'
    elif config_name == 'testing':
        config_class = 'app.config.TestingConfig'
    else:
        config_class = 'app.config.DevelopmentConfig'
    
    app.config.from_object(config_class)
    
    # Initialize configuration with logging
    if config_name == 'production':
        from app.config import ProductionConfig
        ProductionConfig.init_app(app)
    elif config_name == 'development':
        from app.config import DevelopmentConfig
        DevelopmentConfig.init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Initialize asset management
    try:
        from app.assets import init_assets
        assets = init_assets(app)
        app.assets = assets
    except ImportError:
        # Flask-Assets not installed, skip asset management
        app.assets = None 
    
    # Configure Flask-Login
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main.bp)
    
    # User loader for Flask-Login
    from app.models import User, AdminUser
    
    @login_manager.user_loader
    def load_user(user_id):
        """Resolve Flask-Login session id (regular ids vs admin:{id})."""
        if user_id is None:
            return None
        s = str(user_id)
        if s.startswith('admin:'):
            pk = int(s[6:], 10)
            return AdminUser.query.get(pk)
        return User.query.get(int(s, 10))

    if config_name == 'development':
        with app.app_context():
            try:
                from sqlalchemy import inspect
                if inspect(db.engine).has_table('songs'):
                    from app.utils.dev_seed import ensure_default_song_works
                    ensure_default_song_works()
                    db.session.commit()
            except Exception as exc:
                app.logger.warning('Default song setup skipped: %s', exc)
    
    return app 