import sys
from chatai import chat_with_memory

title = sys.argv[1]
print(f"--- Sesi {title} dimulai ---")
while True:
    user_input = input("Anda: ")
    if user_input.lower() == "exit": break
    chat_with_memory(title, user_input)