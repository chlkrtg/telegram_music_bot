from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_inline_main_menu():
    keyboard = [
        [InlineKeyboardButton("🔍 Поиск трека", callback_data="menu_search")],
        [InlineKeyboardButton("📝 Текст песни", callback_data="menu_lyrics")],
        [InlineKeyboardButton("🎤 Топ треков", callback_data="menu_top")],
        [InlineKeyboardButton("🎯 Похожие артисты", callback_data="menu_similar")],
        [InlineKeyboardButton("📊 Чарты Billboard", callback_data="menu_charts")],
        [InlineKeyboardButton("❓ Помощь", callback_data="menu_help")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_menu():
    """Кнопка возврата в главное меню"""
    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu|edit")]]
    return InlineKeyboardMarkup(keyboard)


def get_charts_keyboard(categories: dict):
    """Клавиатура выбора чарта"""
    keyboard = []
    for i, (name, url) in enumerate(categories.items()):
        keyboard.append([InlineKeyboardButton(f"📈 {name}", callback_data=f"chart_{i}")])

    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu|edit")])
    return InlineKeyboardMarkup(keyboard)


def get_after_search_keyboard(track_artist: str = None, track_title: str = None, track_url: str = None,
                              album_url: str = None):
    """
    Клавиатура после поиска трека (с кнопкой для текста этой песни и альбомом)
    """
    keyboard = []
    if track_url:
        keyboard.append([InlineKeyboardButton("🎵 Слушать трек", url=track_url)])

    if album_url:
        keyboard.append([InlineKeyboardButton("💿 Открыть альбом", url=album_url)])

    if track_artist and track_title:
        short_artist = track_artist[:20] if len(track_artist) > 20 else track_artist
        short_title = track_title[:20] if len(track_title) > 20 else track_title
        callback_data = f"lyrics|{short_artist}|{short_title}"
        keyboard.append([InlineKeyboardButton("📝 Найти текст этой песни", callback_data=callback_data)])

    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu|keep")])

    return InlineKeyboardMarkup(keyboard)


def get_after_lyrics_keyboard():
    """Клавиатура после получения текста песни"""
    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu|keep")]]
    return InlineKeyboardMarkup(keyboard)


def get_after_top_keyboard():
    """Клавиатура после вывода топ треков"""
    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu|keep")]]
    return InlineKeyboardMarkup(keyboard)


def get_after_similar_keyboard():
    """Клавиатура после получения похожих артистов"""
    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu|keep")]]
    return InlineKeyboardMarkup(keyboard)
