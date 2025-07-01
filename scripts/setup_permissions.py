#!/usr/bin/env python3
"""
File permission setup script for production deployment
"""

import os
import stat
import sys
from pathlib import Path

def setup_permissions():
    """Set proper file permissions for the application"""
    
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # Directories that need write permissions
    writable_dirs = [
        'data',  # Database directory
        'logs',  # Log files
        'audio/uploads',  # Audio uploads
        'app/static/css',  # Generated CSS
        'app/static/js',   # Generated JS
    ]
    
    # Files that should be executable
    executable_files = [
        'run.py',
        'scripts/migrate_db.py',
        'scripts/build_assets.py',
        'scripts/setup_permissions.py',
    ]
    
    print("🔧 Setting up file permissions...")
    
    # Set directory permissions
    for dir_path in writable_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            # Set 755 permissions (rwxr-xr-x) for directories
            os.chmod(full_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
            print(f"✅ Set permissions for directory: {dir_path}")
        else:
            # Create directory if it doesn't exist
            full_path.mkdir(parents=True, exist_ok=True)
            os.chmod(full_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
            print(f"✅ Created and set permissions for directory: {dir_path}")
    
    # Set file permissions
    for file_path in executable_files:
        full_path = project_root / file_path
        if full_path.exists():
            # Set 755 permissions (rwxr-xr-x) for executable files
            os.chmod(full_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
            print(f"✅ Set permissions for file: {file_path}")
    
    # Set specific permissions for sensitive files
    sensitive_files = [
        '.env',
        'data/game.db',
    ]
    
    for file_path in sensitive_files:
        full_path = project_root / file_path
        if full_path.exists():
            # Set 600 permissions (rw-------) for sensitive files
            os.chmod(full_path, stat.S_IRUSR | stat.S_IWUSR)
            print(f"🔒 Set secure permissions for sensitive file: {file_path}")
    
    print("🎉 File permissions setup completed!")

def check_permissions():
    """Check current file permissions"""
    project_root = Path(__file__).parent.parent
    
    print("🔍 Checking file permissions...")
    
    # Check key directories
    dirs_to_check = ['data', 'logs', 'audio/uploads']
    for dir_path in dirs_to_check:
        full_path = project_root / dir_path
        if full_path.exists():
            mode = os.stat(full_path).st_mode
            permissions = stat.filemode(mode)
            print(f"📁 {dir_path}: {permissions}")
        else:
            print(f"❌ {dir_path}: Directory does not exist")
    
    # Check key files
    files_to_check = ['run.py', '.env', 'data/game.db']
    for file_path in files_to_check:
        full_path = project_root / file_path
        if full_path.exists():
            mode = os.stat(full_path).st_mode
            permissions = stat.filemode(mode)
            print(f"📄 {file_path}: {permissions}")
        else:
            print(f"❌ {file_path}: File does not exist")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        check_permissions()
    else:
        setup_permissions() 