from telegram import Update
from telegram.ext import ContextTypes
from services.spotify_service import SpotifyService
from utils.logger import log_to_file
from utils.keyboards import get_back_menu, get_after_search_keyboard


async def search_track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Поиск трека через Spotify"""
    user_id = update.effective_user.id

    spotify_service = SpotifyService()

    # Обработка текстовых сообщений (без команды)
    if update.message and not update.message.text.startswith('/'):
        query = update.message.text
        log_to_file(user_id, "USER", f"Search: {query}")
    else:
        log_to_file(user_id, "USER", update.message.text)

        if not context.args:
            msg = (
                "🎵 *Поиск трека*\n\n"
                "Укажи название трека.\n\n"
                "💡 *Пример:*\n"
                "/search Blinding Lights\n\n"
                "Или просто отправь мне название песни!"
            )
            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_back_menu())
            log_to_file(user_id, "BOT", msg)
            return

        query = " ".join(context.args)

    try:
        track_info = spotify_service.get_track_info(query)

        if not track_info:
            msg = f"❌ По запросу '{query}' ничего не найдено. Попробуй снова!"
            await update.message.reply_text(msg, reply_markup=get_back_menu())
            log_to_file(user_id, "BOT", msg)
            return

        context.user_data['last_track'] = {
            'artist': track_info['artist_name'],
            'title': track_info['track_name'],
            'artists_list': track_info['artists_list']
        }

        caption = (
            f"🎵 *{track_info['artist_name']}* — *{track_info['track_name']}*\n\n"
            f"💿 Альбом: {track_info['album_name']} ({track_info['release_year']})\n"
            f"👥 Исполнители: {track_info['artists_str']}"
        )

        action_keyboard = get_after_search_keyboard(
            track_artist=track_info['artist_name'],
            track_title=track_info['track_name'],
            track_url=track_info['spotify_url'],
            album_url=track_info['album_url']
        )

        if track_info['album_image_url']:
            await update.message.reply_photo(
                photo=track_info['album_image_url'],
                caption=caption,
                parse_mode="Markdown",
                reply_markup=action_keyboard
            )
        else:
            await update.message.reply_text(
                caption,
                parse_mode="Markdown",
                reply_markup=action_keyboard
            )

        log_to_file(user_id, "BOT", f"Sent track info: {track_info['artist_name']} - {track_info['track_name']}")

    except Exception as e:
        print(f"Ошибка search: {e}")
        await update.message.reply_text(
            "⚠️ Ошибка при поиске трека. Проверь название и попробуй снова.",
            reply_markup=get_back_menu()
        )
        log_to_file(user_id, "BOT", f"Error: {e}")