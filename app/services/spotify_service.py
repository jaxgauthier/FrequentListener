"""
Spotify service for API interactions
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask import current_app


class SpotifyService:
    """Service for Spotify API interactions"""

    MISSING_CREDS_MESSAGE = (
        'Spotify API credentials are missing. Create an app at '
        'https://developer.spotify.com/dashboard then set SPOTIFY_CLIENT_ID and '
        'SPOTIFY_CLIENT_SECRET in a .env file in the project root.'
    )

    def __init__(self):
        self.client_id = (current_app.config.get('SPOTIFY_CLIENT_ID') or '').strip()
        self.client_secret = (current_app.config.get('SPOTIFY_CLIENT_SECRET') or '').strip()

        if self.client_id and self.client_secret:
            self.sp = spotipy.Spotify(
                client_credentials_manager=SpotifyClientCredentials(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                )
            )
        else:
            self.sp = None

    @classmethod
    def search_for_api(cls, query: str, limit: int = 5) -> dict:
        """Search tracks; response shape matches /spotify_search JSON."""
        query = (query or '').strip()
        if not query:
            return {'tracks': []}

        service = cls()
        if not service.sp:
            return {
                'tracks': [],
                'error': cls.MISSING_CREDS_MESSAGE,
                'missing_credentials': True,
            }

        try:
            return {'tracks': service.search_tracks(query, limit=limit)}
        except Exception as exc:
            current_app.logger.warning('Spotify search error: %s', exc)
            return {'tracks': [], 'error': str(exc)}

    def search_tracks(self, query, limit=10):
        if not self.sp:
            return []

        try:
            results = self.sp.search(q=query, type='track', limit=limit)
            tracks = []

            for item in results['tracks']['items']:
                tracks.append({
                    'name': item.get('name', 'Unknown Title'),
                    'artist': (
                        item['artists'][0]['name']
                        if item.get('artists')
                        else 'Unknown Artist'
                    ),
                    'album': item.get('album', {}).get('name', 'Unknown Album'),
                    'spotify_id': item.get('id', ''),
                    'duration_ms': item.get('duration_ms', 0),
                })

            return tracks

        except Exception as e:
            current_app.logger.error('Error searching Spotify: %s', e)
            return []

    def get_track(self, track_id):
        if not self.sp:
            return None

        try:
            track = self.sp.track(track_id)
            return {
                'spotify_id': track['id'],
                'name': track['name'],
                'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
                'album': track['album']['name'] if track['album'] else 'Unknown',
                'duration_ms': track['duration_ms'],
            }

        except Exception as e:
            current_app.logger.error('Error getting track: %s', e)
            return None
