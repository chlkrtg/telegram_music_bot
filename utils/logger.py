import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def log_to_file(user_id: int, role: str, text: str):
    """Записывает лог взаимодействия"""
    log_path = os.path.join(LOG_DIR, f"{user_id}.log")
    with open(log_path, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        clean_text = str(text).replace('\n', ' ')
        f.write(f"[{timestamp}] {role}: {clean_text}\n")