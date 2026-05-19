from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import log_to_file
from utils.keyboards import get_inline_main_menu, get_back_menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    log_to_file(user_id, "USER", "/start")

    context.user_data.pop('awaiting_input', None)

    welcome_text = (
        "🎵 *Music Bot*\n\n"
        "👋 Привет! Я музыкальный бот, который поможет тебе:\n"
        "- Найти треки и информацию о них;\n"
        "- Получить тексты песен;\n"
        "- Узнать популярные треки артистов;\n"
        "- Посмотреть чарты Billboard;\n"
        "- Найти артистов, похожих на данного.\n\n"
        "👇 *Используй кнопки ниже для навигации*"
    )

    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_inline_main_menu()
    )

    log_to_file(user_id, "BOT", "Main menu shown")


async def handle_main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатия на кнопки главного меню"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    callback_data = query.data

    if callback_data.startswith("main_menu"):
        # Разбираем флаг
        parts = callback_data.split("|")
        flag = parts[1] if len(parts) > 1 else "delete"

        context.user_data.pop('awaiting_input', None)

        if flag == "keep":
            await query.message.reply_text(
                "🏠 *Главное меню*\n\nВыбери действие или воспользуйся доступными командами!",
                parse_mode="Markdown",
                reply_markup=get_inline_main_menu()
            )
        else:
            await query.edit_message_text(
                "🏠 *Главное меню*\n\nВыбери действие или воспользуйся доступными командами!",
                parse_mode="Markdown",
                reply_markup=get_inline_main_menu()
            )

        log_to_file(user_id, "BOT", "Returned to main menu")

    elif callback_data == "menu_search":
        context.user_data['awaiting_input'] = 'search'

        msg = (
            "🔍 *Поиск песни*\n\n"
            "Введи название песни в формате:\n"
            "`Артист - Название песни`\n\n"
            "💡 *Пример:*\n"
            "`Lana del Rey Summertime Sadness`\n\n"
            "⚠️ *Для отмены нажми на кнопку ниже*"
        )
        await query.edit_message_text(
            msg,
            parse_mode="Markdown",
            reply_markup=get_back_menu()
        )
        log_to_file(user_id, "BOT", "Search help shown, waiting for input")

    elif callback_data == "menu_lyrics":
        context.user_data['awaiting_input'] = 'lyrics'

        msg = (
            "📝 *Поиск текста песни*\n\n"
            "Введи запрос в формате:\n"
            "`Артист - Название песни`\n\n"
            "💡 *Пример:*\n"
            "`Imagine Dragons - Believer`\n\n"
            "⚠️ *Для отмены нажми на кнопку ниже*"
        )
        await query.edit_message_text(
            msg,
            parse_mode="Markdown",
            reply_markup=get_back_menu()
        )
        log_to_file(user_id, "BOT", "Lyrics help shown, waiting for input")

    elif callback_data == "menu_top":
        context.user_data['awaiting_input'] = 'top'

        msg = (
            "🎤 *Топ песен артиста*\n\n"
            "Введи имя артиста.\n\n"
            "💡 *Пример:*\n"
            "`Vana`\n\n"
            "⚠️ *Для отмены нажми на кнопку ниже*"
        )
        await query.edit_message_text(
            msg,
            parse_mode="Markdown",
            reply_markup=get_back_menu()
        )
        log_to_file(user_id, "BOT", "Top tracks help shown, waiting for input")

    elif callback_data == "menu_charts":
        context.user_data.pop('awaiting_input', None)

        from handlers.charts_handler import get_categories_simple

        status_msg = await query.message.reply_text("🔍 Парсинг категорий Billboard...")

        await get_categories_simple(query.message.chat_id, context.bot, query.from_user.id, context, status_msg)

    elif callback_data == "menu_help":
        context.user_data.pop('awaiting_input', None)

        help_text = (
            "❓ *Помощь по командам*\n\n"
            "📌 *Доступные команды:*\n"
            "- `/search <название>` - Поиск трека с превью\n"
            "- `/lyrics <артист - песня>` - Текст песни\n"
            "- `/top <артист>` - Популярные треки\n"
            "- `/charts` - Чарты Billboard\n"
            "- `/similar <артист>` - Похожие артисты\n"
            "- `/start` - Главное меню\n\n"
            "📌 *Примеры использования:*\n"
            "- `/search PRAY TO ME`\n"
            "- `/lyrics DeathbyRomy - YUNG N RICH`\n"
            "- `/top Imagine Dragons`\n\n"
            "💡 *Совет:* Используй кнопки для быстрой навигации!"
        )
        await query.edit_message_text(
            help_text,
            parse_mode="Markdown",
            reply_markup=get_back_menu()
        )
        log_to_file(user_id, "BOT", "Help shown")

    elif callback_data == "menu_similar":
        context.user_data['awaiting_input'] = 'similar'
        msg = (
            "🎯 *Похожие артисты (Last.fm)*\n\n"
            "Введи имя артиста.\n\n"
            "💡 *Пример:*\n"
            "`Нуки`\n\n"
            "⚠️ *Для отмены нажми на кнопку ниже*"
        )
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=get_back_menu())
        log_to_file(user_id, "BOT", "Similar artists help shown, waiting for input")
