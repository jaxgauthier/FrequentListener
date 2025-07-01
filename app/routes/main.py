"""
Main routes for the game interface
"""

from flask import Blueprint, render_template, request, jsonify, send_file, current_app, redirect, url_for
from flask_login import current_user, login_required, logout_user, login_user
from app.models import Song, UserStats, SongStats, User, SongHistory
from app.services import StatsService, AudioService
from app.services.queue_service import QueueService
import os
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Main game page"""
    # Get current active song
    current_song = Song.query.filter_by(is_active=True).first()
    
    # Get stats for everyone
    stats = None
    if current_song:
        # Get global song stats for all users
        song_stats = SongStats.query.filter_by(song_id=current_song.id).first()
        if song_stats:
            global_stats = {
                'average_score': song_stats.average_score,
                'total_plays': song_stats.total_plays,
                'total_correct_guesses': song_stats.total_correct_guesses
            }
        else:
            global_stats = {'average_score': 0.0, 'total_plays': 0, 'total_correct_guesses': 0}
        
        # Get user-specific stats if logged in
        if current_user.is_authenticated:
            user_stats = StatsService.get_user_stats(current_user.id, current_song.id)
            stats = user_stats
            stats['song_stats'] = global_stats
        else:
            # For guests, just show global stats
            stats = {
                'has_played_current': False,
                'song_stats': global_stats,
                'individual_stats': {'points_distribution': {}, 'max_count': 1}
            }
    
    return render_template('user.html', current_song=current_song, stats=stats)

@bp.route('/play_frequency/<song_name>/<frequency>')
def play_frequency_audio(song_name, frequency):
    """Serve frequency-specific audio files"""
    try:
        song_folder = os.path.join(current_app.config['AUDIO_OUTPUT_FOLDER'], song_name)
        
        if not os.path.exists(song_folder):
            # Fallback to old mapping system
            song_folders = {
                'MrBrightside': 'MrBrighstide',
                'GhostTown': 'GhostTown',
                'Milan': 'Milan',
                'TeenageDirtbag': 'TeenageDirtbag'
            }
            
            folder_name = song_folders.get(song_name)
            if not folder_name:
                return 'Song not found', 404
            song_folder = os.path.join(current_app.config['AUDIO_OUTPUT_FOLDER'], folder_name)
        
        filepath = os.path.join(song_folder, f'reconstructed_audio_{frequency}.wav')
        
        if os.path.exists(filepath):
            return send_file(filepath)
        return 'Frequency version not found', 404
    except Exception as e:
        current_app.logger.error(f"Error in play_frequency_audio: {e}")
        return f'Error: {str(e)}', 500

@bp.route('/submit_guess', methods=['POST'])
def submit_guess():
    """Handle song guess submission"""
    data = request.get_json()
    song_guess = data.get('song_guess', '').strip().lower()
    difficulty_level = data.get('difficulty_level', 0)
    
    # Get current active song
    current_song = Song.query.filter_by(is_active=True).first()
    if not current_song:
        return jsonify({'error': 'No active song'}), 400
    
    # Check if guess is correct
    correct_title = current_song.title.lower()
    correct_artist = current_song.artist.lower()
    correct_title_artist = f"{correct_title} - {correct_artist}"
    
    is_correct = (
        song_guess == correct_title or 
        song_guess == correct_artist or 
        song_guess == correct_title_artist
    )
    
    # Calculate final score
    final_score = max(0, 8 - difficulty_level) if is_correct else 0
    
    # Always update global song stats
    StatsService.update_song_stats(current_song.id, final_score, is_correct)
    
    # Update user stats if user is logged in
    if current_user.is_authenticated:
        StatsService.update_user_stats(
            current_user.id, 
            current_song.id, 
            final_score, 
            is_correct, 
            difficulty_level
        )
    
    return jsonify({
        'correct': is_correct,
        'correct_answer': f"{current_song.title} by {current_song.artist}",
        'score': final_score,
        'difficulty_level': difficulty_level,
        'already_played': False
    })

@bp.route('/current_stats')
def current_stats():
    """Get current song statistics"""
    current_song = Song.query.filter_by(is_active=True).first()
    if not current_song:
        return jsonify({'error': 'No active song'}), 400
    
    # Get global song stats for all users
    song_stats = SongStats.query.filter_by(song_id=current_song.id).first()
    if song_stats:
        global_stats = {
            'average_score': song_stats.average_score,
            'total_plays': song_stats.total_plays,
            'total_correct_guesses': song_stats.total_correct_guesses
        }
    else:
        global_stats = {'average_score': 0.0, 'total_plays': 0, 'total_correct_guesses': 0}
    
    # If user is not authenticated, return basic song info and global stats only
    if not current_user.is_authenticated:
        return jsonify({
            'success': True,
            'song': {
                'title': current_song.title,
                'artist': current_song.artist
            },
            'stats': {
                'has_played_current': False,
                'song_stats': global_stats,
                'individual_stats': {'points_distribution': {}, 'max_count': 1}
            }
        })
    
    # For authenticated users, get full stats
    stats = StatsService.get_user_stats(current_user.id, current_song.id)
    stats['song_stats'] = global_stats
    
    return jsonify({
        'success': True,
        'song': {
            'title': current_song.title,
            'artist': current_song.artist
        },
        'stats': stats
    })

@bp.route('/profile')
@login_required
def profile():
    """User profile page with stats"""
    # Get comprehensive user stats for profile page
    stats = StatsService.get_profile_stats(current_user.id)
    return render_template('profile.html', user=current_user, stats=stats)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')
        
        # Check if admin credentials are correct
        if username == 'admin' and password == 'admin123':  # Change these credentials
            # In a real app, you'd use proper authentication
            if request.is_json:
                return jsonify({'success': True, 'redirect': url_for('main.admin_panel')})
            else:
                return redirect(url_for('main.admin_panel'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Invalid credentials'})
            else:
                return render_template('admin_login.html', error='Invalid credentials')
    
    return render_template('admin_login.html')

@bp.route('/admin')
def admin_panel():
    """Admin panel page"""
    # Get all songs
    songs = Song.query.all()
    
    # Get basic stats
    stats = {
        'total_songs': Song.query.count(),
        'total_plays': 0,  # You can implement this later
        'this_week_plays': 0  # You can implement this later
    }
    
    return render_template('admin.html', songs=songs, stats=stats)

@bp.route('/admin/set_active/<int:song_id>', methods=['POST'])
def set_active(song_id):
    """Set a song as active"""
    # Set all songs as inactive first
    Song.query.update({Song.is_active: False})
    
    # Set the selected song as active
    song = Song.query.get_or_404(song_id)
    song.is_active = True
    
    from app import db
    db.session.commit()
    
    return redirect(url_for('main.admin_panel'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        # Handle both form data and JSON
        if request.is_json:
            data = request.get_json()
            identifier = data.get('identifier')
            password = data.get('password')
        else:
            identifier = request.form.get('identifier')
            password = request.form.get('password')
        
        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if request.is_json:
                return jsonify({'success': True, 'message': 'Login successful'})
            else:
                return redirect(url_for('main.index'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Invalid username/email or password'})
            else:
                return render_template('login.html', error='Invalid username/email or password')
    return render_template('login.html')

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """User signup page"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if not username or not email or not password:
            return render_template('signup.html', error='All fields are required')
        if User.query.filter_by(username=username).first():
            return render_template('signup.html', error='Username already exists')
        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error='Email already exists')
        user = User(username=username, email=email, password_hash=generate_password_hash(password))
        from app import db
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('signup.html')

