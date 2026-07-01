import json
import os
from datetime import datetime

# Pastikan folder 'data' ada
if not os.path.exists("data"):
    os.makedirs("data")

def create_chat_file(title):
    """Fungsi untuk membuat file baru dengan format default"""
    file_path = os.path.join("data", f"{title}.json")
    
    if os.path.exists(file_path):
        print(f"File {title}.json sudah ada!")
        return

    default_data = {
        "name": "NexdyMC",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "title": title,
        "header": {"model": "llama-3.1-8b-instant"},
        "message": [
            {"role": "system", "content": "kamu adalah ai yang bisa melakukan apa saja dari tahap ke tahap"},
            {"role": "user", "content": ""}
        ]
    }
    
    with open(file_path, "w") as f:
        json.dump(default_data, f, indent=4)
    print(f"File {file_path} berhasil dibuat.")

def save_chat_data(title, data):
    """Fungsi untuk menyimpan update data ke file yang ada"""
    file_path = os.path.join("data", f"{title}.json")
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Data di {file_path} berhasil diperbarui.")