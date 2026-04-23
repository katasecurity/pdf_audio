import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading

from logic import read_pdf, count_words, count_chars, convert_to_mp3
from history import save_entry, load_history, clear_history

BG          = "#f5f5f7"
SURFACE     = "#ffffff"
BORDER      = "#e0e0e5"
TEXT_PRI    = "#1a1a1e"
TEXT_SEC    = "#6e6e73"
TEXT_HINT   = "#aeaeb2"
ACCENT      = "#0071e3"
ACCENT_DARK = "#0051a8"
BTN_OPEN    = "#f0f0f5"
BTN_CONV    = "#0071e3"
BTN_HIST    = "#f0f0f5"
SUCCESS     = "#34c759"
ERROR       = "#ff3b30"
WARN        = "#ff9f0a"
FONT        = ("SF Pro Display", 11) if os.name == "nt" else ("Helvetica Neue", 11)
FONT_SMALL  = ("SF Pro Display", 9)  if os.name == "nt" else ("Helvetica Neue", 9)
FONT_MONO   = ("SF Mono", 10)        if os.name == "nt" else ("Courier New", 10)

class AppState:
    text: str     = ""
    filename: str = ""


state = AppState()


def _btn(parent, text, command, bg, fg, width=14, padx=0, pady=0):
    b = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
        relief="flat", bd=0, cursor="hand2",
        font=FONT, width=width,
        padx=padx, pady=pady
    )
    b.bind("<Enter>", lambda e: b.config(bg=_darken(bg)))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b


def _darken(hex_color, amount=12):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r, g, b = max(0, r - amount), max(0, g - amount), max(0, b - amount)
    return f"#{r:02x}{g:02x}{b:02x}"


def _card(parent, **kwargs):
    return tk.Frame(parent, bg=SURFACE, relief="flat", bd=0, **kwargs)


def _status(dot_widget, label_widget, color, text):
    dot_widget.config(bg=color)
    label_widget.config(text=text, fg=TEXT_SEC)


def open_history_window(root):
    entries = load_history()

    win = tk.Toplevel(root)
    win.title("История конверсий")
    win.geometry("480x420")
    win.configure(bg=BG)
    win.resizable(False, False)
    win.grab_set()

    header = tk.Frame(win, bg=BG)
    header.pack(fill="x", padx=20, pady=(16, 0))

    tk.Label(header, text="История конверсий", bg=BG, fg=TEXT_PRI,
             font=(FONT[0], 14, "bold")).pack(side="left")

    def do_clear():
        clear_history()
        _refresh()

    tk.Button(header, text="Очистить", command=do_clear,
              bg=BG, fg=ERROR, activebackground=BG, activeforeground=ERROR,
              relief="flat", bd=0, cursor="hand2",
              font=(FONT[0], 10)).pack(side="right", pady=2)

    tk.Frame(win, bg=BORDER, height=1).pack(fill="x", padx=20, pady=10)

    container = tk.Frame(win, bg=BG)
    container.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    canvas   = tk.Canvas(container, bg=BG, highlightthickness=0, bd=0)
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=BG)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    empty_lbl = tk.Label(scroll_frame, text="Нет конверсий",
                         bg=BG, fg=TEXT_HINT, font=FONT)

    def _refresh():
        for widget in scroll_frame.winfo_children():
            widget.destroy()
        data = load_history()
        if not data:
            empty_lbl = tk.Label(scroll_frame, text="Нет конверсий",
                                 bg=BG, fg=TEXT_HINT, font=FONT)
            empty_lbl.pack(pady=40)
            return
        for i, entry in enumerate(data):
            row = tk.Frame(scroll_frame, bg=SURFACE, pady=10, padx=14)
            row.pack(fill="x", pady=(0, 6))

            top = tk.Frame(row, bg=SURFACE)
            top.pack(fill="x")
            tk.Label(top, text=entry.get("filename", "—"), bg=SURFACE,
                     fg=TEXT_PRI, font=(FONT[0], 10, "bold"),
                     anchor="w").pack(side="left")
            tk.Label(top, text=entry.get("timestamp", ""), bg=SURFACE,
                     fg=TEXT_HINT, font=FONT_SMALL).pack(side="right")

            meta_text = f"Слов: {entry.get('words', 0)}   ·   Знаков: {entry.get('chars', 0)}"
            tk.Label(row, text=meta_text, bg=SURFACE, fg=TEXT_SEC,
                     font=FONT_SMALL, anchor="w").pack(fill="x", pady=(3, 0))

            if i < len(data) - 1:
                tk.Frame(scroll_frame, bg=BORDER, height=1).pack(fill="x", pady=(0, 6))

    _refresh()

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    win.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))


