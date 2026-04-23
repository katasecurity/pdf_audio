import PyPDF2
from gtts import gTTS


def read_pdf(file_path):
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
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


def convert_to_mp3(text, output_file="result.mp3", language="ru"):
    tts = gTTS(text=text, lang=language)
    tts.save(output_file)
    return output_file