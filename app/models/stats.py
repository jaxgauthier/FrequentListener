"""
Statistics models for tracking user performance and song analytics
"""

from app import db
from datetime import datetime
import json

class UserStats(db.Model):
    """User statistics for individual songs"""
    __tablename__ = 'user_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    guess_count = db.Column(db.Integer, default=0)
    correct_guess = db.Column(db.Boolean, default=False)
    difficulty_level = db.Column(db.Integer, default=0)
    guessed_at = db.Column(db.DateTime, default=datetime.utcnow)
    has_played = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<UserStats {self.user_id} - {self.song_id}>'

class SongStats(db.Model):
    """Global statistics for songs"""
    __tablename__ = 'song_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    total_plays = db.Column(db.Integer, default=0)
    total_correct_guesses = db.Column(db.Integer, default=0)
    average_score = db.Column(db.Float, default=0.0)
    points_distribution = db.Column(db.Text, default='{}')  # JSON string
    
    def __repr__(self):
        return f'<SongStats {self.song_id}>'
    
    @property
    def points_distribution_dict(self):
        """Get points distribution as dictionary"""
        try:
            return json.loads(self.points_distribution)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @points_distribution_dict.setter
    def points_distribution_dict(self, value):
        """Set points distribution from dictionary"""
        self.points_distribution = json.dumps(value) 