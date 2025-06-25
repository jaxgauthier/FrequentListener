#!/usr/bin/env python3
"""
Cleanup script for the DFT Audio Frequency Game project.
Removes unnecessary files to keep the project clean.
"""

import os
import shutil
import glob

def cleanup_project():
    """Remove unnecessary files from the project"""
    
    # Files to delete
    files_to_delete = [
        'test_audio_quality.py',
        'test_youtube_download.py', 
        'test_placeholder_10s.wav',
        'pitchTest.py',
        'pitchTestInput.wav',
        'temp_animation_data.json',
        'temp_animation_MrBrightside_10.json',
        'temp_audio.wav',
        '.cache',
        'DisplayWAV.py',
        'manim_test.py'
        # Note: manim_to_audio.py is ESSENTIAL - do not delete!
    ]
    
    # Directories to delete
    dirs_to_delete = [
        'media',
        'InputWAVS',
        '__pycache__'
    ]
    
    # Patterns to match
    patterns_to_delete = [
        '.DS_Store',
        '*.pyc',
        '__pycache__'
    ]
    
    print("🧹 Starting project cleanup...")
    print("=" * 50)
    
    # Delete individual files
    print("\n📁 Deleting unnecessary files:")
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"  ✅ Deleted: {file_path}")
            except Exception as e:
                print(f"  ❌ Failed to delete {file_path}: {e}")
        else:
            print(f"  ⚠️  Not found: {file_path}")
    
    # Delete directories
    print("\n📂 Deleting unnecessary directories:")
    for dir_path in dirs_to_delete:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"  ✅ Deleted: {dir_path}/")
            except Exception as e:
                print(f"  ❌ Failed to delete {dir_path}/: {e}")
        else:
            print(f"  ⚠️  Not found: {dir_path}/")
    
    # Delete files matching patterns
    print("\n🔍 Deleting files matching patterns:")
    for pattern in patterns_to_delete:
        matches = glob.glob(pattern, recursive=True)
        for match in matches:
            try:
                if os.path.isfile(match):
                    os.remove(match)
                    print(f"  ✅ Deleted: {match}")
                elif os.path.isdir(match):
                    shutil.rmtree(match)
                    print(f"  ✅ Deleted: {match}/")
            except Exception as e:
                print(f"  ❌ Failed to delete {match}: {e}")
    
    # Clean up uploads/temp_downloads if empty
    temp_downloads = 'uploads/temp_downloads'
    if os.path.exists(temp_downloads):
        try:
            if not os.listdir(temp_downloads):  # If directory is empty
                os.rmdir(temp_downloads)
                print(f"  ✅ Deleted empty directory: {temp_downloads}/")
        except Exception as e:
            print(f"  ⚠️  Could not delete {temp_downloads}/: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Cleanup complete!")
    print("\n📋 Summary of what was removed:")
    print("  • Test files and scripts")
    print("  • Temporary animation data")
    print("  • Old input audio files")
    print("  • Manim-generated media")
    print("  • Python cache files")
    print("  • macOS system files")
    print("\n💾 Your project is now cleaner and more organized!")

if __name__ == "__main__":
    # Ask for confirmation
    response = input("Are you sure you want to delete these files? (y/N): ")
    if response.lower() in ['y', 'yes']:
        cleanup_project()
    else:
        print("Cleanup cancelled.") 