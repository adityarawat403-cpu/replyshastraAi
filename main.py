from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ================= TOKENS =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# =============== TELEGRAM SEND MESSAGE ===============
def send_message(chat_id, text):
    if not text:
        text = "Samajh gaya... thoda aur detail me bata 🙂"

    # telegram character safety split
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


# =============== AI REPLY FUNCTION ===============
def get_ai_reply(user_message):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "temperature": 0.7,
                "max_tokens": 120,
                "messages": [
                    {
                        "role": "system",
                        "content": """
You are generating a WhatsApp message.

You are NOT talking to the user.
You are NOT an assistant.
You are NOT giving advice.

Your ONLY job:
Write the exact message a boyfriend should send to his girlfriend.

The user will COPY and SEND your message.

ABSOLUTE RULES:
- Output must be ONLY the final message
- Maximum 2 short lines
- Hinglish (Hindi + simple English)
- Romantic, soft, natural
- No explanations
- No tips
- No coaching
- No psychology
- No questions to the user
- No extra sentences
- No roleplay continuation

Never send more than 1 message.

Do not write paragraphs.
Do not write multiple replies.
Do not simulate conversation.

Your output must look exactly like a WhatsApp message ready to copy-paste.
Nothing else.
"""
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            },
            timeout=60
        )

        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()

        return "Thoda network slow hai… 10 sec baad fir bhejo 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server busy hai… 20 sec baad try karo 🙂"


# =============== TELEGRAM WEBHOOK ===============
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

        # START COMMAND GREETING
        if user_message.lower() == "/start":
            send_message(chat_id,
"""Hi! Main ReplyShastra hoon 🙂

GF ignore, naraz, breakup, crush — sab handle karenge.

Apni situation detail me bata 👇
(Main tujhe exact message likh ke dunga jo tu send karega)""")
            return "ok"

        reply = get_ai_reply(user_message)
        send_message(chat_id, reply)

        return "ok"

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return "ok"


# =============== HEALTH CHECK ===============
@app.route("/")
def home():
    return "ReplyShastra running"


# =============== RUN SERVER ===============
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
