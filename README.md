# Music Telegram Bot

Музыкальный бот для Telegram с поддержкой:
- Поиск треков через Spotify;
- Тексты песен через Genius API;
- Топ треков артистов;
- Похожие артисты через Last.fm;
- Парсинг чартов Billboard.

## Установка

1. Клонируйте репозиторий;
2. Создайте виртуальное окружение: `python -m venv venv`;
3. Активируйте: `venv\Scripts\activate`;
4. Установите зависимости: `pip install -r requirements.txt`;
5. Создайте файл `.env` с вашими ключами (см. `config.py`);
6. Запустите: `python main.py`.

## Необходимые ключи

- TELEGRAM_TOKEN;
- SPOTIFY_CLIENT_ID;
- SPOTIFY_CLIENT_SECRET;
- GENIUS_ACCESS_TOKEN;
- LASTFM_API_KEY.