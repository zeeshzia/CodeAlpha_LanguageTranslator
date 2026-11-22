import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import urllib.request
import urllib.parse

# Language name -> code
LANGUAGES = {
    "English": "en",
    "Urdu": "ur",
    "Hindi": "hi",
    "Arabic": "ar",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Chinese": "zh-CN",
}

NON_LATIN = ("Urdu", "Hindi", "Arabic", "Chinese")
HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read().decode("utf-8"))

def google_gtx(text, src, tgt):
    q = urllib.parse.quote(text)
    url = ("https://translate.googleapis.com/translate_a/single"
           f"?client=gtx&sl={src}&tl={tgt}&dt=t&q={q}")
    data = fetch_json(url)
    return "".join(part[0] for part in data[0] if part[0])


def lingva(text, src, tgt, host):
    q = urllib.parse.quote(text, safe="")
    data = fetch_json(f"https://{host}/api/v1/{src}/{tgt}/{q}")
    return data["translation"]


def lingva_1(text, src, tgt):
    return lingva(text, src, tgt, "lingva.ml")


def lingva_2(text, src, tgt):
    return lingva(text, src, tgt, "lingva.lunar.icu")


def mymemory(text, src, tgt):
    q = urllib.parse.quote(text)
    url = f"https://api.mymemory.translated.net/get?q={q}&langpair={src}|{tgt}"
    data = fetch_json(url)
    return data["responseData"]["translatedText"]


SERVICES = [google_gtx, lingva_1, lingva_2, mymemory]


def is_valid(result, text, tgt_name):
    if not result or not result.strip():
        return False
    if result.strip().lower() == text.strip().lower():
        return False
    if "MYMEMORY WARNING" in result.upper():
        return False
    if tgt_name in NON_LATIN and result.isascii():
        return False
    return True


def do_translation(text, src_name, tgt_name):
    src, tgt = LANGUAGES[src_name], LANGUAGES[tgt_name]
    for service in SERVICES:
        try:
            result = service(text, src, tgt)
            if is_valid(result, text, tgt_name):
                return result
        except Exception:
            continue  # try the next service
    raise Exception("All translation services are busy or offline.\n"
                    "Check your internet and try again in a minute.")


# ---------- UI logic ----------
def set_output(text):
    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, text)
    output_box.config(state="disabled")


def worker(text, src_name, tgt_name):
    try:
        result = do_translation(text, src_name, tgt_name)
        root.after(0, finish, result, None)
    except Exception as e:
        root.after(0, finish, None, str(e))


def finish(result, error):
    translate_btn.config(state="normal")
    if error:
        status_var.set("Failed")
        messagebox.showerror("Error", error)
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