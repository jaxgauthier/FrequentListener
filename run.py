#!/usr/bin/env python3
"""
Main application entry point for the Audio Frequency Game
"""

import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()

def main():
    """Main application entry point"""
    # Create the Flask application
    app = create_app()
    
    # Get configuration from environment variables
    # Default :: so both http://localhost (often IPv6 ::1) and http://127.0.0.1 work on macOS.
    # Override with HOST=127.0.0.1 if your platform rejects ::.
    host = os.environ.get('HOST', '::')
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Starting Audio Frequency Game...")
    print(f"📍 Open in browser: http://127.0.0.1:{port}  or  http://localhost:{port}")
    print(f"   (listening on host {host!r} — keep this terminal open while testing)")
    print(f"🔧 Debug mode: {debug}")
    print(f"🌍 Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    # Run the application
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main() 