"""
Main routes for the game interface
"""

from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from flask_login import current_user, login_required
from app.models import Song, UserStats, SongStats
from app.services import StatsService
import os

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Main game page"""
    # Get current active song
    current_song = Song.query.filter_by(is_active=True).first()
    
    # Get user stats if logged in
    stats = None
    if current_user.is_authenticated:
        stats = StatsService.get_user_stats(current_user.id, current_song.id if current_song else None)
    
    return render_template('user.html', current_song=current_song, user=current_user, stats=stats)

@bp.route('/play_frequency/<song_name>/<frequency>')
def play_frequency_audio(song_name, frequency):
    """Serve frequency-specific audio files"""
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
    final_score = max(0, 7 - difficulty_level) if is_correct else 0
    
    # Update stats if user is logged in
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
    if not current_user.is_authenticated:
        return jsonify({'error': 'User not authenticated'}), 400
    
    current_song = Song.query.filter_by(is_active=True).first()
    if not current_song:
        return jsonify({'error': 'No active song'}), 400
    
    stats = StatsService.get_user_stats(current_user.id, current_song.id)
    return jsonify(stats) 