@bp.route('/spotify_search')
def spotify_search():
    """Search Spotify for tracks"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'tracks': []})
    
    try:
        # Import spotipy here to avoid circular imports
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        
        # Initialize Spotify client
        client_credentials_manager = SpotifyClientCredentials(
            client_id=os.environ.get('SPOTIFY_CLIENT_ID'),
            client_secret=os.environ.get('SPOTIFY_CLIENT_SECRET')
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        # Search for tracks
        results = sp.search(q=query, type='track', limit=5)
        
        tracks = []
        if results and 'tracks' in results and 'items' in results['tracks']:
            for track in results['tracks']['items']:
                if track:
                    tracks.append({
                        'name': track.get('name', 'Unknown Title'),
                        'artist': track.get('artists', [{}])[0].get('name', 'Unknown Artist') if track.get('artists') else 'Unknown Artist',
                        'album': track.get('album', {}).get('name', 'Unknown Album') if track.get('album') else 'Unknown Album',
                        'spotify_id': track.get('id', ''),
                        'duration_ms': track.get('duration_ms', 0)
                    })
        
        return jsonify({'tracks': tracks})
        
    except Exception as e:
        print(f"Spotify search error: {e}")
        return jsonify({'tracks': [], 'error': str(e)})

@bp.route('/admin/process_spotify_song', methods=['POST'])
def process_spotify_song():
    """Process a Spotify song and add it to the game"""
    try:
        data = request.get_json()
        
        title = data.get('title')
        artist = data.get('artist')
        album = data.get('album', 'Unknown Album')
        week = data.get('week', 1)
        start_time = data.get('start_time', 0)
        end_time = data.get('end_time', 10)
        spotify_id = data.get('spotify_id')
        
        if not title or not artist:
            return jsonify({
                'success': False,
                'error': 'Title and artist are required'
            })
        
        # Create a safe filename for the song
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_artist = "".join(c for c in artist if c.isalnum() or c in (' ', '-', '_')).rstrip()
        song_folder_name = f"{safe_artist}_{safe_title}".replace(' ', '')
        
        # Check if song already exists
        existing_song = Song.query.filter_by(title=title, artist=artist).first()
        if existing_song:
            return jsonify({
                'success': False,
                'error': f"Song '{title}' by {artist} already exists in the database"
            })
        
        # Create output directory
        output_dir = os.path.join(current_app.config['AUDIO_OUTPUT_FOLDER'], song_folder_name)
        os.makedirs(output_dir, exist_ok=True)
        
        # Download audio from YouTube
        temp_audio_path = os.path.join(output_dir, 'temp_audio.wav')
        download_success = AudioService.download_from_youtube(
            title, artist, temp_audio_path, start_time, end_time
        )
        
        if not download_success:
            return jsonify({
                'success': False,
                'error': f"Failed to download audio for '{title}' by {artist}"
            })
        
        # Process through DFT pipeline
        process_success = AudioService.process_through_dft(
            temp_audio_path, song_folder_name, f"{safe_title}_{safe_artist}"
        )
        
        # Clean up temp file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        
        if not process_success:
            return jsonify({
                'success': False,
                'error': f"Failed to process audio through DFT pipeline for '{title}' by {artist}"
            })
        
        # Add song to database
        new_song = Song(
            title=title,
            artist=artist,
            album=album,
            week=week,
            base_filename=song_folder_name,
            spotify_id=spotify_id,
            has_frequency_versions=True,
            is_active=False  # Don't make it active by default
        )
        
        from app import db
        db.session.add(new_song)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f"Successfully processed '{title}' by {artist}. Song added to database with ID: {new_song.id}"
        })
        
    except Exception as e:
        current_app.logger.error(f"Error processing Spotify song: {e}")
        return jsonify({
            'success': False,
            'error': f"Processing failed: {str(e)}"
        })

@bp.route('/admin/delete/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    """Delete a song from the database"""
    try:
        song = Song.query.get_or_404(song_id)
        
        # Delete queue entries first (foreign key constraint)
        from app.models.song import SongQueue
        SongQueue.query.filter_by(song_id=song_id).delete()
        
        # Delete the song
        from app import db
        db.session.delete(song)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@bp.route('/admin/queue_week', methods=['POST'])
def queue_week():
    """Queue songs for the current week"""
    try:
        data = request.get_json()
        song_ids = data.get('song_ids', [])
        
        if len(song_ids) > 7:
            return jsonify({
                'success': False,
                'error': 'Maximum 7 songs allowed per week'
            })
        
        success = QueueService.queue_songs_for_week(song_ids)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Successfully queued {len(song_ids)} songs for the week'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to queue songs'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@bp.route('/admin/activate_today')
def activate_today():
    """Activate today's song"""
    try:
        song = QueueService.activate_todays_song()
        
        if song:
            return jsonify({
                'success': True,
                'message': f'Activated {song.title} by {song.artist} for today'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No song queued for today'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@bp.route('/admin/queue_status')
def queue_status():
    """Get current queue status"""
    try:
        current_queue = QueueService.get_current_week_queue()
        next_queue = QueueService.get_next_week_queue()
        
        current_songs = []
        for entry in current_queue:
            current_songs.append({
                'id': entry.song.id,
                'title': entry.song.title,
                'artist': entry.song.artist,
                'date': entry.scheduled_date.strftime('%Y-%m-%d'),
                'status': entry.status,
                'is_active': entry.song.is_active
            })
        
        next_songs = []
        for entry in next_queue:
            next_songs.append({
                'id': entry.song.id,
                'title': entry.song.title,
                'artist': entry.song.artist,
                'date': entry.scheduled_date.strftime('%Y-%m-%d'),
                'status': entry.status
            })
        
        return jsonify({
            'success': True,
            'current_week': current_songs,
            'next_week': next_songs
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@bp.route('/admin/clear_queue', methods=['POST'])
def clear_queue():
    """Clear the current week's queue"""
    try:
        from datetime import date, timedelta
        
        # Get the start of the current week (Monday)
        today = date.today()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        
        # Clear queue entries for this week
        from app.models.song import SongQueue
        deleted_count = SongQueue.query.filter(
            SongQueue.scheduled_date >= week_start,
            SongQueue.scheduled_date < week_start + timedelta(days=7)
        ).delete()
        
        from app import db
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Cleared {deleted_count} songs from the current week queue'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@bp.route('/song_history')
def song_history():
    """Display song history page"""
    # Get all song history entries, ordered by most recent first
    history_entries = SongHistory.get_all_history()
    
    # Group by date for better display
    history_by_date = {}
    for entry in history_entries:
        date_str = entry.played_date.strftime('%Y-%m-%d')
        if date_str not in history_by_date:
            history_by_date[date_str] = []
        history_by_date[date_str].append({
            'title': entry.title,
            'artist': entry.artist,
            'album': entry.album
        })
    
    return render_template('song_history.html', history_by_date=history_by_date)

@bp.route('/api/song_history')
def api_song_history():
    """API endpoint to get song history data"""
    try:
        # Get optional date range parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if start_date_str and end_date_str:
            from datetime import datetime
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            history_entries = SongHistory.get_history_by_date_range(start_date, end_date)
        else:
            history_entries = SongHistory.get_all_history()
        
        # Format the data
        history_data = []
        for entry in history_entries:
            history_data.append({
                'id': entry.id,
                'title': entry.title,
                'artist': entry.artist,
                'album': entry.album,
                'played_date': entry.played_date.strftime('%Y-%m-%d'),
                'created_at': entry.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'history': history_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }) 