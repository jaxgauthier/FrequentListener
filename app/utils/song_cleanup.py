"""Remove operational data for a song; keep permanent user stats."""

from app import db
from app.models import SongStats, UserPlayerState
from app.models.song import SongQueue


def clear_song_operational_data(song_id: int) -> None:
    """Queue, global song stats, and in-progress player state — not user_stats."""
    SongQueue.query.filter_by(song_id=song_id).delete()
    SongStats.query.filter_by(song_id=song_id).delete()
    UserPlayerState.query.filter_by(song_id=song_id).delete()


def archive_song(song) -> None:
    """Soft-delete: hide from admin/game but keep Song row for historical user_stats."""
    song.is_active = False
    song.is_deleted = True
    song.has_frequency_versions = False
    clear_song_operational_data(song.id)
