import urllib.parse
import aiohttp
from telegram import Update
from telegram.ext import ContextTypes
from services.spotify_service import SpotifyService
from services.genius_service import GeniusService
from utils.logger import log_to_file
from utils.helpers import clean_genius_lyrics
from utils.keyboards import get_back_menu, get_after_lyrics_keyboard


async def send_lyrics(update: Update, artist: str, title: str, lyrics: str, source_url: str, is_callback: bool = False):
    """Отправляет текст песни отдельным сообщением"""
    if len(lyrics) > 3900:
        lyrics = lyrics[:3900] + "\n\n..."

    result = f"📖 *{artist}* — *{title}*\n\n{lyrics}\n\n🔗 [Источник]({source_url})"

    if is_callback and hasattr(update, 'callback_query') and update.callback_query:
        await update.callback_query.message.reply_text(
            result,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=get_after_lyrics_keyboard()
        )
        await update.callback_query.answer()
    else:
        await update.message.reply_text(
            result,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=get_after_lyrics_keyboard()
        )


async def get_lyrics_by_artist_and_title(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                         artist: str, title: str, user_id: int,
                                         status_msg=None, is_callback: bool = False):
    """Поиск текста песни по артисту и названию"""
    try:
        genius_service = GeniusService()
        song = await genius_service.search_with_multiple_artists(title, [artist])

        if song and song.lyrics:
            lyrics = clean_genius_lyrics(song.lyrics)
            if status_msg:
                try:
                    await status_msg.delete()
                except:
                    pass
            await send_lyrics(update, artist, title, lyrics, song.url, is_callback)
            log_to_file(user_id, "BOT", f"Sent lyrics from Genius: {artist} - {title}")
            return True

        api_url = f"https://api.lyrics.ovh/v1/{urllib.parse.quote(artist)}/{urllib.parse.quote(title)}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    lyrics = data.get('lyrics', '')
                    if lyrics and len(lyrics) > 50:
                        if status_msg:
                            try:
                                await status_msg.delete()
                            except:
                                pass
                        await send_lyrics(update, artist, title, lyrics, "https://lyrics.ovh", is_callback)
                        log_to_file(user_id, "BOT", f"Sent lyrics from Lyrics.ovh: {artist} - {title}")
                        return True

        return False

    except Exception as e:
        print(f"Lyrics search error: {e}")
        return False


async def handle_lyrics_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback для поиска текста песни конкретного трека"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    callback_data = query.data

    if callback_data.startswith("lyrics|"):
        parts = callback_data.split("|")
        if len(parts) >= 3:
            artist = parts[1]
            title = parts[2]

            status_msg = await query.message.reply_text(
                f"🔍 Ищу текст песни *{artist} — {title}*...",
                parse_mode="Markdown"
            )

            found = await get_lyrics_by_artist_and_title(
                update, context, artist, title, user_id,
                status_msg=status_msg, is_callback=True
            )

            if not found:
                try:
                    await status_msg.delete()
                except:
                    pass

                encoded_query = urllib.parse.quote(f"{artist} {title}")
                genius_search_url = f"https://genius.com/search?q={encoded_query}"

                await query.message.reply_text(
                    f"❌ Не удалось найти текст песни *{artist} — {title}*.\n\n"
                    f"💡 Попробуй найти вручную:\n"
                    f"[Искать на Genius]({genius_search_url})\n\n"
                    f"Или проверь правильность написания.",
                    parse_mode="Markdown",
                    disable_web_page_preview=True,
                    reply_markup=get_back_menu()
                )
                log_to_file(user_id, "BOT", f"Lyrics not found: {artist} - {title}")


async def get_lyrics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение текста песни через Genius (команда /lyrics)"""
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            "📝 *Поиск текста песни*\n\n"
            "Введи название песни в формате:\n"
            "`/lyrics Артист - Название`\n\n"
            "💡 *Пример:*\n"
            "`/lyrics Imagine Dragons - Believer`\n\n"
            "Или просто отправь запрос в формате: Артист - Название",
            parse_mode="Markdown",
            reply_markup=get_back_menu()
        )
        return

    query = " ".join(context.args)
    log_to_file(user_id, "USER", f"/lyrics {query}")

    status_msg = await update.message.reply_text(f"🔍 Ищу текст для *{query}*...", parse_mode="Markdown")

    try:
        spotify_service = SpotifyService()
        track_info = spotify_service.get_track_info(query)

        if not track_info:
            if " - " in query:
                artist_part, title_part = query.split(" - ", 1)
                found = await get_lyrics_by_artist_and_title(
                    update, context, artist_part, title_part, user_id,
                    status_msg=status_msg, is_callback=False
                )
                if found:
                    return

            try:
                await status_msg.delete()
            except:
                pass
            await update.message.reply_text(
                "❌ Не удалось найти песню. Пожалуйста, проверь название.\n\n"
                "💡 Формат: `/lyrics Imagine Dragons - Believer`",
                parse_mode="Markdown",
                reply_markup=get_back_menu()
            )
            return

        found = await get_lyrics_by_artist_and_title(
            update, context,
            track_info['artists_list'][0],
            track_info['track_name'],
            user_id,
            status_msg=status_msg,
            is_callback=False
        )

        if found:
            return

        try:
            await status_msg.delete()
        except:
            pass

        search_query = f"{track_info['artists_list'][0]} {track_info['track_name']}"
        encoded_query = urllib.parse.quote(search_query)
        genius_search_url = f"https://genius.com/search?q={encoded_query}"

        await update.message.reply_text(
            f"❌ Не удалось найти текст песни *{track_info['artists_str']} — {track_info['track_name']}*.\n\n"
            f"💡 Попробуй найти вручную:\n"
            f"[Искать на Genius]({genius_search_url})\n\n"
            f"Или проверь правильность написания.",
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=get_back_menu()
        )
        log_to_file(user_id, "BOT", f"Lyrics not found: {track_info['artists_str']} - {track_info['track_name']}")

    except Exception as e:
        print(f"Lyrics error: {e}")
        try:
            await status_msg.delete()
        except:
            pass
        await update.message.reply_text(
            "⚠️ Произошла ошибка при получении текста.",
            reply_markup=get_back_menu()
        )
