import os
import io
import re
from gtts import gTTS
from gtts.lang import tts_langs
import PyPDF2
from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator

LANG_FALLBACK = {"en": "en", "ru": "ru", "ky": "ru"}


def read_pdf(file_path):
    text = ""
    try:
        with open(file_path, "rb") as f:
            for page in PyPDF2.PdfReader(f).pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        return ""
    return text.strip()


def count_words(text):
    return len(text.split())


def count_chars(text):
    return len(text)


def _detect_lang(text):
    try:
        return detect(text[:500])
    except LangDetectException:
        return None


def _translate(text, target_lang, translate_cb=None):
    src = _detect_lang(text)
    if not src or src == target_lang:
        return text, False
    if translate_cb:
        translate_cb(src)
    CHUNK = 4500
    limit = min(len(text), 20000)
    segments = [text[i:i + CHUNK] for i in range(0, limit, CHUNK)]
    parts = []
    for seg in segments:
        try:
            t = GoogleTranslator(source="auto", target=target_lang).translate(seg)
            parts.append(t or seg)
        except Exception:
            parts.append(seg)
    return " ".join(parts), True


def _split_chunks(text, size=400):
    parts = re.split(r'(?<=[.!?\n])\s+', text)
    chunks, cur = [], ""
    for s in parts:
        if len(cur) + len(s) + 1 <= size:
            cur += (" " if cur else "") + s
        else:
            if cur:
                chunks.append(cur)
            cur = s
    if cur:
        chunks.append(cur)
    return chunks or [text]


def convert_to_mp3(text, output_file="result.mp3", language="en",
                   progress_cb=None, translate_cb=None):
    available = tts_langs()
    lang = language if language in available else LANG_FALLBACK.get(language, "en")
    is_fallback = lang != language
    text_to_speak, was_translated = _translate(text[:20000], lang, translate_cb)
    chunks = _split_chunks(text_to_speak)
    parts = []
    for i, chunk in enumerate(chunks):
        buf = io.BytesIO()
        gTTS(text=chunk, lang=lang).write_to_fp(buf)
        parts.append(buf.getvalue())
        if progress_cb:
            progress_cb(int((i + 1) / len(chunks) * 100))
    abs_path = os.path.abspath(output_file)
    with open(abs_path, "wb") as f:
        for p in parts:
            f.write(p)
    return abs_path, is_fallback, lang, was_translated