from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.billboard_service import BillboardService
from utils.logger import log_to_file
from utils.keyboards import get_charts_keyboard, get_back_menu


async def show_categories(chat_id, bot, user_id, context, status_msg=None):
    """Показывает категории чартов (универсальная функция)"""
    try:
        async with BillboardService() as billboard:
            categories = await billboard.get_categories()

        context.user_data['billboard_categories'] = categories

        text = f"📊 *Найдено {len(categories)} чартов*\n\nВыберите категорию:"

        if status_msg:
            try:
                await status_msg.delete()
            except:
                pass

        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=get_charts_keyboard(categories)
        )
        log_to_file(user_id, "BOT", f"Found {len(categories)} categories from Billboard")

    except Exception as e:
        print(f"Billboard categories error: {e}")
        if status_msg:
            try:
                await status_msg.delete()
            except:
                pass
        await bot.send_message(
            chat_id=chat_id,
            text="⚠️ Ошибка при парсинге категорий",
            reply_markup=get_back_menu()
        )


async def get_billboard_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /charts — отправляем статус, потом удаляем и показываем категории"""
    user_id = update.effective_user.id
    log_to_file(user_id, "USER", "/charts")

    status_msg = await update.message.reply_text("🔍 Парсинг категорий Billboard...")

    await show_categories(update.effective_chat.id, context.bot, user_id, context, status_msg)


async def get_categories_simple(chat_id, bot, user_id, context, status_msg=None):
    """Вызов из меню — удаляем переданный статус и показываем категории"""
    await show_categories(chat_id, bot, user_id, context, status_msg)


async def billboard_chart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора категории"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    callback_data = query.data

    if callback_data == "cancel":
        await query.edit_message_text("❌ Отменено", reply_markup=get_back_menu())
        return

    categories = context.user_data.get('billboard_categories', {})
    category_index = int(callback_data.replace("chart_", ""))

    category_names = list(categories.keys())
    category_urls = list(categories.values())

    if category_index >= len(category_names):
        await query.edit_message_text("❌ Категория не найдена", reply_markup=get_back_menu())
        return

    selected_name = category_names[category_index]
    selected_url = category_urls[category_index]

    await query.edit_message_text(
        f"🔍 Парсинг чарта *{selected_name}*...\n⏳ Это может занять 10-15 секунд",
        parse_mode="Markdown"
    )

    try:
        async with BillboardService() as billboard:
            tracks = await billboard.parse_chart(selected_url, limit=10)

        if not tracks:
            await query.edit_message_text(
                "❌ Не удалось спарсить чарт.\n"
                "Возможно, Billboard изменил структуру страницы.",
                reply_markup=get_back_menu()
            )
            return

        response_text = f"🎵 *{selected_name.upper()} — TOP {len(tracks)}* 🎵\n"
        response_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        for track in tracks:
            pos = track['position']
            title = track['title'][:45] if track['title'] else "Unknown"
            artist = track['artist'][:35] if track['artist'] and track['artist'] != "Unknown" else "Artist not found"

            response_text += f"*{pos}. {title}*\n"
            response_text += f"   👤 {artist}\n"

            if track['spotify_url']:
                response_text += f"   🎧 [Слушать на Spotify]({track['spotify_url']})\n"
            else:
                response_text += f"   ❌ Не найдено на Spotify\n"

            response_text += "\n"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Другой чарт", callback_data="menu_charts")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu|keep")]
        ])

        await query.message.reply_text(
            response_text,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=keyboard
        )

        try:
            await query.message.delete()
        except:
            pass

        log_to_file(user_id, "BOT", f"Parsed chart '{selected_name}' with {len(tracks)} items")

    except Exception as e:
        print(f"Chart parsing error: {e}")
        import traceback
        traceback.print_exc()
        await query.edit_message_text(
            f"⚠️ Ошибка при парсинге чарта: {str(e)[:100]}",
            reply_markup=get_back_menu()
        )
