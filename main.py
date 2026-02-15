import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# -------- Telegram Send Function --------
def send_message(chat_id, text):
    if not text:
        text = "Samajh gaya... thoda aur detail me bata 🙂"

    # Telegram max 4096 chars — 3500 pe split
    parts = [text[i:i+3500] for i in range(0, len(text), 3500)]

    for part in parts:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": part
        }
        try:
            requests.post(url, json=payload, timeout=15)
        except:
            pass

# -------- AI Reply Function --------
def get_ai_reply(user_text):

    system_prompt = """
Tu ek expert relationship coach aur WhatsApp reply writer hai.

Rules:
- Sirf message likhega jo ladka apni girlfriend ko bheje
- Explanation, tips, ya headings nahi dena
- Natural Hinglish use kar
- Short, emotional aur realistic message likh
- Over filmy ya cringe nahi
- Ek hi final message dena (2-4 lines max)

Situation: ladki sad / naraz / ignore / emotional ho sakti hai
Goal: ladki ko comfort feel ho aur reply kare
"""

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.8,
        "max_tokens": 200
    }

    try:
        r = requests.post(url, headers=headers, json=data, timeout=60)
        res = r.json()
        return res["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("AI ERROR:", e)
        return "Thoda network slow lag raha... 1 min me phir se bhej 🙂"

# -------- Telegram Webhook --------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # /start command
        if text == "/start":
            send_message(chat_id,
            "Hi! Main ReplyShastra hoon 🙂\n\n"
            "GF ignore, naraz, breakup, crush — sab handle karenge.\n\n"
            "Apni situation detail me bata 👇\n"
            "(Main tujhe exact message likh ke dunga jo tu send karega)")
            return "ok"

        # normal message
        ai_reply = get_ai_reply(text)
        send_message(chat_id, ai_reply)

    return "ok"

# -------- Health Check --------
@app.route("/")
def home():
    return "ReplyShastra running"
