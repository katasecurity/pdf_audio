import os
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from logic import read_pdf, count_words, count_chars, convert_to_mp3
from history import save_entry, load_history, clear_history

DIR = os.path.dirname(os.path.abspath(__file__))
THEME_FILE = os.path.join(DIR, "theme.json")

DARK = {
    "BG": "#1a1a1e", "SURFACE": "#242428", "SURFACE2": "#2d2d32",
    "BORDER": "#3a3a40", "TEXT_PRI": "#f5f5f7", "TEXT_SEC": "#a1a1a6",
    "TEXT_HINT": "#6e6e73", "ACCENT": "#3a8ffe", "ACCENT_D": "#1a6fe0",
    "SUCCESS": "#30d158", "ERROR": "#ff453a", "WARN": "#ffd60a",
    "BTN_OBG": "#2d2d32", "BTN_OFG": "#f5f5f7",
    "BTN_CBG": "#3a8ffe", "BTN_CFG": "#ffffff",
    "BTN_HBG": "#2d2d32", "BTN_HFG": "#a1a1a6", "SEL": "#1a4a8a",
}
LIGHT = {
    "BG": "#f5f5f7", "SURFACE": "#ffffff", "SURFACE2": "#e8e8ed",
    "BORDER": "#d8d8dd", "TEXT_PRI": "#1a1a1e", "TEXT_SEC": "#6e6e73",
    "TEXT_HINT": "#aeaeb2", "ACCENT": "#0071e3", "ACCENT_D": "#0051a8",
    "SUCCESS": "#28a745", "ERROR": "#dc3545", "WARN": "#e67e00",
    "BTN_OBG": "#e8e8ed", "BTN_OFG": "#1a1a1e",
    "BTN_CBG": "#0071e3", "BTN_CFG": "#ffffff",
    "BTN_HBG": "#e8e8ed", "BTN_HFG": "#6e6e73", "SEL": "#cce0ff",
}

FONT   = ("Segoe UI", 11)
FONTB  = ("Segoe UI", 11, "bold")
FONTS  = ("Segoe UI", 9)
FONTSB = ("Segoe UI", 9, "bold")
FONTL  = ("Segoe UI", 14, "bold")
FONTXL = ("Segoe UI", 16, "bold")
FONTM  = ("Consolas", 10)

LANG_MAP = {
    "English  (EN)": "en",
    "Русский   (RU)": "ru",
    "Кыргызча (KY)": "ky",
}

state = {"text": "", "filename": "", "language": "en", "busy": False}


def dk(color, n=18):
    c = color.lstrip("#")
    if len(c) == 3:
        c = c[0]*2 + c[1]*2 + c[2]*2
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    return "#{:02x}{:02x}{:02x}".format(max(0, r-n), max(0, g-n), max(0, b-n))


def flat_btn(parent, text, cmd, bg, fg, padx=14, pady=9):
    b = tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                  activebackground=dk(bg), activeforeground=fg,
                  relief="flat", bd=0, cursor="hand2", font=FONT, padx=padx, pady=pady)
    b.bind("<Enter>", lambda e: b.config(bg=dk(bg)))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b


def load_theme():
    try:
        return json.load(open(THEME_FILE))["theme"]
    except Exception:
        return "light"


def save_theme(name):
    try:
        json.dump({"theme": name}, open(THEME_FILE, "w"))
    except Exception:
        pass


