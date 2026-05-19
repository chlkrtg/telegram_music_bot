import asyncio
from services.cache_service import cached
import lyricsgenius
from config import GENIUS_ACCESS_TOKEN


class GeniusService:
    def __init__(self):
        self.client = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)
        self.client.verbose = False
        self.client.remove_section_headers = True
        self.client.skip_non_songs = True
        self.client.excluded_terms = ["(Remix)", "(Live)", "(Instrumental)"]
        self.client.timeout = 15

    @cached(ttl_seconds=86400)
    async def search_lyrics(self, title: str, artist: str):
        """Поиск текста песни с кэшированием"""
        loop = asyncio.get_event_loop()
        song = await loop.run_in_executor(
            None,
            self.client.search_song,
            title,
            artist
        )

        if song and song.lyrics:
            return song

        clean_title = title.replace("N'", "and").replace("&", "and").replace("N ", "N' ")
        if clean_title != title:
            song = await loop.run_in_executor(
                None,
                self.client.search_song,
                clean_title,
                artist
            )
            if song and song.lyrics:
                return song

        return None

    async def search_with_multiple_artists(self, title: str, artists: list):
        """Поиск с разными комбинациями артистов"""
        song = await self.search_lyrics(title, artists[0])

        if not song and len(artists) > 1:
            artists_str = ", ".join(artists)
            song = await self.search_lyrics(title, artists_str)

        return song
