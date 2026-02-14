from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ---------------- TELEGRAM SEND ----------------
def send_message(chat_id, text):
    if not text:
        text = "Thoda network slow hai… fir se bhej 🙂"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass


# ---------------- AI REPLY ----------------
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
                "max_tokens": 500,
                "messages": [
                    {
                        "role": "system",
                        "content": """You are ReplyShastra — a 23 year old Indian boy helping another boy with relationship problems.

Talk like a real friend in Hinglish WhatsApp chat.

Every reply must:
1 Explain what the girl is thinking
2 Tell what he should do
3 Give 2 ready WhatsApp messages

No AI tone. No lectures. No bullet points."""
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            },
            timeout=45
        )

        data = response.json()

        # ---- SAFE RESPONSE PARSER ----
        if "choices" in data:
            msg = data["choices"][0]

            if "message" in msg and "content" in msg["message"]:
                return msg["message"]["content"]

            if "text" in msg:
                return msg["text"]

        print("OPENROUTER RAW:", data)
        return "Samajh gaya... thoda properly bata kya hua usne exactly kya kiya?"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server busy hai bhai… 10 sec baad fir bhej 🙂"


# ---------------- WEBHOOK ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json

        if "message" not in data:
            return "ok"

        message = data["message"]
        chat_id = message["chat"]["id"]

        # /start greeting
        if "text" in message and message["text"] == "/start":
            send_message(chat_id,
"""Hi! Main ReplyShastra hoon 🙂

GF ignore, GF naraz, crush, breakup — sab solve karenge.

Apni situation detail me bata 👇""")
            return "ok"

        if "text" in message:
            user_message = message["text"]
            reply = get_ai_reply(user_message)
            send_message(chat_id, reply)

        return "ok"

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return "ok"


@app.route("/")
def home():
    return "ReplyShastra Running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
