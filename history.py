import json
import os
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_entry(filename, words, chars, language="en", preview="", audio_path=None):
    entries = load_history()
    entries.insert(0, {
        "filename":  filename,
        "language":  language,
        "words":     words,
        "chars":     chars,
        "preview":   preview[:120].replace(" ", " ").strip(),
        "timestamp": datetime.now().strftime("%d.%m.%Y  %H:%M"),
        "audio":     audio_path,
    })
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(entries[:100], f, ensure_ascii=False, indent=2)


def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)