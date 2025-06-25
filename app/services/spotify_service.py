"""
Spotify service for API interactions
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask import current_app

class SpotifyService:
    """Service for Spotify API interactions"""
    
    def __init__(self):
        """Initialize Spotify client"""
        self.client_id = current_app.config['SPOTIFY_CLIENT_ID']
        self.client_secret = current_app.config['SPOTIFY_CLIENT_SECRET']
        
        if self.client_id and self.client_secret:
            self.sp = spotipy.Spotify(
                client_credentials_manager=SpotifyClientCredentials(
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
            )
        else:
            self.sp = None
    
    def search_tracks(self, query, limit=10):
        """Search for tracks on Spotify"""
        if not self.sp:
            return []
        
        try:
            results = self.sp.search(q=query, type='track', limit=limit)
            tracks = []
            
            for item in results['tracks']['items']:
                track = {
                    'id': item['id'],
                    'name': item['name'],
                    'artist': item['artists'][0]['name'] if item['artists'] else 'Unknown',
                    'album': item['album']['name'] if item['album'] else 'Unknown',
                    'duration_ms': item['duration_ms'],
                    'popularity': item['popularity']
                }
                tracks.append(track)
            
            return tracks
            
        except Exception as e:
            current_app.logger.error(f"Error searching Spotify: {e}")
            return []
    
    def get_track(self, track_id):
        """Get track details by ID"""
        if not self.sp:
            return None
        
        try:
            track = self.sp.track(track_id)
            return {
                'id': track['id'],
                'name': track['name'],
                'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
                'album': track['album']['name'] if track['album'] else 'Unknown',
                'duration_ms': track['duration_ms'],
                'popularity': track['popularity']
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting track: {e}")
            return None 