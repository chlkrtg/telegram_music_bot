import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")


def validate_config():
    """Проверяет наличие всех необходимых переменных окружения"""
    required = {
        "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
        "SPOTIFY_CLIENT_ID": SPOTIFY_CLIENT_ID,
        "SPOTIFY_CLIENT_SECRET": SPOTIFY_CLIENT_SECRET,
        "GENIUS_ACCESS_TOKEN": GENIUS_ACCESS_TOKEN,
        "LASTFM_API_KEY": LASTFM_API_KEY
    }

    missing = [key for key, value in required.items() if not value]

    if missing:
        raise ValueError(
            f"❌ ОТСУТСТВУЮТ КЛЮЧИ В .env: {', '.join(missing)}"
        )

    return required
