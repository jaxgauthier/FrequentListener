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
        config_name = os.environ.get('FLASK_ENV', 'development')
    
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
        """Load user for Flask-Login - checks both regular users and admin users"""
        print(f"Loading user with ID: {user_id}")
        
        # First try to find a regular user
        user = User.query.get(int(user_id))
        if user:
            print(f"Found regular user: {user.username} (type: {type(user)})")
            return user
        
        # If not found, try to find an admin user
        admin_user = AdminUser.query.get(int(user_id))
        if admin_user:
            print(f"Found admin user: {admin_user.username} (type: {type(admin_user)})")
        else:
            print(f"No user found with ID: {user_id}")
        return admin_user
    
    # Railway-specific: Serve static files with whitenoise in production
    if config_name == 'production':
        try:
            from whitenoise import WhiteNoise
            app.wsgi_app = WhiteNoise(app.wsgi_app, root='app/static/')
            app.wsgi_app.add_files('app/static/', prefix='static/')
        except ImportError:
            app.logger.warning("WhiteNoise not available, using default static file serving")
    
    return app 