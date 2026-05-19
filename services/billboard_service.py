import aiohttp
from bs4 import BeautifulSoup
from services.spotify_service import SpotifyService
from services.cache_service import cached


class BillboardService:
    BASE_URL = "https://www.billboard.com"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    def __init__(self):
        self.session = None
        self.spotify = SpotifyService()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_categories(self) -> dict:
        """ Получает чарты Billboard """
        url = f"{self.BASE_URL}/charts/"

        async with self.session.get(url, headers=self.HEADERS, timeout=15) as response:
            if response.status != 200:
                raise Exception(f"Ошибка загрузки Billboard: {response.status}")

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            categories = {}

            working_charts = {
                'hot-100': 'Hot 100',
                'hot-rock-songs': 'Hot Rock Songs',
                'hot-r-and-b-hip-hop-songs': 'Hot R&B/Hip-Hop Songs',
                'country-songs': 'Hot Country Songs',
                'dance-electronic-songs': 'Dance/Electronic Songs',
                'latin-songs': 'Latin Songs',
                'christian-songs': 'Christian Songs',
            }

            chart_links = soup.find_all('a', href=True)

            for link in chart_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)

                for chart_key, chart_name in working_charts.items():
                    if chart_key in href:
                        if href.startswith('/'):
                            full_url = f"{self.BASE_URL}{href}"
                        else:
                            full_url = href

                        if chart_name not in categories:
                            categories[chart_name] = full_url
                            print(f"Found working chart: {chart_name}")
                        break

            if not categories:
                print("Using fallback charts list")
                categories = {
                    "Hot 100": f"{self.BASE_URL}/charts/hot-100/",
                    "Hot Rock Songs": f"{self.BASE_URL}/charts/hot-rock-songs/",
                    "Hot R&B/Hip-Hop Songs": f"{self.BASE_URL}/charts/hot-r-and-b-hip-hop-songs/",
                    "Hot Country Songs": f"{self.BASE_URL}/charts/country-songs/",
                    "Dance/Electronic Songs": f"{self.BASE_URL}/charts/dance-electronic-songs/",
                    "Latin Songs": f"{self.BASE_URL}/charts/latin-songs/",
                    "Christian Songs": f"{self.BASE_URL}/charts/christian-songs/",
                }

            print(f"Total working charts: {len(categories)}")
            return categories

    @cached(ttl_seconds=7200)
    async def parse_chart(self, chart_url: str, limit: int = 10):
        """Парсит конкретный чарт с кэшированием"""
        async with self.session.get(chart_url, headers=self.HEADERS, timeout=15) as response:
            if response.status != 200:
                raise Exception(f"Ошибка загрузки чарта: {response.status}")

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            results = []

            rows = soup.select('div.o-chart-results-list-row-container')

            if not rows:
                rows = soup.select('div.chart-list-item')
                print(f"Using alternative selector, found {len(rows)} rows")

            for idx, row in enumerate(rows[:limit], 1):
                try:
                    title, artist = self._extract_track_info_simple(row)

                    if title and title not in ['New', 'Peak', 'Lyrics', 'Songs']:
                        spotify_url, preview_url = await self._search_spotify(title, artist)

                        results.append({
                            'title': title,
                            'artist': artist if artist else "Unknown Artist",
                            'spotify_url': spotify_url,
                            'preview_url': preview_url,
                            'position': idx
                        })

                except Exception as e:
                    print(f"Error parsing row {idx}: {e}")
                    continue

            return results

    async def _search_spotify(self, title: str, artist: str) -> tuple:
        """Ищет трек в Spotify с разными стратегиями"""
        if not title:
            return None, None

        if not artist or artist == "Unknown":
            queries = [title]
        else:
            queries = [
                f"{title} {artist}",
                f"{artist} - {title}",
                title,
                f"{title} {artist.split()[0]}"
            ]

        for query in queries:
            try:
                tracks = self.spotify.search_track(query, limit=1)
                if tracks:
                    track = tracks[0]
                    track_title = track['name'].lower()
                    search_title = title.lower()

                    if search_title in track_title or track_title in search_title:
                        spotify_url = track['external_urls']['spotify']
                        preview_url = track.get('preview_url')
                        print(f"Found on Spotify: '{track['name']}' by '{track['artists'][0]['name']}'")
                        return spotify_url, preview_url
            except Exception as e:
                print(f"Spotify search error for '{query}': {e}")
                continue

        print(f"Not found on Spotify: {title} - {artist}")
        return None, None

    def _extract_track_info_simple(self, row) -> tuple:
        """
        Простой парсинг: правильно определяем позицию, название и артиста
        """
        all_text = row.get_text(separator='\n', strip=True)
        lines = [line.strip() for line in all_text.split('\n') if line.strip()]

        position = None
        title = None
        artist = None

        if len(lines) >= 3:
            if lines[0].isdigit():
                position = lines[0]

            title = lines[1]
            artist = lines[2]

            if len(lines) >= 4 and lines[3] not in ['LW', 'PEAK', 'WEEKS', 'Share', 'Credits']:
                if artist and artist.endswith('&'):
                    artist = f"{artist} {lines[3]}"
                    if len(lines) >= 5 and lines[4] not in ['LW', 'PEAK', 'WEEKS', 'Share']:
                        artist = f"{artist} {lines[4]}"

        if title:
            title = title.replace('NEW', '').replace('PEAK', '').strip()

        if artist:
            stop_words = ['LW', 'PEAK', 'WEEKS', 'Share', 'Credits', 'Songwriter(s)', 'Producer(s)',
                          'Debut Position', 'Peak Position', 'Chart History', 'Awards', 'Gains In Performance']
            for word in stop_words:
                artist = artist.replace(word, '')
            artist = artist.strip()

            if not artist or artist.isdigit():
                artist = None

        print(f"Parsed: position='{position}', title='{title}', artist='{artist}'")

        return title, artist