def start_app():
    root = tk.Tk()
    root.title("Smart Reader")
    root.geometry("680x540")
    root.minsize(520, 420)
    root.configure(bg=BG)

    header_frame = tk.Frame(root, bg=BG, pady=0)
    header_frame.pack(fill="x", padx=20, pady=(14, 0))

    tk.Label(header_frame, text="Smart Reader", bg=BG, fg=TEXT_PRI,
             font=(FONT[0], 15, "bold")).pack(side="left")

    stats_lbl = tk.Label(header_frame, text="Нет файла", bg=BG,
                         fg=TEXT_HINT, font=FONT_SMALL)
    stats_lbl.pack(side="right", pady=2)

    card = _card(root, highlightbackground=BORDER,
                 highlightthickness=1)
    card.pack(fill="both", expand=True, padx=20, pady=12)

    text_box = tk.Text(
        card, wrap="word", font=FONT_MONO,
        bg=SURFACE, fg=TEXT_PRI,
        relief="flat", bd=0, padx=16, pady=14,
        insertbackground=ACCENT,
        selectbackground="#cce0ff",
        selectforeground=TEXT_PRI,
        state="disabled"
    )
    text_box.pack(fill="both", expand=True)

    scrollbar = tk.Scrollbar(card, command=text_box.yview,
                             relief="flat", bd=0, width=10)
    text_box.configure(yscrollcommand=scrollbar.set)

    status_bar = tk.Frame(card, bg=SURFACE)
    status_bar.pack(fill="x", padx=0)
    tk.Frame(status_bar, bg=BORDER, height=1).pack(fill="x")

    inner_bar = tk.Frame(status_bar, bg=SURFACE)
    inner_bar.pack(fill="x", padx=12, pady=6)

    dot = tk.Label(inner_bar, text="●", bg=SURFACE, fg=TEXT_HINT,
                   font=(FONT[0], 9))
    dot.pack(side="left")

    status_lbl = tk.Label(inner_bar, text="Откройте PDF для начала",
                          bg=SURFACE, fg=TEXT_SEC, font=FONT_SMALL,
                          anchor="w")
    status_lbl.pack(side="left", padx=(5, 0))

    bottom = tk.Frame(root, bg=BG)
    bottom.pack(fill="x", padx=20, pady=(0, 16))

    left_btns = tk.Frame(bottom, bg=BG)
    left_btns.pack(side="left", fill="x", expand=True)

    right_area = tk.Frame(bottom, bg=BG)
    right_area.pack(side="right")

    def set_text(text):
        text_box.config(state="normal")
        text_box.delete("1.0", tk.END)
        text_box.insert(tk.END, text)
        text_box.config(state="disabled")

    def on_open():
        path = filedialog.askopenfilename(
            title="Выберите PDF",
            filetypes=[("PDF файлы", "*.pdf")]
        )
        if not path:
            return

        _status(dot, status_lbl, WARN, "Чтение PDF...")
        root.update()

        text = read_pdf(path)
        if not text:
            _status(dot, status_lbl, ERROR, "Файл не содержит текста")
            messagebox.showerror("Ошибка", "PDF не содержит извлекаемого текста")
            return

        state.text     = text
        state.filename = os.path.basename(path)

        set_text(text)

        words = count_words(text)
        chars = count_chars(text)
        stats_lbl.config(text=f"Слов: {words}  ·  Знаков: {chars}", fg=TEXT_SEC)
        _status(dot, status_lbl, SUCCESS, f"Загружено: {state.filename}")
        btn_convert.config(state="normal", bg=BTN_CONV, fg="white",
                           activebackground=ACCENT_DARK)

    def on_convert():
        if not state.text:
            messagebox.showwarning("Нет текста", "Сначала откройте PDF файл")
            return

        btn_convert.config(state="disabled", text="Конвертация...")
        _status(dot, status_lbl, WARN, "Конвертируем в MP3...")
        root.update()

        def run():
            try:
                convert_to_mp3(state.text, output_file="result.mp3", language="ru")
                words = count_words(state.text)
                chars = count_chars(state.text)
                save_entry(state.filename, words, chars)
                root.after(0, on_done)
            except Exception as e:
                root.after(0, lambda: on_error(str(e)))

        def on_done():
            _status(dot, status_lbl, SUCCESS, "Сохранено: result.mp3")
            btn_convert.config(state="normal", text="Конвертировать в MP3")
            messagebox.showinfo("Готово", "Файл result.mp3 сохранён в папке проекта")

        def on_error(msg):
            _status(dot, status_lbl, ERROR, "Ошибка конвертации")
            btn_convert.config(state="normal", text="Конвертировать в MP3")
            messagebox.showerror("Ошибка", f"Конвертация не удалась:\n{msg}")

        threading.Thread(target=run, daemon=True).start()

    btn_open = _btn(
        left_btns,
        text="Открыть PDF",
        command=on_open,
        bg=BTN_OPEN, fg=TEXT_PRI,
        width=14, padx=6, pady=9
    )
    btn_open.pack(side="left", padx=(0, 10))

    btn_convert = _btn(
        left_btns,
        text="Конвертировать в MP3",
        command=on_convert,
        bg=BTN_CONV, fg="white",
        width=20, padx=6, pady=9
    )
    btn_convert.config(
        state="disabled",
        bg=BTN_OPEN, fg=TEXT_HINT,
        activebackground=BTN_OPEN
    )
    btn_convert.pack(side="left")

    btn_history = _btn(
        right_area,
        text="История",
        command=lambda: open_history_window(root),
        bg=BTN_HIST, fg=TEXT_SEC,
        width=9, padx=6, pady=9
    )
    btn_history.pack(side="right")

    root.mainloop()