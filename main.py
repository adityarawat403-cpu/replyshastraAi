from flask import Flask, request
import requests
import os
import json
import time
import threading

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ================= MEMORY =================

MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def remember(chat_id, role, content):
    memory = load_memory()
    chat_id = str(chat_id)

    if chat_id not in memory:
        memory[chat_id] = []

    memory[chat_id].append({
        "role": role,
        "content": content
    })

    # keep last 20 messages only
    memory[chat_id] = memory[chat_id][-20:]
    save_memory(memory)

def get_history(chat_id):
    memory = load_memory()
    return memory.get(str(chat_id), [])


# ================= TELEGRAM =================

def send_typing(chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
    payload = {
        "chat_id": chat_id,
        "action": "typing"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass


def send_message(chat_id, text):
    if not text:
        text = "Samajh nahi aya… thoda simple likh 🙂"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        requests.post(url, json=payload, timeout=15)
    except:
        pass


# ================= GROQ AI =================

def ask_groq(messages):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.6,
        "max_tokens": 180
    }

    response = requests.post(url, headers=headers, json=data, timeout=60)
    result = response.json()

    return result["choices"][0]["message"]["content"].strip()


# ================= MASTER BRAIN PROMPT =================

MASTER_PROMPT = """
You are ReplyShastra.

You are a real male friend helping a boy handle his relationship situation.

You first understand the situation internally.
Then you write the exact message he should send to the girl.

IMPORTANT:
You DO NOT give advice.
You DO NOT explain anything.
You DO NOT talk to the boy.

You ONLY write the final WhatsApp message for the girl.

Rules:
- Only 1 message
- Maximum 2 short lines
- Natural Hinglish
- Soft, mature tone
- No lectures
- No psychology
- No bullet points
- No coaching

Message must feel real and human.
Copy-paste ready.
Allowed emoji: ❤️ or 🙂 (max one)
"""


# ================= AI REPLY =================

def get_ai_reply(chat_id, user_message):

    # typing animation for ~20 sec
    def typing_loop():
        for _ in range(6):
            send_typing(chat_id)
            time.sleep(3)

    threading.Thread(target=typing_loop).start()

    history = get_history(chat_id)

    messages = [
        {"role": "system", "content": MASTER_PROMPT}
    ] + history + [
        {"role": "user", "content": user_message}
    ]

    try:
        reply = ask_groq(messages)

        # memory save
        remember(chat_id, "user", user_message)
        remember(chat_id, "assistant", reply)

        return reply

    except Exception as e:
        print("AI ERROR:", e)
        return "Network slow lag raha… 20 sec baad fir bhej 🙂"


# ================= WEBHOOK =================

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" not in data:
        return "ok"

    message = data["message"]

    if "text" not in message:
        return "ok"

    chat_id = message["chat"]["id"]
    user_message = message["text"]

    if user_message == "/start":
        send_message(chat_id,
"""Hi! Main ReplyShastra hoon 🙂

Apni situation simple likh.
Main tujhe exact message dunga jo tu usse bhejega 👇""")
        return "ok"

    reply = get_ai_reply(chat_id, user_message)
    send_message(chat_id, reply)

    return "ok"


@app.route("/")
def home():
    return "ReplyShastra Running 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
