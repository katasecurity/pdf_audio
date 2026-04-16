import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os

from logic import read_pdf, count_words, count_chars, convert_to_mp3
from history import save_to_history, load_history, clear_history

<<<<<<< HEAD

=======
>>>>>>> da0bc8ce3b0ead4b06839ed60e2df41077819a69
current_text = ""
current_filename = ""


<<<<<<< HEAD

=======
>>>>>>> da0bc8ce3b0ead4b06839ed60e2df41077819a69
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
<<<<<<< HEAD
    history_box.insert(tk.END, "History cleared.")



def start_app():
    global window, text_box, stats_label, status_label, history_box

    window = tk.Tk()
    window.title("Smart Reader")
    window.geometry("700x540")
    window.resizable(False, False)


    tabs = ttk.Notebook(window)
    tabs.pack(fill="both", expand=True)

    tab_reader = tk.Frame(tabs, bg="#f5f5f5")
    tabs.add(tab_reader, text="  Reader  ")

    btn_frame = tk.Frame(tab_reader, bg="#f5f5f5")
    btn_frame.pack(pady=10)

    tk.Button(
        btn_frame, text="Open PDF", width=16,
        bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
        command=on_open_pdf
    ).pack(side="left", padx=6)

    tk.Button(
        btn_frame, text="Convert to MP3", width=16,
        bg="#2196F3", fg="white", font=("Arial", 10, "bold"),
        command=on_convert
    ).pack(side="left", padx=6)

    stats_label = tk.Label(
        tab_reader, text="Words: —   |   Characters: —",
        fg="gray", bg="#f5f5f5", font=("Arial", 9)
    )
    stats_label.pack()

    text_box = tk.Text(
        tab_reader, wrap="word",
        font=("Courier", 10), bg="white", relief="flat",
        padx=10, pady=10
    )
    text_box.pack(fill="both", expand=True, padx=12, pady=6)

    status_label = tk.Label(
        tab_reader, text="Open a PDF to get started.",
        fg="#388E3C", bg="#f5f5f5", anchor="w", font=("Arial", 9)
    )
    status_label.pack(fill="x", padx=14, pady=(0, 6))


    tab_history = tk.Frame(tabs, bg="#f5f5f5")
    tabs.add(tab_history, text="  History  ")

    hist_btn_frame = tk.Frame(tab_history, bg="#f5f5f5")
    hist_btn_frame.pack(pady=10)

    tk.Button(
        hist_btn_frame, text="Load History", width=14,
        bg="#607D8B", fg="white", font=("Arial", 10, "bold"),
        command=on_show_history
    ).pack(side="left", padx=6)

    tk.Button(
        hist_btn_frame, text="Clear History", width=14,
        bg="#F44336", fg="white", font=("Arial", 10, "bold"),
        command=on_clear_history
    ).pack(side="left", padx=6)

    tk.Label(
        tab_history,
        text="Every conversion you make is saved here.",
        fg="gray", bg="#f5f5f5", font=("Arial", 9)
    ).pack()

    history_box = tk.Text(
        tab_history, wrap="word",
        font=("Courier", 10), bg="white", relief="flat",
        padx=10, pady=10
    )
    history_box.pack(fill="both", expand=True, padx=12, pady=6)

    window.mainloop()
=======
    history_box.insert(tk.END, "History cleared.")
>>>>>>> da0bc8ce3b0ead4b06839ed60e2df41077819a69
