from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime
import requests
import numpy as np
import soundfile as sf
import tempfile
from pydub import AudioSegment
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import re
import glob
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Spotify API configuration
# TODO: Replace these with your actual Spotify credentials from https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = '191d5956bb7e4beea2ec9f1830b3daa0'  # Replace with your actual Client ID from Spotify Developer Dashboard
SPOTIFY_CLIENT_SECRET = '14ffa485968442c88be6abad35b71ece'  # Replace with your actual Client Secret from Spotify Developer Dashboard

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('OutputWAVS', exist_ok=True)

# Initialize with Mr Brightside for demo
songs = [
    {
        'id': 1,
        'title': 'Mr. Brightside',
        'artist': 'The Killers',
        'week': 1,
        'upload_date': '2024-01-01',
        'has_frequency_versions': True,
        'base_filename': 'MrBrightside'
    }
]
current_week = 1

def process_song_through_dft(input_file, output_folder, base_filename, start_time=0, end_time=None):
    """
    Process a song through the DFT pipeline and generate frequency versions
    Note: The input_file should already be the correct time segment
    """
    try:
        # Import the DFT processing functions
        from layersFFT import read_audio_file
        from manim_to_audio import save_audio
        
        print(f"Processing {input_file} through DFT pipeline...")
        
        # Read the audio file (already the correct segment)
        data, sample_rate, num_channels = read_audio_file(input_file)
        print(f"Audio loaded: {data.shape}, {sample_rate}Hz, {num_channels} channels")
        
        # Calculate total duration
        total_duration = len(data) / sample_rate
        print(f"Audio duration: {total_duration:.2f} seconds")
        
        # Process the entire audio file (no time range extraction needed)
        # Compute FFT
        fft_result = np.fft.fft(data)
        freq = np.fft.fftfreq(len(data), 1/sample_rate)
        magnitude = np.abs(fft_result)
        
        # Filter out very small magnitudes (noise)
        min_magnitude_threshold = np.max(magnitude) * 0.01
        significant_indices = magnitude > min_magnitude_threshold
        
        # Define frequency counts to generate
        frequency_counts = [100, 500, 1000, 2000, 3500, 5000, 7500]
        available_indices = np.where(significant_indices)[0]
        
        # Create output folder for this song
        song_output_folder = os.path.join('OutputWAVS', output_folder)
        os.makedirs(song_output_folder, exist_ok=True)
        
        for freq_count in frequency_counts:
            print(f"Generating {freq_count} frequency version...")
            
            # Get top frequencies
            top_indices = available_indices[np.argsort(magnitude[available_indices])[-freq_count:][::-1]]
            top_freqs = freq[top_indices]
            top_magnitudes = magnitude[top_indices]
            
            # Create filtered FFT result
            filtered_fft = np.zeros_like(fft_result)
            
            # Copy significant frequency components
            for freq_val, mag_val in zip(top_freqs, top_magnitudes):
                freq_index = np.argmin(np.abs(freq - freq_val))
                filtered_fft[freq_index] = fft_result[freq_index]
                if freq_index > 0:
                    filtered_fft[len(fft_result) - freq_index] = np.conj(fft_result[freq_index])
            
            # Reconstruct audio
            reconstructed_audio = np.real(np.fft.ifft(filtered_fft))
            reconstructed_audio = reconstructed_audio / np.max(np.abs(reconstructed_audio))
            
            # Save the reconstructed audio
            output_file = os.path.join(song_output_folder, f'reconstructed_audio_{freq_count}.wav')
            save_audio(reconstructed_audio, sample_rate, output_file)
            print(f"Saved: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"Error processing song through DFT: {e}")
        return False

def download_audio_from_youtube(song_title, artist, output_path, start_time=0, end_time=None):
    """
    Download audio from YouTube using song title and artist.
    Downloads the full audio, then extracts the desired segment as .wav.
    """
    try:
        # Create search query
        search_query = f"{song_title} {artist} audio"
        
        # Create a temp file template for the raw download
        with tempfile.NamedTemporaryFile(suffix='', delete=False) as temp_audio_file:
            temp_audio_path_base = temp_audio_file.name
        temp_audio_tmpl = temp_audio_path_base + ".%(ext)s"
        
        # yt-dlp options: download bestaudio to temp file (let yt-dlp choose extension)
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio',  # Prefer m4a, then webm, then best
            'outtmpl': temp_audio_tmpl,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'postprocessors': [],  # No conversion yet
        }
        print(f"Searching YouTube for: {search_query}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch1:{search_query}", download=False)
            if not search_results or 'entries' not in search_results or not search_results['entries']:
                raise Exception(f"No YouTube videos found for: {search_query}")
            video_info = search_results['entries'][0]
            video_url = video_info['url']
            print(f"Found video: {video_info.get('title', 'Unknown')}")
            print(f"Downloading from: {video_url}")
            ydl.download([video_url])
        # Find the actual downloaded file (with correct extension)
        downloaded_files = glob.glob(temp_audio_path_base + ".*")
        if not downloaded_files:
            raise Exception("Download completed but file not found")
        temp_audio_path = downloaded_files[0]  # Use the first match
        print(f"Downloaded raw audio to: {temp_audio_path}")
        # Use pydub to extract the segment
        audio = AudioSegment.from_file(temp_audio_path)
        if end_time is not None:
            segment = audio[start_time*1000:end_time*1000]
        else:
            segment = audio[start_time*1000:]
        
        # No preprocessing - use raw audio to preserve quality
        print("Extracting raw audio segment without preprocessing...")
        
        segment.export(output_path, format="wav")
        print(f"Exported raw segment to: {output_path}")
        # Clean up temp file(s)
        for f in downloaded_files:
            os.remove(f)
            print(f"Cleaned up temp file: {f}")
        return True
    except Exception as e:
        print(f"Error downloading from YouTube: {e}")
        try:
            if 'downloaded_files' in locals():
                for f in downloaded_files:
                    if os.path.exists(f):
                        os.remove(f)
        except Exception:
            pass
        return False

