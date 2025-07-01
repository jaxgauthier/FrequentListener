# pyright: reportGeneralTypeIssues=false
"""
Song model for the Audio Frequency Game
"""

from app import db
from datetime import datetime, date, timedelta

class Song(db.Model):
    """Song model for storing song information"""
    __tablename__ = 'songs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    album = db.Column(db.String(200), nullable=True)
    week = db.Column(db.Integer, default=1)
    base_filename = db.Column(db.String(200), nullable=False)
    spotify_id = db.Column(db.String(100), nullable=True)
    has_frequency_versions = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def available_frequencies(self):
        """Get available frequency versions for this song"""
        from app.services.audio_service import AudioService
        return AudioService.get_available_frequencies(self.base_filename)

class SongHistory(db.Model):
    """Song history model for tracking all songs that have been played"""
    __tablename__ = 'song_history'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    album = db.Column(db.String(200), nullable=True)
    played_date = db.Column(db.Date, nullable=False)  # The date this song was played
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @classmethod
    def add_to_history(cls, song):
        """Add a song to the history"""
        # Check if this song is already in history for this date
        existing = cls.query.filter_by(
            title=song.title,
            artist=song.artist,
            played_date=date.today()
        ).first()
        
        if not existing:
            history_entry = cls(
                title=song.title,
                artist=song.artist,
                album=song.album,
                played_date=date.today()
            )
            db.session.add(history_entry)
            db.session.commit()
    
    @classmethod
    def get_all_history(cls):
        """Get all song history entries"""
        return cls.query.order_by(cls.played_date.desc()).all()
    
    @classmethod
    def get_history_by_date_range(cls, start_date, end_date):
        """Get song history for a specific date range"""
        return cls.query.filter(
            cls.played_date >= start_date,
            cls.played_date <= end_date
        ).order_by(cls.played_date.desc()).all()

class SongQueue(db.Model):
    """Song queue model for weekly scheduling"""
    __tablename__ = 'song_queue'
    
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False)  # Which day it plays
    status = db.Column(db.String(20), default='queued')  # queued, active, completed, deleted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # When to delete files
    
    # Relationship
    song = db.relationship('Song', backref='queue_entries')
    
    @classmethod
    def get_active_song_for_date(cls, target_date=None):
        """Get the active song for a specific date"""
        if target_date is None:
            target_date = date.today()
        
        queue_entry = cls.query.filter_by(
            scheduled_date=target_date,
            status='active'
        ).first()
        
        if queue_entry:
            return queue_entry.song
        return None
    
    @classmethod
    def get_week_queue(cls, start_date=None):
        """Get all songs queued for a week starting from start_date"""
        if start_date is None:
            start_date = date.today()
        
        # Get the start of the week (Monday)
        days_since_monday = start_date.weekday()
        week_start = start_date - timedelta(days=days_since_monday)
        
        # Get all songs for the week
        week_entries = cls.query.filter(
            cls.scheduled_date >= week_start,
            cls.scheduled_date < week_start + timedelta(days=7)
        ).order_by(cls.scheduled_date).all()
        
        return week_entries 