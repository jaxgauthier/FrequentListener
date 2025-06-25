import sqlite3
import os
from datetime import datetime

def create_database():
    """Create the SQLite database and tables for the audio frequency game"""
    
    # Database file path (in project root)
    db_path = 'game.db'
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create songs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            album TEXT,
            week INTEGER DEFAULT 1,
            upload_date TEXT,
            filename TEXT,
            has_frequency_versions BOOLEAN DEFAULT 0,
            base_filename TEXT,
            spotify_id TEXT,
            is_active BOOLEAN DEFAULT 0
        )
    ''')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_login TEXT,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Create user_stats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            song_id INTEGER NOT NULL,
            guess_count INTEGER DEFAULT 0,
            correct_guess BOOLEAN DEFAULT 0,
            difficulty_level INTEGER DEFAULT 0,
            time_taken_seconds INTEGER,
            guessed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            has_played BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (song_id) REFERENCES songs (id)
        )
    ''')
    
    # Create song_stats table for global song statistics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS song_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_id INTEGER NOT NULL,
            total_plays INTEGER DEFAULT 0,
            total_correct_guesses INTEGER DEFAULT 0,
            average_score REAL DEFAULT 0,
            points_distribution TEXT DEFAULT '{}',
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (song_id) REFERENCES songs (id)
        )
    ''')
    
    # Create user_sessions table for remembering users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create game_sessions table (for tracking gameplay)
    cursor.execute('''
        CREATE TABLE game_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            song_id INTEGER,
            difficulty_reached INTEGER DEFAULT 0,
            correct_guess BOOLEAN,
            guess_count INTEGER DEFAULT 0,
            play_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (song_id) REFERENCES songs (id)
        )
    ''')
    
    # Create guesses table (for tracking individual guesses)
    cursor.execute('''
        CREATE TABLE guesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            guess_text TEXT NOT NULL,
            is_correct BOOLEAN,
            guess_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES game_sessions (id)
        )
    ''')
    
    # Insert some sample songs (your existing songs)
    sample_songs = [
        ('Mr. Brightside', 'The Killers', 'MrBrightside', 'spotify:track:003vvx7Niy0FvhfD6s05FG'),
        ('Ghost Town', 'Kanye West', 'GhostTown', 'spotify:track:2Y2nW8P3w9zXe3bYa8osR6'),
        ('Milan', 'Unknown Artist', 'Milan', None),
        ('Teenage Dirtbag', 'Wheatus', 'TeenageDirtbag', 'spotify:track:25jUc9aTzTbjuM5CaymEAA'),
        ('Bohemian Rhapsody', 'Queen', 'Queen_BohemianRhapsody', 'spotify:track:3z8h0TU7ReDPLIbEnYhWZb'),
        ('Free Bird', 'Lynyrd Skynyrd', 'LynyrdSkynyrd_FreeBird', 'spotify:track:5EWPGh7jbTNO2WDvFjRYoJ'),
        ('Somebody That I Used to Know', 'Gotye', 'Gotye_SomebodyThatIUsedToKnow', 'spotify:track:4C0UfhGTdrL3cjH4O2HcVx'),
        ('AREWESTILLFRIENDS', 'Tyler, The Creator', 'TylerTheCreator_AREWESTILLFRIENDS', 'spotify:track:5xrcs8pl0MCLg4F9IYj5Hd')
    ]
    
    cursor.executemany('''
        INSERT INTO songs (title, artist, base_filename, spotify_id)
        VALUES (?, ?, ?, ?)
    ''', sample_songs)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"✅ Database created successfully: {db_path}")
    print("📊 Tables created:")
    print("   - songs (stores song information)")
    print("   - users (for future user accounts)")
    print("   - user_stats (tracks user stats with has_played flag)")
    print("   - song_stats (tracks global song statistics)")
    print("   - user_sessions (remembers user sessions)")
    print("   - game_sessions (tracks gameplay)")
    print("   - guesses (tracks individual guesses)")
    print(f"🎵 Added {len(sample_songs)} sample songs")

if __name__ == "__main__":
    create_database() 