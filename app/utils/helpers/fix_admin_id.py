#!/usr/bin/env python3
"""
Script to fix admin user ID conflict and update JaxsonG05 password
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User, AdminUser
from werkzeug.security import generate_password_hash

def fix_admin_id():
    app = create_app()
    with app.app_context():
        print("=== Fixing Admin User ID Conflict ===")
        
        # Check current state
        regular_user = User.query.filter_by(username='JaxsonG05').first()
        admin_user = AdminUser.query.filter_by(username='admin').first()
        
        print(f"Regular user 'JaxsonG05': ID {regular_user.id if regular_user else 'Not found'}")
        print(f"Admin user 'admin': ID {admin_user.id if admin_user else 'Not found'}")
        
        # Change password for JaxsonG05
        if regular_user:
            regular_user.password_hash = generate_password_hash('Charlie702')
            db.session.commit()
            print("✅ Changed password for JaxsonG05 to 'Charlie702'")
        else:
            print("❌ Could not find user JaxsonG05 to change password")
        
        if regular_user and admin_user and regular_user.id == admin_user.id:
            print("⚠️  ID conflict detected! Both users have ID 1")
            
            # Delete the admin user
            db.session.delete(admin_user)
            db.session.commit()
            print("Deleted conflicting admin user")
            
            # Create new admin user with explicit ID
            new_admin = AdminUser(
                id=999,  # Use a high ID number to avoid conflicts
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('MadJax195')
            )
            db.session.add(new_admin)
            db.session.commit()
            
            print(f"✅ Created new admin user with ID {new_admin.id}")
            
            # Verify the fix
            regular_user = User.query.filter_by(username='JaxsonG05').first()
            admin_user = AdminUser.query.filter_by(username='admin').first()
            
            print(f"Regular user 'JaxsonG05': ID {regular_user.id}")
            print(f"Admin user 'admin': ID {admin_user.id}")
            
            if regular_user.id != admin_user.id:
                print("✅ ID conflict resolved!")
            else:
                print("❌ ID conflict still exists")
        else:
            print("✅ No ID conflict detected")

if __name__ == "__main__":
    fix_admin_id() 