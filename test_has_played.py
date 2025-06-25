#!/usr/bin/env python3
"""
Test script to verify the has_played functionality
"""

import sqlite3
import json

def test_has_played_functionality():
    """Test the has_played functionality"""
    
    # Connect to database
    conn = sqlite3.connect('game.db')
    conn.row_factory = sqlite3.Row
    
    print("🔍 Testing has_played functionality...")
    
    # Check if has_played column exists
    cursor = conn.execute("PRAGMA table_info(user_stats)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'has_played' not in columns:
        print("❌ has_played column not found in user_stats table")
        return False
    else:
        print("✅ has_played column exists")
    
    # Check if song_stats table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='song_stats'")
    if not cursor.fetchone():
        print("❌ song_stats table not found")
        return False
    else:
        print("✅ song_stats table exists")
    
    # Get current active song
    current_song = conn.execute('SELECT * FROM songs WHERE is_active = 1').fetchone()
    if not current_song:
        print("❌ No active song found")
        return False
    
    print(f"✅ Active song: {current_song['title']} by {current_song['artist']}")
    
    # Check song_stats for current song
    song_stats = conn.execute('SELECT * FROM song_stats WHERE song_id = ?', (current_song['id'],)).fetchone()
    if song_stats:
        print(f"✅ Song stats found - Total plays: {song_stats['total_plays']}, Average score: {song_stats['average_score']}")
        points_dist = json.loads(song_stats['points_distribution'])
        print(f"   Points distribution: {points_dist}")
    else:
        print("⚠️  No song stats found for current song")
    
    # Check user_stats for has_played flags
    user_stats = conn.execute('SELECT * FROM user_stats WHERE song_id = ?', (current_song['id'],)).fetchall()
    print(f"✅ Found {len(user_stats)} user stats records for current song")
    
    for stat in user_stats:
        user = conn.execute('SELECT username FROM users WHERE id = ?', (stat['user_id'],)).fetchone()
        username = user['username'] if user else f"User {stat['user_id']}"
        print(f"   {username}: has_played={stat['has_played']}, correct_guess={stat['correct_guess']}")
    
    conn.close()
    print("✅ Test completed successfully")
    return True

if __name__ == "__main__":
    test_has_played_functionality() 