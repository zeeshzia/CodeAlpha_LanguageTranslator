import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from deep_translator import GoogleTranslator, MyMemoryTranslator

# Language name -> (Google code, MyMemory name)
LANGUAGES = {
    "English": ("en", "english"),
    "Urdu": ("ur", "urdu"),
    "Hindi": ("hi", "hindi"),
    "Arabic": ("ar", "arabic"),
    "French": ("fr", "french"),
    "German": ("de", "german"),
    "Spanish": ("es", "spanish"),
    "Chinese": ("zh-CN", "chinese simplified"),
}


def do_translation(text, src_name, tgt_name):
    src_g, src_m = LANGUAGES[src_name]
    tgt_g, tgt_m = LANGUAGES[tgt_name]

    # Google: 3 attempts with waiting
    for _ in range(3):
        try:
            result = GoogleTranslator(source=src_g, target=tgt_g).translate(text)
            if result:
                return result
        except Exception:
            time.sleep(3)

    # Backup translator
    result = MyMemoryTranslator(source=src_m, target=tgt_m).translate(text)
    non_latin = tgt_name in ("Urdu", "Hindi", "Arabic", "Chinese")
    bad = (
        not result
        or result.strip().lower() == text.strip().lower()
        or (non_latin and result.isascii())
    )
    if bad:
        raise Exception("Google is busy. Wait 2 minutes and try again.")
    return result


def set_output(text):
    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, text)
    output_box.config(state="disabled")


def worker(text, src_name, tgt_name):
    try:
        result = do_translation(text, src_name, tgt_name)
        root.after(0, lambda: finish(result, None))
    except Exception as e:
        root.after(0, lambda: finish(None, e))


def finish(result, error):
    translate_btn.config(state="normal")
    if error:
        status_var.set("Failed")
        messagebox.showerror(
            "Error",
            "Translation failed. Check your internet and try again.\n\n" + str(error),
        )
    else:
        set_output(result)
        status_var.set("Done")


def translate_text():
    text = input_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Empty", "Please enter some text first.")
        return
    if source_var.get() == target_var.get():
        messagebox.showwarning("Same language", "Please choose different languages.")
        return
    translate_btn.config(state="disabled")
    status_var.set("Translating...")
    threading.Thread(
        target=worker,
        args=(text, source_var.get(), target_var.get()),
        daemon=True,
    ).start()


def copy_text():
    text = output_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Nothing to copy", "Translate something first.")
        return
    root.clipboard_clear()
    root.clipboard_append(text)
    status_var.set("Copied to clipboard")


def swap_languages():
    s, t = source_var.get(), target_var.get()
    source_var.set(t)
    target_var.set(s)


def clear_all():
    input_box.delete("1.0", tk.END)
    set_output("")
    status_var.set("Ready")


# ---------------- UI ----------------
root = tk.Tk()
root.title("Language Translation Tool")
root.geometry("620x620")

source_var = tk.StringVar(value="English")
target_var = tk.StringVar(value="Urdu")
status_var = tk.StringVar(value="Ready")

top = tk.Frame(root)
top.pack(pady=12)
ttk.Combobox(top, textvariable=source_var, values=list(LANGUAGES),
             state="readonly", width=15).grid(row=0, column=0, padx=5)
tk.Button(top, text="⇄", command=swap_languages, width=3).grid(row=0, column=1)
ttk.Combobox(top, textvariable=target_var, values=list(LANGUAGES),
             state="readonly", width=15).grid(row=0, column=2, padx=5)

tk.Label(root, text="Enter text:").pack()
input_box = tk.Text(root, height=8, width=65, font=("Arial", 11))
input_box.pack(pady=5)

btns = tk.Frame(root)
btns.pack(pady=8)
translate_btn = tk.Button(btns, text="Translate", command=translate_text,
                          bg="#4CAF50", fg="white", width=15)
translate_btn.grid(row=0, column=0, padx=5)
tk.Button(btns, text="Clear", command=clear_all, width=10).grid(row=0, column=1, padx=5)

tk.Label(root, text="Translation:").pack()
output_box = tk.Text(root, height=8, width=65, font=("Arial", 11), state="disabled")
output_box.pack(pady=5)

tk.Button(root, text="Copy", command=copy_text, width=15).pack(pady=8)
tk.Label(root, textvariable=status_var, fg="gray").pack()

root.mainloop()
