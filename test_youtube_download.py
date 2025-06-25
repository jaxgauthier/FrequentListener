#!/usr/bin/env python3
"""
Test script for YouTube audio download functionality
"""

import os
import sys
from app import download_audio_from_youtube

def test_youtube_download():
    """Test downloading a short audio clip"""
    print("Testing YouTube audio download...")
    
    # Test with a well-known song
    song_title = "Bohemian Rhapsody"
    artist = "Queen"
    output_path = "test_download.wav"
    
    # Test downloading only a 10-second range (from 30s to 40s)
    start_time = 30
    end_time = 40
    
    print(f"Attempting to download: {song_title} by {artist}")
    print(f"Time range: {start_time}s - {end_time}s (10 seconds)")
    
    success = download_audio_from_youtube(song_title, artist, output_path, start_time, end_time)
    
    if success and os.path.exists(output_path):
        print(f"✅ Success! Downloaded: {output_path}")
        print(f"File size: {os.path.getsize(output_path)} bytes")
        
        # Clean up
        os.remove(output_path)
        print("Cleaned up test file")
        return True
    else:
        print("❌ Download failed")
        return False

if __name__ == "__main__":
    test_youtube_download() 