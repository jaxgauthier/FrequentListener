import sqlite3
import json

def migrate_database():
    """Migrate existing database to add new columns and tables"""
    
    db_path = 'game.db'
    
    if not os.path.exists(db_path):
        print("Database not found. Please run create_database.py first.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add has_played column to user_stats table if it doesn't exist
        cursor.execute("PRAGMA table_info(user_stats)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'has_played' not in columns:
            print("Adding has_played column to user_stats table...")
            cursor.execute('ALTER TABLE user_stats ADD COLUMN has_played BOOLEAN DEFAULT 0')
            print("✅ Added has_played column")
        else:
            print("✅ has_played column already exists")
        
        # Create song_stats table if it doesn't exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='song_stats'")
        if not cursor.fetchone():
            print("Creating song_stats table...")
            cursor.execute('''
                CREATE TABLE song_stats (
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
            print("✅ Created song_stats table")
        else:
            print("✅ song_stats table already exists")
        
        # Initialize song_stats for existing songs
        print("Initializing song_stats for existing songs...")
        songs = cursor.execute('SELECT id FROM songs').fetchall()
        for song in songs:
            song_id = song[0]
            
            # Check if song_stats already exists for this song
            existing = cursor.execute('SELECT id FROM song_stats WHERE song_id = ?', (song_id,)).fetchone()
            if not existing:
                # Calculate initial stats from existing user_stats
                stats = cursor.execute('''
                    SELECT 
                        COUNT(*) as total_plays,
                        SUM(CASE WHEN correct_guess = 1 THEN 1 ELSE 0 END) as total_correct,
                        AVG(CASE WHEN correct_guess = 1 THEN (7 - difficulty_level) ELSE 0 END) as avg_score
                    FROM user_stats 
                    WHERE song_id = ?
                ''', (song_id,)).fetchone()
                
                # Calculate points distribution
                points_dist = {}
                for score in range(8):
                    count = cursor.execute('''
                        SELECT COUNT(*) as count
                        FROM user_stats 
                        WHERE song_id = ? AND correct_guess = 1 AND (7 - difficulty_level) = ?
                    ''', (song_id, score)).fetchone()
                    points_dist[score] = count[0]
                
                cursor.execute('''
                    INSERT INTO song_stats (song_id, total_plays, total_correct_guesses, average_score, points_distribution)
                    VALUES (?, ?, ?, ?, ?)
                ''', (song_id, stats[0] or 0, stats[1] or 0, stats[2] or 0, json.dumps(points_dist)))
        
        # Set has_played=1 for users who have already played songs
        print("Setting has_played=1 for existing players...")
        cursor.execute('UPDATE user_stats SET has_played = 1 WHERE correct_guess = 1 OR guess_count > 0')
        updated_count = cursor.rowcount
        print(f"✅ Updated {updated_count} user stats records")
        
        conn.commit()
        print("✅ Database migration completed successfully")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    import os
    migrate_database() 