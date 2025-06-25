from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
import os
import uuid
import json
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
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
import hashlib
import secrets
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-this-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Spotify API configuration
# TODO: Replace these with your actual Spotify credentials from https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = '191d5956bb7e4beea2ec9f1830b3daa0'
SPOTIFY_CLIENT_SECRET = '14ffa485968442c88be6abad35b71ece'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('OutputWAVS', exist_ok=True)

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

# Authentication helper functions
def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_session_token():
    """Generate a secure random session token"""
    return secrets.token_urlsafe(32)

def create_user_session(user_id):
    """Create a new session for a user"""
    token = generate_session_token()
    expires_at = datetime.now() + timedelta(days=30)  # 30 day session
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO user_sessions (user_id, session_token, expires_at)
        VALUES (?, ?, ?)
    ''', (user_id, token, expires_at.strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()
    
    return token

def get_user_from_session():
    """Get user from session token"""
    session_token = request.cookies.get('session_token')
    if not session_token:
        return None
    
    conn = get_db_connection()
    user = conn.execute('''
        SELECT u.* FROM users u
        JOIN user_sessions s ON u.id = s.user_id
        WHERE s.session_token = ? AND s.expires_at > ?
    ''', (session_token, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))).fetchone()
    conn.close()
    
    return user

def login_required(f):
    """Decorator to require login for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_user_from_session()
        if not user:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin access using admin_users table"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_user_from_session()
        if not user:
            return redirect(url_for('login'))
        
        # Check if user exists in admin_users table
        conn = get_db_connection()
        admin_user = conn.execute('''
            SELECT * FROM admin_users WHERE username = ?
        ''', (user['username'],)).fetchone()
        conn.close()
        
        if not admin_user:
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def get_user_stats(user_id, current_song_id=None):
    """Get stats for a user, focusing on current song performance and all-time stats"""
    conn = get_db_connection()
    
    # Check if user has already played the current song
    has_played_current = False
    if current_song_id:
        played_check = conn.execute('''
            SELECT has_played FROM user_stats 
            WHERE user_id = ? AND song_id = ?
        ''', (user_id, current_song_id)).fetchone()
        has_played_current = played_check['has_played'] if played_check else False
    
    # Get global song stats for the current song (for average score)
    global_song_stats = None
    if current_song_id:
        song_stats_row = conn.execute('''
            SELECT * FROM song_stats WHERE song_id = ?
        ''', (current_song_id,)).fetchone()
        
        if song_stats_row:
            global_points_distribution = json.loads(song_stats_row['points_distribution'])
            global_max_count = max(global_points_distribution.values()) if global_points_distribution.values() else 1
            
            global_song_stats = {
                'average_score': song_stats_row['average_score'] or 0,
                'points_distribution': global_points_distribution,
                'max_count': global_max_count,
                'total_plays': song_stats_row['total_plays'] or 0
            }
    
    # If no global song stats exist, create default
    if not global_song_stats:
        global_song_stats = {
            'average_score': 0,
            'points_distribution': {i: 0 for i in range(8)},
            'max_count': 1,
            'total_plays': 0
        }
    
    # Get ALL-TIME individual user stats across all songs (for personal bar chart)
    all_time_stats = conn.execute('''
        SELECT difficulty_level, correct_guess FROM user_stats 
        WHERE user_id = ? AND correct_guess = 1
    ''', (user_id,)).fetchall()
    
    # Create all-time points distribution
    all_time_points_distribution = {i: 0 for i in range(8)}
    for stat in all_time_stats:
        score = 7 - stat['difficulty_level']  # Calculate score from difficulty level
        all_time_points_distribution[score] += 1
    
    all_time_max_count = max(all_time_points_distribution.values()) if all_time_points_distribution.values() else 1
    
    individual_stats = {
        'points_distribution': all_time_points_distribution,
        'max_count': all_time_max_count,
        'total_correct_guesses': sum(all_time_points_distribution.values())
    }
    
    conn.close()
    
    return {
        'has_played_current': has_played_current,
        'song_stats': global_song_stats,  # Global stats for current song average
        'individual_stats': individual_stats  # All-time stats for personal bar chart
    }

def update_song_stats(song_id, final_score, is_correct):
    """Update global song statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get current song stats
        song_stats = conn.execute('SELECT * FROM song_stats WHERE song_id = ?', (song_id,)).fetchone()
        
        if song_stats:
            # Debug: Print the raw database values
            print(f"Raw database values: total_plays={song_stats['total_plays']} (type: {type(song_stats['total_plays'])})")
            print(f"Raw database values: total_correct_guesses={song_stats['total_correct_guesses']} (type: {type(song_stats['total_correct_guesses'])})")
            
            # Update existing stats - ensure proper type conversion
            total_plays = int(song_stats['total_plays']) + 1
            total_correct = int(song_stats['total_correct_guesses']) + (1 if is_correct else 0)
            
            # Get current points distribution
            points_dist = json.loads(song_stats['points_distribution'])
            print(f"Current points_dist: {points_dist} (type: {type(points_dist)})")
            
            # Convert all keys to integers to ensure consistency
            points_dist = {int(k): int(v) for k, v in points_dist.items()}
            print(f"Converted points_dist: {points_dist}")
            
            # Update points distribution if correct
            if is_correct:
                print(f"Updating points_dist for score {final_score}")
                print(f"Current value for {final_score}: {points_dist.get(final_score, 0)} (type: {type(points_dist.get(final_score, 0))})")
                points_dist[final_score] = points_dist.get(final_score, 0) + 1
                print(f"New value for {final_score}: {points_dist[final_score]}")
            
            # Calculate new average
            print(f"Calculating average from points_dist: {points_dist}")
            total_score = sum(score * count for score, count in points_dist.items())
            total_correct_plays = sum(points_dist.values())
            new_average = total_score / total_correct_plays if total_correct_plays > 0 else 0
            
            print(f"Updating song stats: final_score={final_score}, is_correct={is_correct}")
            print(f"Points distribution: {points_dist}")
            print(f"Total score: {total_score}, Total correct plays: {total_correct_plays}")
            print(f"New average: {new_average}")
            
            cursor.execute('''
                UPDATE song_stats 
                SET total_plays = ?, total_correct_guesses = ?, average_score = ?, 
                    points_distribution = ?, last_updated = ?
                WHERE song_id = ?
            ''', (total_plays, total_correct, new_average, json.dumps(points_dist), 
                  datetime.now().strftime('%Y-%m-%d %H:%M:%S'), song_id))
        else:
            # Create new song stats
            points_dist = {final_score: 1} if is_correct else {i: 0 for i in range(8)}
            # Ensure all keys are integers
            points_dist = {int(k): int(v) for k, v in points_dist.items()}
            # Calculate average the same way as for updates
            total_score = sum(score * count for score, count in points_dist.items())
            total_correct_plays = sum(points_dist.values())
            average_score = total_score / total_correct_plays if total_correct_plays > 0 else 0
            
            print(f"Creating new song stats: final_score={final_score}, is_correct={is_correct}")
            print(f"Points distribution: {points_dist}")
            print(f"Total score: {total_score}, Total correct plays: {total_correct_plays}")
            print(f"Initial average: {average_score}")
            
            cursor.execute('''
                INSERT INTO song_stats (song_id, total_plays, total_correct_guesses, 
                                       average_score, points_distribution, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (song_id, 1, 1 if is_correct else 0, average_score, 
                  json.dumps(points_dist), datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        conn.commit()
        
    except Exception as e:
        print(f"Error updating song stats: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

def reset_has_played_for_all_users():
    """Reset has_played flags for all users when active song changes"""
    conn = get_db_connection()
    conn.execute('UPDATE user_stats SET has_played = 0')
    conn.commit()
    conn.close()
    print("Reset has_played flags for all users")

@app.route('/current_stats')
def current_stats():
    """Get current stats for the logged-in user and active song"""
    user = get_user_from_session()
    conn = get_db_connection()
    current_song = conn.execute('SELECT * FROM songs WHERE is_active = 1').fetchone()
    conn.close()
    
    if not user or not current_song:
        return jsonify({'success': False, 'error': 'No user or song'}), 400
    
    stats = get_user_stats(user['id'], current_song['id'])
    
    # Also return song title/artist for context
    return jsonify({
        'success': True,
        'stats': stats,
        'song': {
            'title': current_song['title'],
            'artist': current_song['artist']
        }
    })

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password are required'}), 400
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if not user or user['password_hash'] != hash_password(password):
            return jsonify({'success': False, 'error': 'Invalid username or password'}), 401
        
        # Create session
        session_token = create_user_session(user['id'])
        
        # Update last login
        conn = get_db_connection()
        conn.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                    (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user['id']))
        conn.commit()
        conn.close()
        
        response = jsonify({'success': True, 'message': 'Login successful'})
        response.set_cookie('session_token', session_token, max_age=30*24*60*60, httponly=True)
        return response
    
    return render_template('login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'})
        
        # Check admin credentials
        conn = get_db_connection()
        admin_user = conn.execute('''
            SELECT * FROM admin_users WHERE username = ?
        ''', (username,)).fetchone()
        conn.close()
        
        if admin_user and admin_user['password_hash'] == hash_password(password):
            # Create session for admin user (using regular users table for session management)
            # First check if admin exists as regular user, if not create them
            conn = get_db_connection()
            regular_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            
            if not regular_user:
                # Create regular user account for admin (for session management)
                cursor = conn.cursor()
                admin_user_dict = dict(admin_user)
                email = admin_user_dict.get('email', f'{username}@admin.local')  # Provide default email
                cursor.execute('''
                    INSERT INTO users (username, password_hash, email)
                    VALUES (?, ?, ?)
                ''', (username, admin_user['password_hash'], email))
                user_id = cursor.lastrowid
                conn.commit()
            else:
                user_id = regular_user['id']
            
            conn.close()
            
            session_token = create_user_session(user_id)
            response = jsonify({'success': True, 'redirect': url_for('admin_page')})
            response.set_cookie('session_token', session_token, max_age=86400, httponly=True)
            return response
        else:
            return jsonify({'success': False, 'error': 'Invalid admin credentials'})
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session_token = request.cookies.get('session_token')
    if session_token:
        # Remove session from database
        conn = get_db_connection()
        conn.execute('DELETE FROM user_sessions WHERE session_token = ?', (session_token,))
        conn.commit()
        conn.close()
    
    response = redirect(url_for('admin_login'))
    response.delete_cookie('session_token')
    return response

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user registration"""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            return jsonify({'success': False, 'error': 'All fields are required'}), 400
        
        if password != confirm_password:
            return jsonify({'success': False, 'error': 'Passwords do not match'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return jsonify({'success': False, 'error': 'Username can only contain letters, numbers, and underscores'}), 400
        
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        conn = get_db_connection()
        
        # Check if username or email already exists
        existing_user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', 
                                   (username, email)).fetchone()
        if existing_user:
            conn.close()
            return jsonify({'success': False, 'error': 'Username or email already exists'}), 409
        
        # Create new user
        password_hash = hash_password(password)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', (username, email, password_hash))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Create session
        session_token = create_user_session(user_id)
        
        response = jsonify({'success': True, 'message': 'Account created successfully'})
        response.set_cookie('session_token', session_token, max_age=30*24*60*60, httponly=True)
        return response
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """Handle user logout"""
    session_token = request.cookies.get('session_token')
    if session_token:
        conn = get_db_connection()
        conn.execute('DELETE FROM user_sessions WHERE session_token = ?', (session_token,))
        conn.commit()
        conn.close()
    
    response = redirect(url_for('user_page'))
    response.delete_cookie('session_token')
    return response

@app.route('/profile')
@login_required
def profile():
    """User profile page with stats"""
    user = get_user_from_session()
    if not user:
        return redirect(url_for('login'))
    stats = get_user_stats(user['id'])
    return render_template('profile.html', user=user, stats=stats)

@app.route('/')
def user_page():
    """Main user page"""
    # Get current active song
    conn = get_db_connection()
    current_song = conn.execute('SELECT * FROM songs WHERE is_active = 1').fetchone()
    conn.close()
    
    # Get user from session (optional - users can play without logging in)
    user = get_user_from_session()
    stats = None
    
    if user:
        # Get user stats
        stats = get_user_stats(user['id'], current_song['id'] if current_song else None)
    
    if current_song:
        # Get available frequencies for this song
        available_frequencies = get_available_frequencies(current_song['base_filename'])
        current_song = dict(current_song)
        current_song['available_frequencies'] = available_frequencies
    
    return render_template('user.html', current_song=current_song, user=user, stats=stats)

@app.route('/admin')
@admin_required
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
@admin_required
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
        
        # Add song to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO songs (title, artist, week, filename, upload_date, has_frequency_versions, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, artist, week, unique_filename, datetime.now().strftime('%Y-%m-%d'), False, 0))
        
        song_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Song uploaded successfully', 'song_id': song_id})
    
    return jsonify({'error': 'Invalid file'}), 400

@app.route('/admin/delete/<int:song_id>', methods=['DELETE'])
@admin_required
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
    difficulty_level = int(request.form.get('difficulty_level', 0))  # Current difficulty level
    current_score = int(request.form.get('current_score', 100))  # Current score
    
    # Get the current active song from database
    conn = get_db_connection()
    current_song = conn.execute('SELECT * FROM songs WHERE is_active = 1').fetchone()
    conn.close()
    
    if not current_song:
        return jsonify({'error': 'No active song available'}), 400
    
    # Get correct song info
    correct_title = current_song['title'].lower()
    correct_artist = current_song['artist'].lower()
    correct_title_artist = f"{correct_title} - {correct_artist}"
    
    # Check if guess matches title only, artist only, or title - artist format
    is_correct = (
        song_guess == correct_title or 
        song_guess == correct_artist or 
        song_guess == correct_title_artist
    )
    
    # Calculate final score (score decreases with each difficulty level)
    # Score starts at 7 for hardest difficulty (0 difficulty level)
    # and decreases by 1 for each easier level revealed
    final_score = max(0, 7 - difficulty_level) if is_correct else 0
    
    # Track stats if user is logged in
    user = get_user_from_session()
    if user:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user has already played this song
        existing_stat = conn.execute('''
            SELECT * FROM user_stats 
            WHERE user_id = ? AND song_id = ?
        ''', (user['id'], current_song['id'])).fetchone()
        
        if existing_stat and existing_stat['has_played']:
            # User has already played this song, don't allow another attempt
            conn.close()
            return jsonify({
                'correct': False,
                'correct_answer': f"{current_song['title']} by {current_song['artist']}",
                'score': 0,
                'difficulty_level': difficulty_level,
                'already_played': True,
                'message': 'You have already played this song. Wait for the next song to be active.'
            })
        
        if existing_stat:
            # Update existing stat and mark as played
            guess_count = existing_stat['guess_count'] + 1
            cursor.execute('''
                UPDATE user_stats 
                SET guess_count = ?, correct_guess = ?, difficulty_level = ?, 
                    guessed_at = ?, has_played = 1
                WHERE user_id = ? AND song_id = ?
            ''', (guess_count, is_correct, difficulty_level, 
                  datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                  user['id'], current_song['id']))
        else:
            # Create new stat and mark as played
            cursor.execute('''
                INSERT INTO user_stats (user_id, song_id, guess_count, correct_guess, 
                                       difficulty_level, guessed_at, has_played)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            ''', (user['id'], current_song['id'], 1, is_correct, difficulty_level,
                  datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        conn.commit()
        conn.close()
        
        # Update global song stats
        update_song_stats(current_song['id'], final_score, is_correct)
    
    return jsonify({
        'correct': is_correct,
        'correct_answer': f"{current_song['title']} by {current_song['artist']}",
        'score': final_score,
        'difficulty_level': difficulty_level,
        'already_played': False
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
@admin_required
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
        
        # Add song to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO songs (title, artist, album, week, upload_date, has_frequency_versions, base_filename, spotify_id, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, artist, album, week, datetime.now().strftime('%Y-%m-%d'), True, base_filename, spotify_id, 0))
        
        song_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'Successfully processed {title} by {artist} ({start_time}s - {end_time}s)',
            'song_id': song_id
        })
        
    except Exception as e:
        print(f"Error processing Spotify song: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/set_active/<int:song_id>', methods=['POST'])
@admin_required
def set_active(song_id):
    conn = get_db_connection()
    conn.execute('UPDATE songs SET is_active = 0')
    conn.execute('UPDATE songs SET is_active = 1 WHERE id = ?', (song_id,))
    conn.commit()
    conn.close()
    
    # Reset has_played flags for all users when active song changes
    reset_has_played_for_all_users()
    
    return redirect(url_for('admin_page'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001) 