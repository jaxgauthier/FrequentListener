import os
import sys

def play_audio(file_path):
    """Play the audio file using system default player"""
    try:
        print(f"Attempting to play audio file: {file_path}")
        if sys.platform == 'darwin':  # macOS
            os.system(f'afplay "{file_path}"')
        elif sys.platform == 'win32':  # Windows
            os.system(f'start wmplayer "{file_path}"')
        else:  # Linux
            os.system(f'aplay "{file_path}"')
        print("Audio playback command sent successfully")
    except Exception as e:
        print(f"Error during audio playback: {str(e)}")
        import traceback
        traceback.print_exc()

