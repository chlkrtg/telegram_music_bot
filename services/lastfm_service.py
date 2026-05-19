import aiohttp
from services.cache_service import cached

from typing import List, Dict, Optional
from config import LASTFM_API_KEY


class LastFMService:
    def __init__(self):
        self.api_key = LASTFM_API_KEY

        if not self.api_key:
            raise ValueError("LASTFM_API_KEY not found in .env file or parameter")

        self.base_url = "https://ws.audioscrobbler.com/2.0/"
        self.headers = {
            'User-Agent': 'MusicBot/1.0 (https://t.me/music_bot)'
        }

    @cached(ttl_seconds=3600)
    async def get_similar_artists(self, artist_name: str, limit: int = 10) -> List[Dict]:
        """Получает список похожих артистов из Last.fm"""
        params = {
            'method': 'artist.getsimilar',
            'artist': artist_name,
            'api_key': self.api_key,
            'format': 'json',
            'limit': limit
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        self.base_url,
                        params=params,
                        headers=self.headers,
                        timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    if 'error' in data:
                        print(f"Last.fm API error: {data['message']}")
                        return []

                    similar = []
                    for artist in data.get('similarartists', {}).get('artist', []):
                        similar.append({
                            'name': artist['name'],
                            'match': float(artist.get('match', 0)) * 100,
                            'url': artist.get('url', '')
                        })
                    return similar

        except aiohttp.ClientError as e:
            print(f"Last.fm request error: {e}")
            return []
        except Exception as e:
            print(f"Last.fm unexpected error: {e}")
            return []

    @cached(ttl_seconds=3600)
    async def search_artist(self, query: str) -> List[str]:
        """Поиск артиста по названию"""
        params = {
            'method': 'artist.search',
            'artist': query,
            'api_key': self.api_key,
            'format': 'json',
            'limit': 5
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        self.base_url,
                        params=params,
                        headers=self.headers,
                        timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    artists = data.get('results', {}).get('artistmatches', {}).get('artist', [])
                    return [a['name'] for a in artists]
        except Exception as e:
            print(f"Search error: {e}")
            return []

    async def get_artist_info(self, artist_name: str) -> Optional[Dict]:
        """Получает подробную информацию об артисте"""
        params = {
            'method': 'artist.getinfo',
            'artist': artist_name,
            'api_key': self.api_key,
            'format': 'json'
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        self.base_url,
                        params=params,
                        headers=self.headers,
                        timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    if 'error' in data:
                        return None

                    artist = data.get('artist', {})

                    tags = []
                    for tag in artist.get('tags', {}).get('tag', []):
                        if isinstance(tag, dict) and 'name' in tag:
                            tags.append(tag['name'])

                    return {
                        'name': artist.get('name'),
                        'listeners': artist.get('stats', {}).get('listeners'),
                        'playcount': artist.get('stats', {}).get('playcount'),
                        'bio': artist.get('bio', {}).get('summary', '')[:500],
                        'tags': tags[:5],
                        'url': artist.get('url')
                    }

        except Exception as e:
            print(f"Error getting artist info: {e}")
            return None
