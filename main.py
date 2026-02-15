from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ================= TOKENS =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ================= TELEGRAM MESSAGE SENDER (FIXED) =================
def send_message(chat_id, text):
    if not text:
        text = "Samajh gaya... thoda aur detail me bata 🙂"

    # Telegram 4096 char limit — split message
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


# ================= AI REPLY =================
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
                "model": "openrouter/auto",
                "temperature": 0.85,
                "max_tokens": 500,
                "messages": [
                    {
                        "role": "system",
                        "content": """
You are ReplyShastra — a friendly Indian male relationship expert (big brother vibe).

You talk like a real Indian guy in natural Hinglish.

Your job:
1) First understand his situation
2) Explain WHY girl is behaving like that
3) Tell EXACTLY what he should do
4) Give 2-3 ready-to-send messages he can copy paste

Rules:
- Friendly tone (not robotic)
- No “as an AI”
- No bullet formatting markdown
- Simple WhatsApp style text
- Emotional but practical
- Clear actionable advice
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

        return "Samajh nahi aya properly... thoda detail me bata 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server thoda busy hai... 10 sec baad fir bhej 🙂"


# ================= TELEGRAM WEBHOOK =================
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
        if user_message == "/start":
            send_message(chat_id,
"""Hi! Main ReplyShastra hoon 🙂

GF ignore, GF naraz, crush, breakup — sab solve karenge.

Apni situation detail me bata 👇
(Main exact solution + ready messages dunga)""")
            return "ok"

        reply = get_ai_reply(user_message)
        send_message(chat_id, reply)

        return "ok"

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return "ok"


# ================= HOME CHECK =================
@app.route("/")
def home():
    return "ReplyShastra running"


# ================= RUN SERVER =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
