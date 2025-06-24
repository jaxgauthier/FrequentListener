from flask import Flask, render_template, request, jsonify, send_file
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

# Routes
@app.route('/')
def user_page():
    """User-facing game page"""
    # Get current week's song (for demo, just use the first song)
    current_song = songs[0] if songs else None
    
    return render_template('user.html', 
                         current_week=current_week,
                         current_song=current_song)

@app.route('/admin')
def admin_page():
    """Admin page for managing songs"""
    stats = {
        'total_songs': len(songs),
        'total_plays': 0,  # TODO: implement play tracking
        'this_week_plays': 0  # TODO: implement play tracking
    }
    
    return render_template('admin.html', songs=songs, stats=stats)

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
    """Delete a song"""
    global songs
    songs = [song for song in songs if song['id'] != song_id]
    return jsonify({'success': True})

@app.route('/submit_guess', methods=['POST'])
def submit_guess():
    """Handle user guess submission"""
    song_guess = request.form.get('song_guess', '').strip().lower()
    
    # Get current song
    current_song = songs[0] if songs else None
    
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
    # Map song names to their folder names
    song_folders = {
        'MrBrightside': 'MrBrighstide',  # Note the typo in the folder name
        'GhostTown': 'GhostTown',
        'Milan': 'Milan',
        'TeenageDirtbag': 'TeenageDirtbag'
    }
    
    folder_name = song_folders.get(song_name)
    if not folder_name:
        return 'Song not found', 404
    
    filepath = os.path.join('OutputWAVS', folder_name, f'reconstructed_audio_{frequency}.wav')
    
    if os.path.exists(filepath):
        return send_file(filepath)
    return 'Frequency version not found', 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 