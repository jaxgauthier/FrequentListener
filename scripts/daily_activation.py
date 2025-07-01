#!/usr/bin/env python3
"""
Daily song activation script
This script should be run daily via cron job to:
1. Activate today's song
2. Clean up expired songs
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.services.queue_service import QueueService
from datetime import datetime

def main():
    """Main function to activate today's song and clean up expired songs"""
    app = create_app()
    
    with app.app_context():
        print(f"[{datetime.now()}] Starting daily song activation...")
        
        # Activate today's song
        try:
            song = QueueService.activate_todays_song()
            if song:
                print(f"[{datetime.now()}] ✅ Activated: {song.title} by {song.artist}")
            else:
                print(f"[{datetime.now()}] ⚠️  No song queued for today")
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Error activating today's song: {e}")
        
        # Clean up expired songs
        try:
            QueueService.cleanup_expired_songs()
            print(f"[{datetime.now()}] ✅ Cleaned up expired songs")
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Error cleaning up expired songs: {e}")
        
        print(f"[{datetime.now()}] Daily activation complete")

if __name__ == '__main__':
    main() 