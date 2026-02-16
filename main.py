import os
import json
import time
import threading
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# -------- Memory (per user) ----------
user_memory = {}

# ---------- typing animation ----------
def send_typing(chat_id, seconds=12):
    end = time.time() + seconds
    while time.time() < end:
        try:
            requests.post(f"{TELEGRAM_API}/sendChatAction",
                          json={"chat_id": chat_id, "action": "typing"})
            time.sleep(4)
        except:
            break

# ---------- send message ----------
def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

# ---------- AI brain ----------
def get_ai_reply(user_id, user_message):

    # store conversation memory
    if user_id not in user_memory:
        user_memory[user_id] = []

    user_memory[user_id].append({"role": "user", "content": user_message})

    # keep last 8 messages only
    user_memory[user_id] = user_memory[user_id][-8:]

    system_prompt = """
You are ReplyShastra.

You are NOT girlfriend.
You are NOT chatbot assistant.

You are a real male best friend helping a boy save his relationship.

Boy comes to you after fight, ignore, breakup fear, anger, guilt.

FIRST understand emotional problem.
Then generate the exact WhatsApp message he should send her.

Important:
- You talk like a supportive bro
- Short natural Hinglish
- 1 or 2 lines only
- Caring but not desperate
- No lectures
- No explanation
- Only message to send girl
- Never say "as an AI"
- Never give advice paragraph
- Never roleplay girl
"""

    try:
        payload = {
            "model": "llama3-70b-8192",
            "messages": [{"role": "system", "content": system_prompt}] + user_memory[user_id],
            "temperature": 0.7,
            "max_tokens": 120
        }

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=50
        )

        data = response.json()
        print("GROQ:", data)

        if data.get("choices"):
            reply = data["choices"][0]["message"]["content"].strip()
            user_memory[user_id].append({"role": "assistant", "content": reply})
            return reply

        return "Ek sec bhai... dobara bhej 🙂"

    except Exception as e:
        print("ERROR:", e)
        return "Server busy hai, 15 sec baad bhej 🙂"


# ---------- webhook ----------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = message.get("text", "")

    # start command
    if text == "/start":
        send_message(chat_id,
        "Hi! Main ReplyShastra hoon 🙂\n\n"
        "GF ignore, naraz, breakup, late reply — sab handle karenge.\n\n"
        "Apni situation simple likh 👇")
        return "ok"

    # typing animation thread
    threading.Thread(target=send_typing, args=(chat_id, 10)).start()

    # small thinking delay
    time.sleep(6)

    reply = get_ai_reply(user_id, text)
    send_message(chat_id, reply)

    return "ok"


@app.route("/")
def home():
    return "ReplyShastra Running"
