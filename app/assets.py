"""
Static asset management for the Audio Frequency Game
"""

from flask_assets import Environment, Bundle

def init_assets(app):
    """Initialize Flask-Assets with CSS and JS bundles"""
    assets = Environment(app)
    
    # Configure asset output directory
    assets.url = app.static_url_path
    assets.directory = app.static_folder
    
    # CSS Bundles
    css_bundle = Bundle(
        'css/auth.css',
        'css/user.css',
        'css/profile.css',
        'css/admin.css',
        filters='cssmin',
        output='css/bundle.min.css'
    )
    assets.register('css_all', css_bundle)
    
    # JavaScript Bundles
    js_bundle = Bundle(
        'js/auth.js',
        'js/admin_auth.js',
        'js/user.js',
        'js/admin.js',
        filters='jsmin',
        output='js/bundle.min.js'
    )
    assets.register('js_all', js_bundle)
    
    # Individual bundles for specific pages
    auth_css = Bundle(
        'css/auth.css',
        filters='cssmin',
        output='css/auth.min.css'
    )
    assets.register('auth_css', auth_css)
    
    user_css = Bundle(
        'css/user.css',
        filters='cssmin',
        output='css/user.min.css'
    )
    assets.register('user_css', user_css)
    
    admin_css = Bundle(
        'css/admin.css',
        filters='cssmin',
        output='css/admin.min.css'
    )
    assets.register('admin_css', admin_css)
    
    user_js = Bundle(
        'js/user.js',
        filters='jsmin',
        output='js/user.min.js'
    )
    assets.register('user_js', user_js)
    
    admin_js = Bundle(
        'js/admin.js',
        'js/admin_auth.js',
        filters='jsmin',
        output='js/admin.min.js'
    )
    assets.register('admin_js', admin_js)
    
    return assets 