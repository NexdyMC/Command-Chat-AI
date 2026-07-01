# pyinstaller --onefile chatai.py

import sys
import json
import os
import subprocess
import requests

FILE_NAME = "chatai.json"

def get_file_path(title):
    return f"{title}.json"

def create_chat(title):
    initial_data = {
        "title": title,
        "messages": [{"role": "system", "content": "Kamu adalah asisten AI yang jenius."}]
    }
    with open(get_file_path(title), "w") as f:
        json.dump(initial_data, f, indent=4)
    print(f"Percakapan '{title}' berhasil dibuat.")

def load_data():
    if not os.path.exists(FILE_NAME):
        return {"name": "Nexdy", "link": "https://api.groq.com/openai/v1/chat/completions", "header": {"model": "llama-3.1-8b-instant", "authorization": ""}, "message": [{"role": "system", "message": "kamu adalah ai jenius"}]}
    with open(FILE_NAME, "r") as f:
        return json.load(f)

def save_data(data):
    with open(FILE_NAME, "w") as f:
        json.dump(data, f, indent=4)

def chat_with_memory(title, user_input, model_override=None):
    config = load_data()
    file_path = get_file_path(title)
    
    if not os.path.exists(file_path):
        print("Chat tidak ditemukan. Gunakan --create [title] terlebih dahulu.")
        return

    with open(file_path, "r") as f:
        data = json.load(f)

    data["messages"].append({"role": "user", "content": user_input})

    headers = {"Authorization": "Bearer YOUR_API_KEY", "Content-Type": "application/json"}
    payload = {"model": "llama-3.1-8b-instant", "messages": data["messages"]}
    
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    ai_reply = response.json()["choices"][0]["message"]["content"]

    data["messages"].append({"role": "assistant", "content": ai_reply})
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    
    print(f"\nAI: {ai_reply}")

def chat_with_groq(user_input, model_override=None):
    config = load_data()
    model = model_override if model_override else config["header"]["model"]
    
    headers = {
        "Authorization": f"Bearer {config['header']['authorization']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": config["message"] + [{"role": "user", "content": user_input}]
    }

    try:
        response = requests.post(config["link"], headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        print(f"\n==================== [ {model} ] ====================\n")
        print(result["choices"][0]["message"]["content"])
        
        if response.status_code != 200:
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}") 
        response.raise_for_status()
    
    except Exception as e:  
        print(f"\nError: {e}")

if __name__ == "__main__":
    data = load_data()
    changed = False
    
    if "--create" in sys.argv:
        create_chat(sys.argv[sys.argv.index("--create") + 1])
    elif "--view" in sys.argv:
        title = sys.argv[sys.argv.index("--view") + 1]
        subprocess.Popen(f'start cmd /k "python chat_interface.py {title}"', shell=True)

    if "--api" in sys.argv or "-k" in sys.argv:
        idx = sys.argv.index("--api")
        data["header"]["authorization"] = sys.argv[idx + 1]
        print("API Key done in update")
        changed = True
        
    if "--user" in sys.argv or "-u" in sys.argv:
        idx = sys.argv.index("--user") if "--user" in sys.argv else sys.argv.index("-u")
        data["name"] = sys.argv[idx + 1]
        print(f"Username done in update : {sys.argv[idx + 1]}")
        changed = True
    
    if "-m" in sys.argv or "--model" in sys.argv:
        idx = sys.argv.index("-m") if "-m" in sys.argv else sys.argv.index("--model") 
        data["header"]["model"] = sys.argv[idx + 1]
        print(f"model done in update : {sys.argv[idx + 1]}")
        model_pilihan = sys.argv[idx + 1]
        changed = True
    
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Info Argument")
        print("Argument :")
        print("\t--help, -h \t: memberikan bantuan penggunaan")
        print("\t--user, -u \t: mengubah nama user")
        print("\t--model, -m \t: mengubah jenis model ai")
        print("\t--api, -k \t: mengubah jenis model ai")

    
    if changed:
        save_data(data)
        sys.exit()

    # 2. Logika Chat
    if len(sys.argv) < 2:
        print("Penggunaan: python chatai.py \"Pertanyaan Anda\" [model <nama_model>]")
    else:
        model_pilihan = None
        if "model" in sys.argv:
            idx = sys.argv.index("model")
            model_pilihan = sys.argv[idx + 1]
        
        chat_with_groq(sys.argv[1], model_pilihan)