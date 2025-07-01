"""
Queue service for managing weekly song scheduling
"""

from datetime import datetime, date, timedelta
from app.models.song import Song, SongQueue, SongHistory
from app import db
import os
import shutil

class QueueService:
    """Service for managing the weekly song queue"""
    
    @staticmethod
    def queue_songs_for_week(song_ids, start_date=None):
        """Queue songs for a week starting from start_date"""
        if start_date is None:
            start_date = date.today()
        
        # Get the start of the week (Monday)
        days_since_monday = start_date.weekday()
        week_start = start_date - timedelta(days=days_since_monday)
        
        # Clear any existing queue for this week
        QueueService.clear_week_queue(week_start)
        
        # Queue the new songs
        for i, song_id in enumerate(song_ids):
            if i >= 7:  # Only queue 7 songs max
                break
                
            song = Song.query.get(song_id)
            if not song:
                continue
            
            # Calculate the date for this song (Monday = 0, Sunday = 6)
            song_date = week_start + timedelta(days=i)
            
            # Create queue entry
            queue_entry = SongQueue(
                song_id=song_id,
                scheduled_date=song_date,
                status='queued',
                expires_at=week_start + timedelta(days=14)  # Delete after 2 weeks
            )
            
            db.session.add(queue_entry)
        
        db.session.commit()
        return True
    
    @staticmethod
    def clear_week_queue(start_date):
        """Clear all queue entries for a specific week"""
        week_end = start_date + timedelta(days=7)
        
        # Mark existing entries as deleted
        SongQueue.query.filter(
            SongQueue.scheduled_date >= start_date,
            SongQueue.scheduled_date < week_end
        ).update({'status': 'deleted'})
        
        db.session.commit()
    
    @staticmethod
    def activate_todays_song():
        """Activate today's song and deactivate others"""
        today = date.today()
        
        # Deactivate all currently active songs
        Song.query.update({'is_active': False})
        
        # Get today's queue entry
        queue_entry = SongQueue.query.filter_by(
            scheduled_date=today,
            status='queued'
        ).first()
        
        if queue_entry:
            # Activate the song
            queue_entry.song.is_active = True
            queue_entry.status = 'active'
            
            # Add to song history
            SongHistory.add_to_history(queue_entry.song)
            
            db.session.commit()
            return queue_entry.song
        
        return None
    
    @staticmethod
    def cleanup_expired_songs():
        """Delete audio files and database records for expired songs, but preserve song history"""
        expired_entries = SongQueue.query.filter(
            SongQueue.expires_at <= datetime.utcnow(),
            SongQueue.status.in_(['completed', 'deleted'])
        ).all()
        
        for entry in expired_entries:
            if entry.song:
                # Delete audio files
                QueueService.delete_song_files(entry.song.base_filename)
                
                # Delete all related stats
                from app.models import UserStats, SongStats
                UserStats.query.filter_by(song_id=entry.song.id).delete()
                SongStats.query.filter_by(song_id=entry.song.id).delete()
                
                # Delete the song record itself
                db.session.delete(entry.song)
                
                # Delete the queue entry
                db.session.delete(entry)
        
        db.session.commit()
    
    @staticmethod
    def delete_song_files(base_filename):
        """Delete audio files for a song"""
        from flask import current_app
        
        audio_dir = os.path.join(current_app.config['AUDIO_OUTPUT_FOLDER'], base_filename)
        if os.path.exists(audio_dir):
            try:
                shutil.rmtree(audio_dir)
                print(f"Deleted audio files for {base_filename}")
            except Exception as e:
                print(f"Error deleting audio files for {base_filename}: {e}")
    
    @staticmethod
    def get_current_week_queue():
        """Get the current week's queue"""
        return SongQueue.get_week_queue()
    
    @staticmethod
    def get_next_week_queue():
        """Get next week's queue"""
        next_week_start = date.today() + timedelta(days=7)
        return SongQueue.get_week_queue(next_week_start)
    
    @staticmethod
    def is_song_queued(song_id, target_date=None):
        """Check if a song is queued for a specific date"""
        if target_date is None:
            target_date = date.today()
        
        return SongQueue.query.filter_by(
            song_id=song_id,
            scheduled_date=target_date,
            status='queued'
        ).first() is not None 