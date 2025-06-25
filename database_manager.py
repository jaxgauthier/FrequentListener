#!/usr/bin/env python3
"""
Database Management Script for Audio Frequency Game
Handles database creation, migrations, and management operations.
"""

import sqlite3
import os
import sys
from datetime import datetime

def create_database():
    """Create the database with all necessary tables"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Create songs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            album TEXT,
            week INTEGER DEFAULT 1,
            upload_date DATE,
            has_frequency_versions BOOLEAN DEFAULT FALSE,
            base_filename TEXT,
            spotify_id TEXT,
            is_active BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # Create user_stats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            song_id INTEGER NOT NULL,
            guess_count INTEGER DEFAULT 0,
            correct_guess BOOLEAN DEFAULT FALSE,
            difficulty_level INTEGER DEFAULT 0,
            guessed_at TIMESTAMP,
            has_played BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (song_id) REFERENCES songs (id),
            UNIQUE(user_id, song_id)
        )
    ''')
    
    # Create song_stats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS song_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_id INTEGER NOT NULL,
            total_plays INTEGER DEFAULT 0,
            total_correct_guesses INTEGER DEFAULT 0,
            average_score REAL DEFAULT 0,
            points_distribution TEXT DEFAULT '{}',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (song_id) REFERENCES songs (id),
            UNIQUE(song_id)
        )
    ''')
    
    # Create admin_users table for secure admin access
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            is_super_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database created successfully!")

def create_admin_user(username, password, email=None, is_super_admin=False):
    """Create an admin user with secure password hashing"""
    import hashlib
    
    # Hash the password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO admin_users (username, password_hash, email, is_super_admin)
            VALUES (?, ?, ?, ?)
        ''', (username, password_hash, email, is_super_admin))
        
        conn.commit()
        print(f"✅ Admin user '{username}' created successfully!")
        
    except sqlite3.IntegrityError:
        print(f"❌ Admin user '{username}' already exists!")
    finally:
        conn.close()

def list_admin_users():
    """List all admin users"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT username, email, is_super_admin, created_at FROM admin_users')
    admins = cursor.fetchall()
    
    if admins:
        print("\n📋 Admin Users:")
        print("-" * 60)
        for admin in admins:
            username, email, is_super, created = admin
            admin_type = "Super Admin" if is_super else "Admin"
            print(f"👤 {username} ({admin_type})")
            if email:
                print(f"   📧 {email}")
            print(f"   📅 Created: {created}")
            print()
    else:
        print("❌ No admin users found!")
    
    conn.close()

def reset_database():
    """Reset the entire database (DANGEROUS - removes all data)"""
    if input("⚠️  This will delete ALL data! Type 'YES' to confirm: ") != "YES":
        print("❌ Database reset cancelled.")
        return
    
    # Remove the database file
    if os.path.exists('game.db'):
        os.remove('game.db')
        print("🗑️  Database file removed.")
    
    # Recreate the database
    create_database()
    print("✅ Database reset and recreated!")

def backup_database():
    """Create a backup of the database"""
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"game_backup_{timestamp}.db"
    
    if os.path.exists('game.db'):
        shutil.copy2('game.db', backup_filename)
        print(f"✅ Database backed up as: {backup_filename}")
    else:
        print("❌ No database file found to backup!")

def show_database_stats():
    """Show database statistics"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    # Count records in each table
    tables = ['users', 'songs', 'user_stats', 'song_stats', 'admin_users']
    stats = {}
    
    for table in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        stats[table] = count
    
    print("\n📊 Database Statistics:")
    print("-" * 30)
    print(f"👥 Users: {stats['users']}")
    print(f"🎵 Songs: {stats['songs']}")
    print(f"📈 User Stats: {stats['user_stats']}")
    print(f"📊 Song Stats: {stats['song_stats']}")
    print(f"🔐 Admin Users: {stats['admin_users']}")
    
    # Show active song
    cursor.execute('SELECT title, artist FROM songs WHERE is_active = 1')
    active_song = cursor.fetchone()
    if active_song:
        print(f"🎯 Active Song: {active_song[0]} by {active_song[1]}")
    else:
        print("🎯 Active Song: None")
    
    conn.close()

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("""
🗄️  Database Management Tool

Usage:
  python database_manager.py <command> [options]

Commands:
  create          - Create the database and tables
  create-admin    - Create an admin user (requires username and password)
  list-admins     - List all admin users
  backup          - Create a backup of the database
  reset           - Reset the entire database (DANGEROUS)
  stats           - Show database statistics

Examples:
  python database_manager.py create
  python database_manager.py create-admin admin mypassword123
  python database_manager.py list-admins
  python database_manager.py backup
  python database_manager.py stats
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == 'create':
        create_database()
    
    elif command == 'create-admin':
        if len(sys.argv) < 4:
            print("❌ Usage: python database_manager.py create-admin <username> <password>")
            return
        username = sys.argv[2]
        password = sys.argv[3]
        email = sys.argv[4] if len(sys.argv) > 4 else None
        create_admin_user(username, password, email, is_super_admin=True)
    
    elif command == 'list-admins':
        list_admin_users()
    
    elif command == 'backup':
        backup_database()
    
    elif command == 'reset':
        reset_database()
    
    elif command == 'stats':
        show_database_stats()
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == '__main__':
    main() 