# Smart Reader 🎧

**Course:** Programming with Python &nbsp;·&nbsp; **Language:** Python 3

---

## 📌 Problem

PDFs accumulate faster than we can read them — lectures, articles, textbooks. Reading requires full attention. Listening does not.

## 💡 Solution

Smart Reader converts any PDF into an MP3 audio file with two clicks. It also keeps a detailed history of every file you've converted, so you always know what's been processed. 

Open PDF - Read Text → Save MP3 - Log it.

---

## ✨ Features

- **PDF Text Extraction:** Extracts text from all pages with full multi-page support.
- **Auto-Translation & Language Detection:** Automatically detects the source document language and translates the text on the fly using `deep-translator` if it differs from the chosen audio language.
- **Multi-Language Voices:** Choose between English, Russian, and Kyrgyz (with smart fallback logic).
- **Dark & Light Mode:** Beautiful built-in UI themes that persist across sessions via `theme.json`.
- **Real-time Progress:** Visual progress bar tracking chunks during text-to-speech conversion.
- **Advanced Conversion History:** Logs timestamps, word/character counts, and text previews. Directly play generated audio or reuse text straight from the history tab.

---

## 🛠 Tech Stack & Libraries

- **Language:** Python 3
- **GUI:** `tkinter`
- **PDF Parsing:** `PyPDF2`
- **Text-to-Speech:** `gTTS`
- **Translation:** `langdetect` & `deep-translator`

---

## 🚀 How to Run

**Step 1** — Install Python 3.8+ from https://python.org

**Step 2** — Install dependencies:
```bash
pip install -r requirements.txt

**Step 2** — Install dependencies:
```bash
pip install -r requirements.txt

Step 3
python main.py