def open_history(root, T, on_reuse):
    win = tk.Toplevel(root)
    win.title("История конверсий")
    win.geometry("540x500")
    win.configure(bg=T["BG"])
    win.grab_set()
    win.bind("<Escape>", lambda e: win.destroy())

    hdr = tk.Frame(win, bg=T["BG"])
    hdr.pack(fill="x", padx=20, pady=(16, 0))
    tk.Label(hdr, text="История конверсий", bg=T["BG"], fg=T["TEXT_PRI"], font=FONTL).pack(side="left")

    def refresh():
        for w in inner.winfo_children():
            w.destroy()
        data = load_history()
        if not data:
            tk.Label(inner, text="Нет записей", bg=T["BG"], fg=T["TEXT_HINT"], font=FONT).pack(pady=50)
            return
        for entry in data:
            card = tk.Frame(inner, bg=T["SURFACE"], highlightbackground=T["BORDER"],
                            highlightthickness=1, pady=8, padx=12)
            card.pack(fill="x", pady=(0, 6))

            row1 = tk.Frame(card, bg=T["SURFACE"])
            row1.pack(fill="x")
            tk.Label(row1, text=entry.get("filename", "—"), bg=T["SURFACE"],
                     fg=T["TEXT_PRI"], font=FONTB, anchor="w").pack(side="left")
            lang = entry.get("language", "en")
            tk.Label(row1, text=f" {lang.upper()} ", bg=T["ACCENT_D"], fg="#fff",
                     font=FONTSB, padx=4).pack(side="left", padx=8)
            tk.Label(row1, text=entry.get("timestamp", ""), bg=T["SURFACE"],
                     fg=T["TEXT_HINT"], font=FONTS).pack(side="right")

            tk.Label(card, text=f"Слов: {entry.get('words', 0)}  ·  Знаков: {entry.get('chars', 0)}",
                     bg=T["SURFACE"], fg=T["TEXT_SEC"], font=FONTS, anchor="w").pack(fill="x", pady=(3, 0))

            preview = entry.get("preview", "")
            if preview:
                tk.Label(card, text=preview[:100] + ("…" if len(preview) > 100 else ""),
                         bg=T["SURFACE"], fg=T["TEXT_HINT"], font=FONTS, anchor="w",
                         wraplength=460, justify="left").pack(fill="x", pady=(2, 4))

            row2 = tk.Frame(card, bg=T["SURFACE"])
            row2.pack(fill="x")
            audio = entry.get("audio")
            if audio and os.path.isfile(audio):
                flat_btn(row2, "▶  Воспроизвести",
                         lambda p=audio: os.startfile(p),
                         T["SURFACE2"], T["ACCENT"], padx=10, pady=4).pack(side="left", padx=(0, 6))
            if preview:
                flat_btn(row2, "↩  Использовать",
                         lambda t=preview: [on_reuse(t), win.destroy()],
                         T["SURFACE2"], T["TEXT_SEC"], padx=10, pady=4).pack(side="left")

    tk.Button(hdr, text="Очистить всё", command=lambda: [clear_history(), refresh()],
              bg=T["BG"], fg=T["ERROR"], activebackground=T["BG"], activeforeground=T["ERROR"],
              relief="flat", bd=0, cursor="hand2", font=FONTS).pack(side="right")
    tk.Frame(win, bg=T["BORDER"], height=1).pack(fill="x", padx=20, pady=10)

    outer = tk.Frame(win, bg=T["BG"])
    outer.pack(fill="both", expand=True, padx=20, pady=(0, 16))
    canvas = tk.Canvas(outer, bg=T["BG"], highlightthickness=0)
    vbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=T["BG"])
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=vbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    vbar.pack(side="right", fill="y")
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    win.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

    refresh()

    footer = tk.Frame(win, bg=T["BG"])
    footer.pack(fill="x", padx=20, pady=(0, 14))
    flat_btn(footer, "✕  Закрыть", win.destroy,
             T["SURFACE2"], T["TEXT_SEC"], padx=16, pady=7).pack(side="right")


