"""
Song model for managing audio tracks
"""

from app import db
from datetime import datetime

class Song(db.Model):
    """Song model for audio tracks"""
    __tablename__ = 'songs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    album = db.Column(db.String(200))
    week = db.Column(db.Integer, default=1)
    upload_date = db.Column(db.Date, default=datetime.utcnow().date)
    has_frequency_versions = db.Column(db.Boolean, default=False)
    base_filename = db.Column(db.String(200))
    spotify_id = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=False)
    
    # Relationships
    user_stats = db.relationship('UserStats', backref='song', lazy=True)
    song_stats = db.relationship('SongStats', backref='song', lazy=True, uselist=False)
    
    def __repr__(self):
        return f'<Song {self.title} by {self.artist}>'
    
    @property
    def available_frequencies(self):
        """Get available frequency levels for this song"""
        from app.services.audio_service import AudioService
        return AudioService.get_available_frequencies(self.base_filename) 