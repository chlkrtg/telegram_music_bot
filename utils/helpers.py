def clean_genius_lyrics(lyrics: str) -> str:
    """Очищает текст от заголовков Genius и лишних строк"""
    lines = lyrics.split('\n')

    if lines and 'lyrics' in lines[0].lower():
        lines = lines[1:]

    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    return '\n'.join(lines)