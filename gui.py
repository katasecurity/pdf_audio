import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os

from logic import read_pdf, count_words, count_chars, convert_to_mp3
from history import save_to_history, load_history, clear_history

current_text = ""
current_filename = ""


def on_open_pdf():
    global current_text, current_filename

    path = filedialog.askopenfilename(
        title="Choose a PDF",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not path:
        return

    text = read_pdf(path)
    if not text:
        messagebox.showerror("Error", "No readable text found in this PDF.")
        return

    current_text = text
    current_filename = os.path.basename(path)

    text_box.delete("1.0", tk.END)
    text_box.insert(tk.END, text)

    words = count_words(text)
    chars = count_chars(text)
    stats_label.config(text=f"Words: {words}   |   Characters: {chars}")
    status_label.config(text=f"Loaded: {current_filename}")


def on_convert():
    if not current_text:
        messagebox.showwarning("No text", "Please open a PDF first.")
        return

    status_label.config(text="Converting to MP3... please wait.")
    window.update()

    convert_to_mp3(current_text, output_file="result.mp3", language="ru")

    words = count_words(current_text)
    chars = count_chars(current_text)
    save_to_history(current_filename, words, chars)

    status_label.config(text="Saved as result.mp3 ✓")
    messagebox.showinfo("Done", "result.mp3 has been saved in the project folder.")


def on_show_history():
    entries = load_history()
    history_box.delete("1.0", tk.END)
    if not entries:
        history_box.insert(tk.END, "No conversions yet.")
    else:
        for entry in entries:
            history_box.insert(tk.END, entry + "\n")


def on_clear_history():
    clear_history()
    history_box.delete("1.0", tk.END)
    history_box.insert(tk.END, "History cleared.")