def start_app():
    root = tk.Tk()
    root.title("Smart Reader")
    root.geometry("700x540")
    root.minsize(520, 400)

    T = [load_theme()]
    C = [DARK if T[0] == "dark" else LIGHT]

    hdr = tk.Frame(root)
    hdr.pack(fill="x", padx=24, pady=(16, 0))
    title_lbl = tk.Label(hdr, text="Smart Reader", font=FONTXL)
    title_lbl.pack(side="left")
    theme_btn = tk.Button(hdr, relief="flat", bd=0, cursor="hand2", font=FONTS, padx=10, pady=4)
    theme_btn.pack(side="right")
    stats_lbl = tk.Label(hdr, text="Нет файла", font=FONTS)
    stats_lbl.pack(side="right", padx=(0, 12))

    card = tk.Frame(root, highlightthickness=1)
    card.pack(fill="both", expand=True, padx=24, pady=10)
    text_box = tk.Text(card, wrap="word", font=FONTM, relief="flat", bd=0,
                       padx=14, pady=12, state="disabled")
    text_box.pack(fill="both", expand=True, side="left")
    sb = tk.Scrollbar(card, command=text_box.yview, relief="flat", bd=0, width=10)
    sb.pack(fill="y", side="right")
    text_box.configure(yscrollcommand=sb.set)

    sbar = tk.Frame(card)
    sbar.pack(fill="x", side="bottom")
    sep = tk.Frame(sbar, height=1)
    sep.pack(fill="x")
    prog_outer = tk.Frame(sbar, height=5)
    prog_inner = tk.Frame(prog_outer, height=5)
    ibar = tk.Frame(sbar)
    ibar.pack(fill="x", padx=10, pady=5)
    dot = tk.Label(ibar, text="●", font=("Segoe UI", 9))
    dot.pack(side="left")
    status_lbl = tk.Label(ibar, text="Откройте PDF для начала", font=FONTS, anchor="w")
    status_lbl.pack(side="left", padx=(5, 0))
    pct_lbl = tk.Label(ibar, text="", font=FONTS)
    pct_lbl.pack(side="right", padx=(0, 4))

    bottom = tk.Frame(root)
    bottom.pack(fill="x", padx=24, pady=(0, 16))
    left = tk.Frame(bottom)
    left.pack(side="left")
    right = tk.Frame(bottom)
    right.pack(side="right")

    lang_var = tk.StringVar(value="English  (EN)")
    lang_var.trace_add("write", lambda *_: state.update({"language": LANG_MAP.get(lang_var.get(), "en")}))
    lang_dd = tk.OptionMenu(left, lang_var, *LANG_MAP.keys())
    lang_dd.config(relief="flat", bd=0, cursor="hand2", font=FONTS, pady=8, highlightthickness=0)

    btn_open    = flat_btn(left,  "📂  Открыть PDF",    lambda: on_open(),    "#888", "#fff")
    btn_convert = flat_btn(left,  "🎵  Конвертировать", lambda: on_convert(), "#888", "#fff")
    btn_history = flat_btn(right, "🕐  История",        lambda: on_history(), "#888", "#fff")
    btn_convert.config(state="disabled")

    btn_open.pack(side="left", padx=(0, 8))
    lang_dd.pack(side="left", padx=(0, 8))
    btn_convert.pack(side="left")
    btn_history.pack(side="right")

    def set_status(kind, msg):
        colors = {"idle": C[0]["TEXT_HINT"], "loading": C[0]["WARN"],
                  "success": C[0]["SUCCESS"], "error": C[0]["ERROR"]}
        dot.config(fg=colors.get(kind, C[0]["TEXT_HINT"]))
        status_lbl.config(text=msg)

    def set_text(text):
        text_box.config(state="normal")
        text_box.delete("1.0", tk.END)
        text_box.insert(tk.END, text)
        text_box.config(state="disabled")

    def style_convert():
        if str(btn_convert["state"]) == "disabled":
            btn_convert.config(bg=C[0]["SURFACE2"], fg=C[0]["TEXT_HINT"],
                               activebackground=C[0]["SURFACE2"])
        else:
            cb = C[0]["BTN_CBG"]
            btn_convert.config(bg=cb, fg=C[0]["BTN_CFG"], activebackground=dk(cb))
            btn_convert.bind("<Enter>", lambda e: btn_convert.config(bg=dk(cb)))
            btn_convert.bind("<Leave>", lambda e: btn_convert.config(bg=cb))

    def show_progress(pct):
        prog_outer.update_idletasks()
        w = prog_outer.winfo_width()
        prog_inner.place(x=0, y=0, width=max(1, int(w * pct / 100)), height=5)
        pct_lbl.config(text=f"{pct}%")

    def hide_progress():
        prog_inner.place_forget()
        prog_outer.pack_forget()
        pct_lbl.config(text="")

    def apply_theme(name):
        T[0] = name
        C[0] = DARK if name == "dark" else LIGHT
        save_theme(name)

        root.configure(bg=C[0]["BG"])
        for w in (hdr, bottom, left, right):
            w.configure(bg=C[0]["BG"])
        title_lbl.configure(bg=C[0]["BG"], fg=C[0]["TEXT_PRI"])
        stats_lbl.configure(bg=C[0]["BG"], fg=C[0]["TEXT_HINT"])
        theme_btn.configure(
            text="☀  Светлая" if name == "dark" else "🌙  Тёмная",
            bg=C[0]["SURFACE2"], fg=C[0]["TEXT_SEC"],
            activebackground=dk(C[0]["SURFACE2"]),
        )
        card.configure(bg=C[0]["SURFACE"], highlightbackground=C[0]["BORDER"])
        text_box.configure(bg=C[0]["SURFACE"], fg=C[0]["TEXT_PRI"],
                           insertbackground=C[0]["ACCENT"], selectbackground=C[0]["SEL"])
        sb.configure(bg=C[0]["SURFACE2"], troughcolor=C[0]["SURFACE"])
        for w in (sbar, ibar, dot, status_lbl, pct_lbl, prog_outer):
            w.configure(bg=C[0]["SURFACE"])
        sep.configure(bg=C[0]["BORDER"])
        prog_inner.configure(bg=C[0]["ACCENT"])
        status_lbl.configure(fg=C[0]["TEXT_SEC"])
        pct_lbl.configure(fg=C[0]["TEXT_HINT"])

        for widget, bg_key, fg_key in [
            (btn_open,    "BTN_OBG", "BTN_OFG"),
            (btn_history, "BTN_HBG", "BTN_HFG"),
        ]:
            bg = C[0][bg_key]
            widget.configure(bg=bg, fg=C[0][fg_key], activebackground=dk(bg))
            widget.bind("<Enter>", lambda e, b=bg: widget.config(bg=dk(b)))
            widget.bind("<Leave>", lambda e, b=bg: widget.config(bg=b))

        ld = C[0]["BTN_OBG"]
        lang_dd.configure(bg=ld, fg=C[0]["BTN_OFG"], activebackground=dk(ld))
        lang_dd["menu"].configure(bg=C[0]["SURFACE"], fg=C[0]["TEXT_PRI"])

        style_convert()

    theme_btn.configure(command=lambda: apply_theme("light" if T[0] == "dark" else "dark"))

    def on_open():
        if state["busy"]:
            return
        path = filedialog.askopenfilename(title="Выберите PDF", filetypes=[("PDF файлы", "*.pdf")])
        if not path:
            return
        set_status("loading", "Чтение PDF…")
        root.update_idletasks()
        text = read_pdf(path)
        if not text:
            set_status("error", "PDF не содержит текста")
            messagebox.showerror("Ошибка", "PDF не содержит извлекаемого текста.")
            return
        state["text"] = text
        state["filename"] = os.path.basename(path)
        set_text(text)
        stats_lbl.config(text=f"Слов: {count_words(text)}  ·  Знаков: {count_chars(text)}",
                         fg=C[0]["TEXT_SEC"])
        set_status("success", f"Загружено: {state['filename']}")
        btn_convert.config(state="normal")
        style_convert()

    def on_convert():
        if state["busy"] or not state["text"].strip():
            return
        state["busy"] = True
        btn_convert.config(state="disabled", text="⏳  Конвертация…")
        lang_dd.config(state="disabled")
        style_convert()
        set_status("loading", "Конвертируем в MP3…")
        prog_outer.pack(fill="x", padx=10, pady=(0, 0), before=ibar)
        show_progress(0)

        snap_text = state["text"]
        snap_name = state["filename"]
        snap_lang = state["language"]
        out_file  = os.path.join(DIR, "result.mp3")

        def run():
            LANG_NAMES = {"en": "English", "ru": "Русский", "ky": "Кыргызча"}

            def on_translate(src_lang):
                src_name = LANG_NAMES.get(src_lang, src_lang.upper())
                tgt_name = LANG_NAMES.get(snap_lang, snap_lang.upper())
                root.after(0, lambda: set_status("loading", f"Переводим {src_name} → {tgt_name}…"))

            def on_progress(pct):
                root.after(0, lambda p=pct: [
                    show_progress(p),
                    set_status("loading", f"Озвучиваем… {p}%"),
                ])

            try:
                path, is_fallback, used, was_translated = convert_to_mp3(
                    snap_text, out_file, snap_lang,
                    progress_cb=on_progress,
                    translate_cb=on_translate,
                )
                save_entry(snap_name, count_words(snap_text), count_chars(snap_text),
                           snap_lang, snap_text, path)
                root.after(0, lambda: done(path, is_fallback, used, was_translated))
            except Exception as ex:
                root.after(0, lambda: err(str(ex)))

        def done(path, is_fallback, used, was_translated):
            LANG_NAMES = {"en": "English", "ru": "Русский", "ky": "Кыргызча"}
            state["busy"] = False
            btn_convert.config(state="normal", text="🎵  Конвертировать")
            lang_dd.config(state="normal")
            style_convert()
            hide_progress()
            lang_name = LANG_NAMES.get(used, used.upper())
            tag = f" · {lang_name}" + (" (перевод)" if was_translated else "")
            set_status("success", f"Сохранено: result.mp3{tag}")
            msg = "Файл result.mp3 успешно сохранён."
            if is_fallback:
                msg += "\n\n⚠ Кыргызский не поддерживается gTTS. (выбран русский)"
            messagebox.showinfo("Готово", msg)

        def err(msg):
            state["busy"] = False
            btn_convert.config(state="normal", text="🎵  Конвертировать")
            lang_dd.config(state="normal")
            style_convert()
            hide_progress()
            set_status("error", "Ошибка конвертации")
            messagebox.showerror("Ошибка", f"Конвертация не удалась:\n{msg}")

        threading.Thread(target=run, daemon=True).start()

    def on_history():
        def reuse(t):
            state["text"] = t
            set_text(t)
            stats_lbl.config(text=f"Слов: {count_words(t)}  ·  Знаков: {count_chars(t)}",
                             fg=C[0]["TEXT_SEC"])
            btn_convert.config(state="normal")
            style_convert()
            set_status("idle", "Текст загружен из истории")
        open_history(root, C[0], reuse)

    apply_theme(T[0])
    set_status("idle", "Откройте PDF для начала")
    root.mainloop()


if __name__ == "__main__":
    start_app()