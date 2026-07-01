"""
chatai.py - CLI Chat AI menggunakan Groq API
Mendukung riwayat chat per-judul (mirip ChatGPT/Claude), mode tanya cepat,
dan tampilan output berwarna + Markdown rendering (lihat ui.py).

Build ke exe:
    pip install requests rich
    pyinstaller --onefile --name chatai chatai.py

Setelah dibuild, chatai.exe bisa dipanggil dari folder mana saja karena
config.json dan folder data/ otomatis dibuat tepat di sebelah file exe-nya
(bukan di folder tempat cmd sedang aktif).

PENTING: ui.py harus ikut di-copy ke folder yang sama sebelum di-build,
karena file ini di-import langsung (bukan lewat pip).
"""

import sys
import os
import json
import argparse
import requests
from datetime import datetime

import ui

# ---------------------------------------------------------------------------
# Path helper
# ---------------------------------------------------------------------------
def get_base_dir():
    if getattr(sys, "frozen", False):
        # Berjalan sebagai exe hasil PyInstaller
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
DATA_DIR = os.path.join(BASE_DIR, "data")

DEFAULT_CONFIG = {
    "name": "User",
    "link": "https://api.groq.com/openai/v1/chat/completions",
    "model": "llama-3.1-8b-instant",
    "api_key": "",
    "system_prompt": "Kamu adalah asisten AI yang jenius dan membantu."
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
def load_config():
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    for key, value in DEFAULT_CONFIG.items():
        config.setdefault(key, value)
    return config


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Chat history (folder data/)
# ---------------------------------------------------------------------------
def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def get_chat_path(title):
    safe_title = "".join(c for c in title if c not in '<>:"/\\|?*').strip()
    return os.path.join(DATA_DIR, f"{safe_title}.json")


def load_chat(title, config):
    ensure_data_dir()
    path = get_chat_path(title)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "title": title,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "messages": [{"role": "system", "content": config["system_prompt"]}]
    }


def save_chat(title, data):
    ensure_data_dir()
    with open(get_chat_path(title), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def list_chats():
    ensure_data_dir()
    return sorted(f[:-5] for f in os.listdir(DATA_DIR) if f.endswith(".json"))


# ---------------------------------------------------------------------------
# Groq API call
# ---------------------------------------------------------------------------
def call_groq(messages, config, model_override=None):
    if not config.get("api_key"):
        raise RuntimeError("API key belum diset. Gunakan: chatai --api <API_KEY>")

    model = model_override or config["model"]
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    payload = {"model": model, "messages": messages}

    response = requests.post(config["link"], headers=headers, json=payload, timeout=60)
    if response.status_code != 200:
        raise RuntimeError(f"Groq API error {response.status_code}: {response.text}")

    return response.json()["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# Mode: tanya cepat (tanpa memori)
# ---------------------------------------------------------------------------
def quick_chat(question, config, model_override=None):
    messages = [
        {"role": "system", "content": config["system_prompt"]},
        {"role": "user", "content": question}
    ]
    model_used = model_override or config["model"]
    try:
        with ui.console.status("[bold cyan]AI sedang berpikir...[/bold cyan]", spinner="dots"):
            reply = call_groq(messages, config, model_override)
        ui.print_ai_reply(model_used, reply)
    except Exception as e:
        ui.error(str(e))


# ---------------------------------------------------------------------------
# Mode: chat dengan memori (per judul)
# ---------------------------------------------------------------------------
def interactive_chat(title, config, model_override=None):
    data = load_chat(title, config)
    is_new = len(data["messages"]) == 1
    ui.print_session_header(title, is_new)

    model_used = model_override or config["model"]

    while True:
        try:
            user_input = ui.ask(config["name"])
        except (KeyboardInterrupt, EOFError):
            ui.notice("Sesi diakhiri.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            ui.notice("Sesi diakhiri.")
            break

        data["messages"].append({"role": "user", "content": user_input})

        try:
            with ui.console.status("[bold cyan]AI sedang berpikir...[/bold cyan]", spinner="dots"):
                reply = call_groq(data["messages"], config, model_override)
        except Exception as e:
            ui.error(str(e))
            data["messages"].pop()  # jangan simpan pesan user kalau request gagal
            continue

        data["messages"].append({"role": "assistant", "content": reply})
        save_chat(title, data)
        ui.print_ai_reply(model_used, reply)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser():
    parser = argparse.ArgumentParser(
        prog="chatai",
        description="ChatAI - CLI chat dengan Groq API, mendukung riwayat percakapan.",
        add_help=False
    )
    parser.add_argument("question", nargs="?",
                         help="Pertanyaan langsung (mode tanpa memori)")
    parser.add_argument("--api", "-k", metavar="API_KEY",
                         help="Set/ubah API key Groq")
    parser.add_argument("--model", "-m", metavar="MODEL",
                         help="Set/ubah model AI default, atau dipakai sekali saja bersama pertanyaan/--new")
    parser.add_argument("--user", "-u", metavar="NAMA",
                         help="Set nama pengguna")
    parser.add_argument("--new", "-n", metavar="JUDUL",
                         help="Buat/lanjutkan sesi chat dengan memori berdasarkan judul")
    parser.add_argument("--list", "-l", action="store_true",
                         help="Tampilkan daftar sesi chat yang tersimpan")
    parser.add_argument("--help", "-h", action="store_true",
                         help="Tampilkan bantuan")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.help or len(sys.argv) == 1:
        ui.print_help()
        return

    config = load_config()
    changed = False

    if args.api:
        config["api_key"] = args.api
        ui.success("API key berhasil diperbarui.")
        changed = True

    if args.user:
        config["name"] = args.user
        ui.success(f"Nama pengguna diubah menjadi: {args.user}")
        changed = True

    # --model tanpa --new dan tanpa pertanyaan -> ubah model default secara permanen
    if args.model and not args.new and not args.question:
        config["model"] = args.model
        ui.success(f"Model default diubah menjadi: {args.model}")
        changed = True

    if changed:
        save_config(config)

    if args.list:
        ui.print_chat_list(list_chats())
        return

    if args.new:
        interactive_chat(args.new, config, model_override=args.model)
        return

    if args.question:
        quick_chat(args.question, config, model_override=args.model)
        return

    if not changed:
        ui.print_help()


if __name__ == "__main__":
    main()