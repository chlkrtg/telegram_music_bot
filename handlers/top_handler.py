from telegram import Update
from telegram.ext import ContextTypes
from services.spotify_service import SpotifyService
from utils.logger import log_to_file
from utils.keyboards import get_back_menu, get_after_top_keyboard


async def get_top_tracks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Популярные треки артиста через Spotify"""
    user_id = update.effective_user.id
    spotify_service = SpotifyService()

    if update.message and not update.message.text.startswith('/'):
        query = update.message.text
        log_to_file(user_id, "USER", f"Top tracks (text): {query}")
    else:
        log_to_file(user_id, "USER", update.message.text)

        if not context.args:
            msg = (
                "🎤 *Топ треков артиста*\n\n"
                "Укажи артиста.\n\n"
                "💡 *Пример:*\n"
                "/top Imagine Dragons\n\n"
                "Или просто отправь имя артиста!"
            )
            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_back_menu())
            log_to_file(user_id, "BOT", msg)
            return

        query = " ".join(context.args)

    try:
        tracks = spotify_service.get_top_tracks(query)

        if not tracks:
            msg = f"❌ Артист '{query}' не найден"
            await update.message.reply_text(msg, reply_markup=get_back_menu())
        else:
            msg = f"🎤 *{query.upper()}*\n━━━━━━━━━━━━━━━\n"
            for i, t in enumerate(tracks, 1):
                spotify_url = t['external_urls']['spotify']
                track_name = t['name']
                album_name = t['album']['name']
                msg += f"{i}. *{track_name}*\n   └─ Альбом: {album_name} │ [▶️]({spotify_url})\n"

            await update.message.reply_text(
                msg,
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=get_after_top_keyboard()
            )

        log_to_file(user_id, "BOT", msg)

    except Exception as e:
        print(f"Top tracks error: {e}")
        await update.message.reply_text("⚠️ Ошибка Spotify API", reply_markup=get_back_menu())
        log_to_file(user_id, "BOT", f"Error: {e}")
