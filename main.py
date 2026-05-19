from utils.keyboards import get_back_menu
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import TELEGRAM_TOKEN, validate_config
from handlers.start_handler import start, handle_main_menu_callback
from handlers.search_handler import search_track
from handlers.lyrics_handler import get_lyrics, handle_lyrics_callback
from handlers.top_handler import get_top_tracks
from handlers.charts_handler import get_billboard_categories, billboard_chart_callback
from handlers.lastfm_handler import get_similar_artists, more_similar_callback


async def handle_text(update, context):
    """Умный обработчик текстовых сообщений"""
    text = update.message.text

    if 'awaiting_input' in context.user_data:
        mode = context.user_data['awaiting_input']

        if mode == 'search':
            context.args = [text]
            await search_track(update, context)
            context.user_data.pop('awaiting_input', None)
            return

        elif mode == 'lyrics':
            context.args = text.split()
            await get_lyrics(update, context)
            context.user_data.pop('awaiting_input', None)
            return

        elif mode == 'top':
            context.args = [text]
            await get_top_tracks(update, context)
            context.user_data.pop('awaiting_input', None)
            return

        elif mode == 'similar':
            context.args = [text]
            await get_similar_artists(update, context)
            context.user_data.pop('awaiting_input', None)
            return

    if text and not text.startswith('/'):
        await update.message.reply_text(
            "❓ *Я не понимаю этот запрос!*\n\n"
            "Пожалуйста, используй команды:\n"
            "• `/search <название>` - поиск трека\n"
            "• `/lyrics <артист - песня>` - текст песни\n"
            "• `/top <артист>` - топ треки\n"
            "• `/similar <артист>` - похожие артисты\n"
            "• `/charts` - чарты Billboard\n\n"
            "💡 *Примеры:*\n"
            "`/search Blinding Lights`\n"
            "`/lyrics Imagine Dragons - Believer`\n"
            "`/top The Weeknd`\n"
            "`/similar Imagine Dragons`",
            parse_mode="Markdown",
            reply_markup=get_back_menu()
        )
        return


async def handle_unknown_text(update, context):
    """Обработчик неизвестных команд"""
    await update.message.reply_text(
        "❓ *Неизвестная команда!*\n\n"
        "Я не знаю такую команду. Вот что я умею:\n\n"
        "📌 *Доступные команды:*\n"
        "• `/search <название>` - поиск трека с превью\n"
        "• `/lyrics <артист - песня>` - текст песни\n"
        "• `/top <артист>` - популярные треки артиста\n"
        "• `/similar <артист>` - похожие артисты\n"
        "• `/charts` - чарты Billboard\n"
        "• `/start` - главное меню\n\n"
        "💡 *Пример:* `/search Blinding Lights`",
        parse_mode="Markdown",
        reply_markup=get_back_menu()
    )


def main():
    """Главная функция запуска бота"""
    try:
        validate_config()
    except ValueError as e:
        print(e)
        exit(1)

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search_track))
    app.add_handler(CommandHandler("top", get_top_tracks))
    app.add_handler(CommandHandler("lyrics", get_lyrics))
    app.add_handler(CommandHandler("charts", get_billboard_categories))
    app.add_handler(CommandHandler("similar", get_similar_artists))
    app.add_handler(CallbackQueryHandler(more_similar_callback, pattern="^more_similar\|"))
    app.add_handler(CallbackQueryHandler(handle_main_menu_callback, pattern="^(main_menu|menu_|example_|new_)"))
    app.add_handler(CallbackQueryHandler(handle_lyrics_callback, pattern="^(lyrics|new_lyrics)"))
    app.add_handler(CallbackQueryHandler(billboard_chart_callback, pattern="^chart_"))
    app.add_handler(CallbackQueryHandler(billboard_chart_callback, pattern="^cancel$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.COMMAND, handle_unknown_text))

    print("🚀 МУЗЫКАЛЬНЫЙ БОТ ЗАПУЩЕН")

    app.run_polling()


if __name__ == "__main__":
    main()
