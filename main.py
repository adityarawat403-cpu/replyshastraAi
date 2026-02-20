import os
import time
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ================= ENV =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SITE_URL = os.getenv("SITE_URL")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ================= MEMORY =================
MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)

memory = load_memory()

# ================= TELEGRAM =================
def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload, timeout=15)
    except:
        pass

def typing(chat_id, sec=2):
    url = f"{TELEGRAM_API}/sendChatAction"
    payload = {"chat_id": chat_id, "action": "typing"}
    try:
        requests.post(url, json=payload, timeout=10)
        time.sleep(sec)
    except:
        pass

# ================= SYSTEM PROMPT =================
SYSTEM_PROMPT = """
You are ReplyShastra.

You are a real calm Indian elder brother.

IMPORTANT:
You DO NOT instantly give solution.

You first talk to the user like a human friend.

You must follow stages:

STAGE 1 → Know the situation (ask 1 simple question)
STAGE 2 → Understand details (ask short follow up)
STAGE 3 → Give final message for girlfriend

Rules:
• Very short replies
• Hinglish only
• No lectures
• No psychology words
• Never big paragraphs

When giving final output use EXACT format:

[FINAL MESSAGE]
(only one message user will send to girl, max 2 lines, natural Hinglish, 1 emoji ❤️ or 🥺)

Never give multiple options.
Never explain after final message.
"""

# ================= AI =================
def ask_ai(chat_id, user_text):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": SITE_URL,
        "X-Title": "ReplyShastra",
        "Content-Type": "application/json"
    }

    user_data = memory.get(str(chat_id), {"history": [], "stage": 1})

    history = user_data["history"]
    stage = user_data["stage"]

    history.append({"role": "user", "content": user_text})
    history = history[-10:]

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    data = {
        "model": "openchat/openchat-3.5-0106",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 300
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        res = response.json()

        if "choices" not in res:
            return "Net thoda slow hai... fir bhej 🙂"

        reply = res["choices"][0]["message"]["content"].strip()

        history.append({"role": "assistant", "content": reply})

        # stage progression
        if "[FINAL MESSAGE]" in reply:
            stage = 3
        else:
            if stage < 3:
                stage += 1

        memory[str(chat_id)] = {"history": history, "stage": stage}
        save_memory(memory)

        return reply

    except Exception as e:
        print(e)
        return "Server busy hai... 10 sec baad bhej."

# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" not in data:
        return jsonify({"status": "ok"})

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    if text == "/start":
        memory[str(chat_id)] = {"history": [], "stage": 1}
        save_memory(memory)

        send_message(chat_id,
                     "Bhai aa gaya 🤝\nTension mat le.\nSeedha bata kya hua tum dono ke beech?")
        return jsonify({"status": "ok"})

    typing(chat_id, 2)
    ai_reply = ask_ai(chat_id, text)
    send_message(chat_id, ai_reply)

    return jsonify({"status": "ok"})

@app.route("/", methods=["GET"])
def home():
    return "ReplyShastra Live"
