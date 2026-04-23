# Smart Reader 🎧
Course: Programming with Python &nbsp;·&nbsp; Language: Python 3 &nbsp;·&nbsp; Libraries: PyPDF2, gTTS, tkinter

Team: Samir Murakev · Saidilbek Ubaidullaev · Bayel Bagynbaev

---

## Problem

PDFs accumulate faster than we can read them — lectures, articles, textbooks. Reading requires full attention. Listening does not.

## Solution

Smart Reader converts any PDF into an MP3 audio file with two clicks. It also keeps a history of every file you've converted, so you always know what's been processed.

Open PDF → Read Text → Save MP3 → Log it.

## Why this topic?

We wanted to build something practical. Existing PDF-to-audio tools are either paid, require an account, or are too complicated. We built a free, simple desktop version using only Python.

---

## Features

- Open any PDF file using a file dialog
- Extracts text from all pages (multi-page support)
- Shows word count and character count
- Converts text to speech → saves as result.mp3
- Conversion history tab — logs every conversion with timestamp, word count, and character count
- History can be cleared with one click
- No internet account or API key needed

---

## How to Run

Step 1 — Install Python 3.8+ from https://python.org

Step 2 — Install dependencies:
pip install -r requirements.txt

Step 3 — Run the app:
python main.py
