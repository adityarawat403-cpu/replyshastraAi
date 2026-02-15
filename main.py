from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ENV TOKENS (Railway me set honge)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ========== TELEGRAM MESSAGE SENDER ==========
def send_message(chat_id, text):
    if not text:
        text = "Samajh gaya... thoda aur detail me bata 🙂"

    # Telegram limit 4096 chars (safe split)
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


# ========== AI REPLY ==========
def get_ai_reply(user_message):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://telegram.org",
                "X-Title": "ReplyShastra"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "temperature": 0.7,
                "max_tokens": 800,
                "messages": [
                    {
                        "role": "system",
                        "content": """You are ReplyShastra — a 23 year old Indian boy + relationship expert friend.

Your job:
Understand the user's relationship problem and explain the psychology behind what the girl might be thinking. Then give step-by-step advice AND ready-to-send messages.

Rules:
- Talk like a real human friend (Hinglish)
- Be emotionally understanding
- No short robotic replies
- First understand situation
- Then explain what is happening
- Then tell exactly what he should do
- Then give 2-3 ready-to-send WhatsApp messages
- Never say "I am an AI"
- Never ask too many questions
- If user writes very small message (like "gf ignore kar rahi hai") you must still give a full explanation and solution."""
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            },
            timeout=90
        )

        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()

        return "Network thoda slow hai... ek baar aur bhej 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server busy hai... 20 sec baad try karo 🙂"


# ========== TELEGRAM WEBHOOK ==========
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json

        if "message" not in data:
            return "ok"

        message = data["message"]

        if "text" not in message:
            return "ok"

        chat_id = message["chat"]["id"]
        user_message = message["text"]

        # /start greeting
        if user_message == "/start":
            intro = """Hi! Main ReplyShastra hoon 🙂

GF ignore, naraz, breakup, crush — sab handle karenge.

Apni situation detail me bata 👇
(Main tujhe exact samjhaunga + ready message bhi dunga)"""
            send_message(chat_id, intro)
            return "ok"

        # AI reply
        reply = get_ai_reply(user_message)
        send_message(chat_id, reply)

        return "ok"

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return "ok"


# ========== HEALTH CHECK ==========
@app.route("/")
def home():
    return "ReplyShastra running"


# ========== RUN ==========
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
