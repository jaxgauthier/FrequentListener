#!/usr/bin/env python3
"""
Asset build script for production deployment
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def build_assets():
    """Build and minify static assets"""
    try:
        from app import create_app
        from flask_assets import Environment, Bundle
        
        app = create_app('production')
        
        with app.app_context():
            # Initialize assets
            assets = Environment(app)
            assets.url = app.static_url_path
            assets.directory = app.static_folder
            
            # Define and register bundles
            css_bundle = Bundle(
                'css/auth.css',
                'css/user.css', 
                'css/profile.css',
                'css/admin.css',
                filters='cssmin',
                output='css/bundle.min.css'
            )
            assets.register('css_bundle', css_bundle)
            
            js_bundle = Bundle(
                'js/auth.js',
                'js/admin_auth.js',
                'js/user.js',
                'js/admin.js',
                filters='jsmin',
                output='js/bundle.min.js'
            )
            assets.register('js_bundle', js_bundle)
            
            # Build bundles
            print("Building CSS bundle...")
            assets['css_bundle'].build()
            print("✅ CSS bundle built successfully")
            
            print("Building JavaScript bundle...")
            assets['js_bundle'].build()
            print("✅ JavaScript bundle built successfully")
            
            # Get file sizes
            static_folder = app.static_folder or 'app/static'
            css_path = os.path.join(static_folder, 'css', 'bundle.min.css')
            js_path = os.path.join(static_folder, 'js', 'bundle.min.js')
            
            if os.path.exists(css_path):
                css_size = os.path.getsize(css_path) / 1024  # KB
                print(f"📦 CSS bundle size: {css_size:.1f} KB")
            
            if os.path.exists(js_path):
                js_size = os.path.getsize(js_path) / 1024  # KB
                print(f"📦 JS bundle size: {js_size:.1f} KB")
            
            print("🎉 Asset build completed successfully!")
            
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Please install Flask-Assets: pip install Flask-Assets cssmin jsmin")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error building assets: {e}")
        sys.exit(1)

def clean_assets():
    """Clean built asset files"""
    static_dir = Path(__file__).parent.parent / 'app' / 'static'
    
    files_to_remove = [
        'css/bundle.min.css',
        'js/bundle.min.js',
        'css/auth.min.css',
        'css/user.min.css', 
        'css/admin.min.css',
        'js/user.min.js',
        'js/admin.min.js'
    ]
    
    for file_path in files_to_remove:
        full_path = static_dir / file_path
        if full_path.exists():
            full_path.unlink()
            print(f"🗑️  Removed {file_path}")
    
    print("🧹 Asset cleanup completed!")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'clean':
        clean_assets()
    else:
        build_assets() 