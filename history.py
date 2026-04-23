import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_entry(filename, words, chars):
    entries = load_history()
    entry = {
        "filename": filename,
        "words": words,
        "chars": chars,
        "timestamp": datetime.now().strftime("%d.%m.%Y  %H:%M")
    }
    entries.insert(0, entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)