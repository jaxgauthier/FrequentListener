"""
Statistics service for managing user and song analytics
"""

from app.models import UserStats, SongStats, Song
from app import db
from datetime import datetime
import json

class StatsService:
    """Service for managing statistics"""
    
    @staticmethod
    def get_user_stats(user_id, current_song_id=None):
        """Get user statistics for current song and all-time"""
        try:
            # Get current song stats
            current_song_stats = None
            has_played_current = False
            
            if current_song_id:
                current_song = Song.query.get(current_song_id)
                if current_song:
                    # Check if user has played current song
                    user_stat = UserStats.query.filter_by(
                        user_id=user_id, 
                        song_id=current_song_id
                    ).first()
                    
                    has_played_current = user_stat and user_stat.has_played
                    
                    # Get song stats
                    song_stats = SongStats.query.filter_by(song_id=current_song_id).first()
                    if song_stats:
                        current_song_stats = {
                            'average_score': song_stats.average_score,
                            'total_plays': song_stats.total_plays,
                            'total_correct_guesses': song_stats.total_correct_guesses
                        }
            
            # Get all-time user stats for bar chart
            all_user_stats = UserStats.query.filter_by(user_id=user_id).all()
            points_distribution = {}
            
            for stat in all_user_stats:
                if stat.correct_guess:
                    score = max(0, 7 - stat.difficulty_level)
                    points_distribution[score] = points_distribution.get(score, 0) + 1
            
            # Calculate max count for bar chart scaling
            max_count = max(points_distribution.values()) if points_distribution else 1
            
            individual_stats = {
                'points_distribution': points_distribution,
                'max_count': max_count
            }
            
            return {
                'has_played_current': has_played_current,
                'song_stats': current_song_stats or {'average_score': 0.0},
                'individual_stats': individual_stats
            }
            
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {
                'has_played_current': False,
                'song_stats': {'average_score': 0.0},
                'individual_stats': {'points_distribution': {}, 'max_count': 1}
            }
    
    @staticmethod
    def update_user_stats(user_id, song_id, final_score, is_correct, difficulty_level):
        """Update user statistics for a song"""
        try:
            # Check if user has already played this song
            existing_stat = UserStats.query.filter_by(
                user_id=user_id, 
                song_id=song_id
            ).first()
            
            if existing_stat and existing_stat.has_played:
                return False  # User has already played
            
            if existing_stat:
                # Update existing stat
                existing_stat.guess_count += 1
                existing_stat.correct_guess = is_correct
                existing_stat.difficulty_level = difficulty_level
                existing_stat.guessed_at = datetime.utcnow()
                existing_stat.has_played = True
            else:
                # Create new stat
                new_stat = UserStats(
                    user_id=user_id,
                    song_id=song_id,
                    guess_count=1,
                    correct_guess=is_correct,
                    difficulty_level=difficulty_level,
                    guessed_at=datetime.utcnow(),
                    has_played=True
                )
                db.session.add(new_stat)
            
            db.session.commit()
            
            # Update global song stats
            StatsService.update_song_stats(song_id, final_score, is_correct)
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating user stats: {e}")
            return False
    
    @staticmethod
    def update_song_stats(song_id, final_score, is_correct):
        """Update global song statistics"""
        try:
            song_stats = SongStats.query.filter_by(song_id=song_id).first()
            
            if not song_stats:
                # Create new song stats
                song_stats = SongStats(
                    song_id=song_id,
                    total_plays=1,
                    total_correct_guesses=1 if is_correct else 0,
                    average_score=float(final_score) if is_correct else 0.0,
                    points_distribution=json.dumps({int(final_score): 1} if is_correct else {})
                )
                db.session.add(song_stats)
            else:
                # Update existing stats
                song_stats.total_plays += 1
                if is_correct:
                    song_stats.total_correct_guesses += 1
                
                # Update points distribution
                points_dist = song_stats.points_distribution_dict
                # Convert string keys to integers
                points_dist = {int(k): v for k, v in points_dist.items()}
                
                if is_correct:
                    final_score_int = int(final_score)
                    points_dist[final_score_int] = points_dist.get(final_score_int, 0) + 1
                
                song_stats.points_distribution_dict = points_dist
                
                # Recalculate average
                total_score = sum(score * count for score, count in points_dist.items())
                total_correct = sum(points_dist.values())
                song_stats.average_score = total_score / total_correct if total_correct > 0 else 0.0
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating song stats: {e}")
            import traceback
            traceback.print_exc()
    
    @staticmethod
    def reset_has_played_for_all_users():
        """Reset has_played flag for all users when active song changes"""
        try:
            UserStats.query.update({UserStats.has_played: False})
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error resetting has_played flags: {e}")
    
    @staticmethod
    def get_profile_stats(user_id):
        """Get comprehensive user stats for profile page"""
        try:
            # Get all user stats
            all_user_stats = UserStats.query.filter_by(user_id=user_id).all()
            
            # Calculate basic stats
            total_guesses = sum(stat.guess_count for stat in all_user_stats)
            correct_guesses = sum(1 for stat in all_user_stats if stat.correct_guess)
            songs_attempted = len(all_user_stats)
            accuracy = (correct_guesses / total_guesses * 100) if total_guesses > 0 else 0
            
            # Get recent activity (last 10 guesses)
            recent_stats = UserStats.query.filter_by(user_id=user_id)\
                .order_by(UserStats.guessed_at.desc())\
                .limit(10)\
                .all()
            
            recent_activity = []
            for stat in recent_stats:
                song = Song.query.get(stat.song_id)
                if song:
                    recent_activity.append({
                        'title': song.title,
                        'artist': song.artist,
                        'correct_guess': stat.correct_guess,
                        'difficulty_level': stat.difficulty_level,
                        'guessed_at': stat.guessed_at.strftime('%Y-%m-%d %H:%M:%S') if stat.guessed_at else 'Unknown'
                    })
            
            return {
                'total_guesses': total_guesses,
                'correct_guesses': correct_guesses,
                'accuracy': accuracy,
                'songs_attempted': songs_attempted,
                'recent_activity': recent_activity
            }
            
        except Exception as e:
            print(f"Error getting profile stats: {e}")
            return {
                'total_guesses': 0,
                'correct_guesses': 0,
                'accuracy': 0.0,
                'songs_attempted': 0,
                'recent_activity': []
            } 