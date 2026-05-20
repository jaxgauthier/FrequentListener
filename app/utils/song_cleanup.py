"""Delete song rows and related statistics."""

from app import db
from app.models import SongStats, UserPlayerState, UserStats
from app.models.song import SongQueue


def delete_song_related_rows(song_id: int) -> None:
    """Remove FK-dependent rows before deleting a Song."""
    SongQueue.query.filter_by(song_id=song_id).delete()
    UserStats.query.filter_by(song_id=song_id).delete()
    SongStats.query.filter_by(song_id=song_id).delete()
    UserPlayerState.query.filter_by(song_id=song_id).delete()