def get_available_frequencies(song_name):
    """Get the available frequency levels for a given song"""
    song_folder = os.path.join('OutputWAVS', song_name)
    
    if not os.path.exists(song_folder):
        # Fallback to the old mapping system
        song_folders = {
            'MrBrightside': 'MrBrighstide',  # Note the typo in the folder name
            'GhostTown': 'GhostTown',
            'Milan': 'Milan',
            'TeenageDirtbag': 'TeenageDirtbag'
        }
        
        folder_name = song_folders.get(song_name)
        if not folder_name:
            return []
        song_folder = os.path.join('OutputWAVS', folder_name)
    
    available_frequencies = []
    if os.path.exists(song_folder):
        for file in os.listdir(song_folder):
            if file.startswith('reconstructed_audio_') and file.endswith('.wav'):
                freq = file.replace('reconstructed_audio_', '').replace('.wav', '')
                available_frequencies.append(freq)
    
    # Sort frequencies numerically
    available_frequencies.sort(key=int)
    return available_frequencies

def get_db_connection():
    conn = sqlite3.connect('game.db')
    conn.row_factory = sqlite3.Row
    return conn

# Routes
@app.route('/spotify_search')
def spotify_search():
    """Search Spotify for songs based on query"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'tracks': []})
    
    # Check if Spotify credentials are configured
    if SPOTIFY_CLIENT_ID == 'your-spotify-client-id' or SPOTIFY_CLIENT_SECRET == 'your-spotify-client-secret':
        # Return sample songs for testing when credentials aren't configured
        sample_songs = [
            {'id': 'sample1', 'name': 'Bohemian Rhapsody', 'artist': 'Queen', 'album': 'A Night at the Opera'},
            {'id': 'sample2', 'name': 'Hotel California', 'artist': 'Eagles', 'album': 'Hotel California'},
            {'id': 'sample3', 'name': 'Stairway to Heaven', 'artist': 'Led Zeppelin', 'album': 'Led Zeppelin IV'},
            {'id': 'sample4', 'name': 'Imagine', 'artist': 'John Lennon', 'album': 'Imagine'},
            {'id': 'sample5', 'name': 'Hey Jude', 'artist': 'The Beatles', 'album': 'The Beatles 1967-1970'},
            {'id': 'sample6', 'name': 'Wonderwall', 'artist': 'Oasis', 'album': '(What\'s the Story) Morning Glory?'},
            {'id': 'sample7', 'name': 'Smells Like Teen Spirit', 'artist': 'Nirvana', 'album': 'Nevermind'},
            {'id': 'sample8', 'name': 'Sweet Child O\' Mine', 'artist': 'Guns N\' Roses', 'album': 'Appetite for Destruction'}
        ]
        
        # Filter sample songs based on query
        filtered_songs = [
            song for song in sample_songs 
            if query.lower() in song['name'].lower() or query.lower() in song['artist'].lower()
        ]
        
        return jsonify({'tracks': filtered_songs[:5]})
    
    try:
        # Initialize Spotify client
        client_credentials_manager = SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        # Search Spotify
        results = sp.search(q=query, type='track', limit=5)
        
        if not results or 'tracks' not in results:
            return jsonify({'tracks': [], 'error': 'No search results'})
        
        tracks = results['tracks']['items']
        results = []
        
        for track in tracks:
            results.append({
                'id': track['id'],
                'name': track['name'],
                'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown Artist',
                'album': track['album']['name'] if track['album'] else 'Unknown Album'
            })
        
        return jsonify({'tracks': results})
        
    except Exception as e:
        print(f"Spotify search error: {e}")
        return jsonify({'tracks': [], 'error': 'Search failed'})

@app.route('/')
def user_page():
    conn = get_db_connection()
    song = conn.execute('SELECT * FROM songs WHERE is_active = 1').fetchone()
    conn.close()
    
    if song:
        # Convert to dict and add available frequencies
        song_dict = dict(song)
        song_dict['available_frequencies'] = get_available_frequencies(song_dict['base_filename'])
        return render_template('user.html', current_song=song_dict)
    else:
        return render_template('user.html', current_song=None)

@app.route('/admin')
def admin_page():
    conn = get_db_connection()
    songs = conn.execute('SELECT * FROM songs').fetchall()
    conn.close()
    # Add available frequencies to each song (dynamically from filesystem)
    song_list = []
    for song in songs:
        song_dict = dict(song)
        song_dict['available_frequencies'] = get_available_frequencies(song_dict['base_filename'])
        song_list.append(song_dict)
    stats = {
        'total_songs': len(song_list),
        'total_plays': 0,  # TODO: implement play tracking
        'this_week_plays': 0  # TODO: implement play tracking
    }
    return render_template('admin.html', songs=song_list, stats=stats)

@app.route('/admin/upload', methods=['POST'])
def admin_upload():
    """Handle song upload from admin"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Get form data
        title = request.form.get('title', 'Unknown')
        artist = request.form.get('artist', 'Unknown')
        week = int(request.form.get('week', 1))
        
        # Create song entry
        song = {
            'id': len(songs) + 1,
            'title': title,
            'artist': artist,
            'week': week,
            'filename': unique_filename,
            'upload_date': datetime.now().strftime('%Y-%m-%d'),
            'has_frequency_versions': False  # New uploads don't have frequency versions yet
        }
        
        songs.append(song)
        
        return jsonify({'success': True, 'message': 'Song uploaded successfully'})
    
    return jsonify({'error': 'Invalid file'}), 400

