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
        CREATE TABLE songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            base_filename TEXT UNIQUE NOT NULL,
            spotify_id TEXT,
            week INTEGER DEFAULT 1,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            available_frequencies TEXT DEFAULT '[]'
        )
    ''')
    
    # Create users table (for future user accounts)
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
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
    print("   - game_sessions (tracks gameplay)")
    print("   - guesses (tracks individual guesses)")
    print(f"🎵 Added {len(sample_songs)} sample songs")

if __name__ == "__main__":
    create_database() 