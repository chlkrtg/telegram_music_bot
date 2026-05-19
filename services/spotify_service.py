import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from services.cache_service import cached


class SpotifyService:
    def __init__(self):
        self.auth_manager = SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        )
        self.client = spotipy.Spotify(auth_manager=self.auth_manager)

    @cached(ttl_seconds=3600)
    def search_track(self, query: str, limit: int = 1):
        """Поиск трека в Spotify"""
        results = self.client.search(q=query, type='track', limit=limit)
        return results.get('tracks', {}).get('items', [])

    @cached(ttl_seconds=7200)
    def get_top_tracks(self, artist_name: str, limit: int = 5):
        """Получение топ треков артиста"""
        results = self.client.search(
            q=f"artist:{artist_name}",
            type='track',
            limit=limit
        )
        return results.get('tracks', {}).get('items', [])

    @staticmethod
    def format_track_info(track: dict):
        """Форматирует информацию о треке"""
        album_images = track['album']['images']
        album_image_url = album_images[0]['url'] if album_images else None

        return {
            'artist_name': track['artists'][0]['name'],
            'artists_list': [artist['name'] for artist in track['artists']],
            'artists_str': ", ".join([artist['name'] for artist in track['artists']]),
            'track_name': track['name'],
            'album_name': track['album']['name'],
            'release_year': track['album']['release_date'][:4],
            'preview_url': track.get('preview_url'),
            'spotify_url': track['external_urls']['spotify'],
            'album_url': track['album']['external_urls']['spotify'],
            'album_image_url': album_image_url
        }

    def get_track_info(self, query: str):
        """Полная информация о треке по запросу"""
        tracks = self.search_track(query)
        if not tracks:
            return None
        return self.format_track_info(tracks[0])
