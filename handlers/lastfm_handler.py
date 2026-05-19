from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.lastfm_service import LastFMService
from utils.logger import log_to_file
from utils.keyboards import get_back_menu, get_after_similar_keyboard


async def get_similar_artists(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Поиск похожих артистов через Last.fm"""
    user_id = update.effective_user.id

    lastfm = LastFMService()

    if update.message and not update.message.text.startswith('/'):
        artist_query = update.message.text
        log_to_file(user_id, "USER", f"Similar artists (text): {artist_query}")
    else:
        log_to_file(user_id, "USER", update.message.text)

        if not context.args:
            msg = (
                "🎯 *Похожие артисты*\n\n"
                "Укажи имя артиста.\n\n"
                "💡 *Пример:*\n"
                "`/similar The Weeknd`\n\n"
                "Или просто отправь мне имя артиста!"
            )
            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_back_menu())
            log_to_file(user_id, "BOT", msg)
            return

        artist_query = " ".join(context.args)

    status_msg = await update.message.reply_text(
        f"🔍 Ищу похожих на *{artist_query}*...\n"
        f"⏳ Обычно это занимает 1-2 секунды",
        parse_mode="Markdown"
    )

    try:
        similar_artists = await lastfm.get_similar_artists(artist_query, limit=10)

        if not similar_artists:
            search_results = await lastfm.search_artist(artist_query)
            if search_results:
                suggestions = "\n".join([f"• {name}" for name in search_results[:5]])
                await status_msg.edit_text(
                    f"❌ Артист '{artist_query}' не найден.\n\n"
                    f"💡 Возможно, ты имел в виду:\n{suggestions}\n\n"
                    f"Попробуй: `{search_results[0]}`",
                    parse_mode="Markdown",
                    reply_markup=get_after_similar_keyboard()
                )
            else:
                await status_msg.edit_text(
                    f"❌ Артист '{artist_query}' не найден в базе.\n\n"
                    f"Проверь правильность написания и попробуй снова.",
                    reply_markup=get_after_similar_keyboard()
                )
            return

        result = f"🎤 *{artist_query.upper()}*\n"
        result += "━━━━━━━━━━━━━━━\n"

        artist_info = await lastfm.get_artist_info(artist_query)

        if artist_info and artist_info.get('tags') and len(artist_info['tags']) > 0:
            tags = artist_info['tags'][:3]
            result += f"🏷️ Жанры: {', '.join(tags)}\n"

        result += "🎭 *Похожие артисты:*\n\n"

        for i, artist in enumerate(similar_artists[:8], 1):
            match = artist['match']
            bar_length = int(match / 20)
            bar = "█" * bar_length + "░" * (5 - bar_length)
            result += f"{i}. *{artist['name']}*\n"
            result += f"   `{bar}` {match:.0f}% совпадение\n\n"

        keyboard_buttons = []
        if len(similar_artists) > 8:
            keyboard_buttons.append(
                [InlineKeyboardButton("🔄 Ещё похожих", callback_data=f"more_similar|{artist_query}")]
            )
        keyboard_buttons.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu|keep")])

        keyboard = InlineKeyboardMarkup(keyboard_buttons)

        await status_msg.edit_text(result, parse_mode="Markdown", reply_markup=keyboard)
        log_to_file(user_id, "BOT", f"Found {len(similar_artists)} similar artists for {artist_query}")

    except Exception as e:
        print(f"Last.fm error: {e}")
        await status_msg.edit_text(
            "⚠️ Ошибка при обращении к Last.fm API.\n"
            "Пожалуйста, попробуй позже.",
            reply_markup=get_back_menu()
        )


async def more_similar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Ещё похожих' - показывает следующие 10 артистов"""
    query = update.callback_query
    await query.answer()

    _, artist_name = query.data.split("|")

    lastfm = LastFMService()

    similar_artists = await lastfm.get_similar_artists(artist_name, limit=20)

    if not similar_artists or len(similar_artists) <= 10:
        await query.message.reply_text(
            "❌ Больше похожих артистов не найдено.",
            reply_markup=get_back_menu()
        )
        return

    more_artists = similar_artists[10:20]

    await query.edit_message_reply_markup(reply_markup=None)

    result = f"🎤 *{artist_name.upper()}*\n"
    result += "━━━━━━━━━━━━━━━\n"
    result += "🎭 *Ещё похожие артисты:*\n\n"

    for i, artist in enumerate(more_artists, 11):
        match = artist['match']
        bar_length = int(match / 20)
        bar = "█" * bar_length + "░" * (5 - bar_length)
        result += f"{i}. *{artist['name']}*\n"
        result += f"   `{bar}` {match:.0f}% совпадение\n\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu|keep")]
    ])

    await query.message.reply_text(result, parse_mode="Markdown", reply_markup=keyboard)
