"""
Asset helper utilities for templates
"""

from flask import current_app, url_for

def get_cdn_url(filename):
    """Get CDN URL for a static file if CDN is configured"""
    if (hasattr(current_app, 'config') and 
        current_app.config.get('USE_CDN') and 
        current_app.config.get('CDN_URL')):
        return f"{current_app.config['CDN_URL']}/{filename}"
    return url_for('static', filename=filename)

def get_css_assets(bundle_name=None):
    """
    Get CSS assets for templates
    Args:
        bundle_name: Specific bundle name or None for all CSS
    """
    if hasattr(current_app, 'assets') and current_app.assets: # type: ignore
        # Use Flask-Assets bundles
        if bundle_name:
            return current_app.assets[bundle_name].urls() # type: ignore
        else:
            return current_app.assets['css_all'].urls() # type: ignore
    else:
        # Fallback to individual files
        if bundle_name == 'auth_css':
            return [get_cdn_url('css/auth.css')]
        elif bundle_name == 'user_css':
            return [get_cdn_url('css/user.css')]
        elif bundle_name == 'admin_css':
            return [get_cdn_url('css/admin.css')]
        else:
            # Return all CSS files
            return [
                get_cdn_url('css/auth.css'),
                get_cdn_url('css/user.css'),
                get_cdn_url('css/profile.css'),
                get_cdn_url('css/admin.css')
            ]

def get_js_assets(bundle_name=None):
    """
    Get JavaScript assets for templates
    Args:
        bundle_name: Specific bundle name or None for all JS
    """
    if hasattr(current_app, 'assets') and current_app.assets: # type: ignore
        # Use Flask-Assets bundles
        if bundle_name:
            return current_app.assets[bundle_name].urls() # type: ignore
        else:
            return current_app.assets['js_all'].urls() # type: ignore
    else:
        # Fallback to individual files
        if bundle_name == 'user_js':
            return [get_cdn_url('js/user.js')]
        elif bundle_name == 'admin_js':
            return [
                get_cdn_url('js/admin.js'),
                get_cdn_url('js/admin_auth.js')
            ]
        else:
            # Return all JS files
            return [
                get_cdn_url('js/auth.js'),
                get_cdn_url('js/admin_auth.js'),
                get_cdn_url('js/user.js'),
                get_cdn_url('js/admin.js')
            ]

def get_audio_url(song_name, frequency):
    """Get CDN URL for audio files"""
    filename = f"audio/OutputWAVS/{song_name}/reconstructed_audio_{frequency}.wav"
    return get_cdn_url(filename) 