@app.route('/admin/delete/<int:song_id>', methods=['DELETE'])
def admin_delete(song_id):
    """Delete a song from the database"""
    try:
        conn = get_db_connection()
        
        # Get the song info before deleting (for cleanup)
        song = conn.execute('SELECT * FROM songs WHERE id = ?', (song_id,)).fetchone()
        
        if not song:
            conn.close()
            return jsonify({'success': False, 'error': 'Song not found'}), 404
        
        # Delete from database
        conn.execute('DELETE FROM songs WHERE id = ?', (song_id,))
        conn.commit()
        conn.close()
        
        # Optional: Clean up frequency files from filesystem
        try:
            if song['base_filename']:
                song_folder = os.path.join('OutputWAVS', song['base_filename'])
                if os.path.exists(song_folder):
                    import shutil
                    shutil.rmtree(song_folder)
                    print(f"Deleted frequency files for: {song['base_filename']}")
        except Exception as e:
            print(f"Warning: Could not clean up frequency files: {e}")
        
        return jsonify({'success': True, 'message': f'Deleted {song["title"]} by {song["artist"]}'})
        
    except Exception as e:
        print(f"Error deleting song: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/submit_guess', methods=['POST'])
def submit_guess():
    """Handle user guess submission"""
    song_guess = request.form.get('song_guess', '').strip().lower()
    
    # Get the current song (most recently added song - last in the list)
    current_song = songs[-1] if songs else None
    
    if not current_song:
        return jsonify({'error': 'No song available'}), 400
    
    # Simple string matching (you can make this more sophisticated)
    correct_song = current_song['title'].lower()
    
    is_correct = (song_guess == correct_song)
    
    return jsonify({
        'correct': is_correct,
        'correct_answer': f"{current_song['title']} by {current_song['artist']}"
    })

@app.route('/play/<filename>')
def play_audio(filename):
    """Serve audio files from uploads folder"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath)
    return 'File not found', 404

@app.route('/play_frequency/<song_name>/<frequency>')
def play_frequency_audio(song_name, frequency):
    """Serve frequency-specific audio files from OutputWAVS"""
    # First check if the song folder exists directly
    song_folder = os.path.join('OutputWAVS', song_name)
    
    if not os.path.exists(song_folder):
        # Fallback to the old mapping system
        song_folders = {
            'MrBrightside': 'MrBrighstide',  # Note the typo in the folder name
            'GhostTown': 'GhostTown',
            'Milan': 'Milan',
            'TeenageDirtbag': 'TeenageDirtbag'
        }
        
        folder_name = song_folders.get(song_name)
        if not folder_name:
            return 'Song not found', 404
        song_folder = os.path.join('OutputWAVS', folder_name)
    
    filepath = os.path.join(song_folder, f'reconstructed_audio_{frequency}.wav')
    
    if os.path.exists(filepath):
        return send_file(filepath)
    return 'Frequency version not found', 404

@app.route('/admin/process_spotify_song', methods=['POST'])
def admin_process_spotify_song():
    """Process a Spotify song through the DFT pipeline"""
    try:
        data = request.get_json()
        spotify_id = data.get('spotify_id')
        title = data.get('title')
        artist = data.get('artist')
        album = data.get('album')
        week = data.get('week', 1)
        start_time = data.get('start_time', 0)
        end_time = data.get('end_time', 10)
        
        if not all([spotify_id, title, artist]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Create a safe filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_artist = "".join(c for c in artist if c.isalnum() or c in (' ', '-', '_')).rstrip()
        base_filename = f"{safe_artist}_{safe_title}".replace(' ', '')
        
        # Create temporary directory for downloads
        temp_dir = os.path.join('uploads', 'temp_downloads')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Download audio from YouTube
        audio_filename = f"{base_filename}.wav"
        audio_path = os.path.join(temp_dir, audio_filename)
        
        print(f"Downloading audio for '{title}' by {artist}...")
        download_success = download_audio_from_youtube(title, artist, audio_path, start_time, end_time)
        
        if not download_success:
            return jsonify({'success': False, 'error': f'Failed to download audio for {title}'}), 500
        
        if not os.path.exists(audio_path):
            return jsonify({'success': False, 'error': 'Downloaded file not found'}), 500
        
        print(f"Successfully downloaded: {audio_path}")
        
        # Process the song through DFT pipeline (audio file is already the correct segment)
        success = process_song_through_dft(audio_path, base_filename, base_filename)
        
        if not success:
            return jsonify({'success': False, 'error': 'Failed to process song through DFT pipeline'}), 500
        
        # Clean up the downloaded file
        try:
            os.remove(audio_path)
            print(f"Cleaned up temporary file: {audio_path}")
        except Exception as e:
            print(f"Warning: Could not clean up temporary file: {e}")
        
        # Create song entry
        song = {
            'id': len(songs) + 1,
            'title': title,
            'artist': artist,
            'album': album,
            'week': week,
            'upload_date': datetime.now().strftime('%Y-%m-%d'),
            'has_frequency_versions': True,
            'base_filename': base_filename,
            'spotify_id': spotify_id
        }
        
        songs.append(song)
        
        return jsonify({
            'success': True, 
            'message': f'Successfully processed {title} by {artist} ({start_time}s - {end_time}s)',
            'song_id': song['id']
        })
        
    except Exception as e:
        print(f"Error processing Spotify song: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/set_active/<int:song_id>', methods=['POST'])
def set_active(song_id):
    conn = get_db_connection()
    conn.execute('UPDATE songs SET is_active = 0')
    conn.execute('UPDATE songs SET is_active = 1 WHERE id = ?', (song_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_page'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 