from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ================= TOKENS =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ============ TELEGRAM SEND FUNCTION ============
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    requests.post(url, json=payload)


# ============ AI RESPONSE FUNCTION ============
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
                "temperature": 0.6,
                "max_tokens": 500,
                "messages": [
                    {
                        "role": "system",
                        "content": """You are ReplyShastra — a 23 year old Indian guy helping another boy with his relationship problems.

You talk like a real friend/bhai on WhatsApp, not like a coach, not like a therapist, and never like an AI.

Your behavior:
Friendly, casual Hinglish, human tone.

In EVERY reply you must:

1) First explain what the girl is likely thinking or feeling.
2) Then clearly tell what he should do (simple practical steps).
3) Then give 2 or 3 ready-to-copy WhatsApp messages he can send her.

Rules:
- No robotic tone
- No “as an AI”
- No bullet symbols
- No long lectures
- Write like real WhatsApp chat
- Natural Hinglish
- Helpful but chill
- Do not say you are an AI

Your reply must feel like an experienced friend guiding him."""
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
            return data["choices"][0]["message"]["content"]

        return "Network thoda slow hai… 10 sec baad fir bhej 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server busy hai… thodi der baad try kar 🙂"


# ============ TELEGRAM WEBHOOK ============
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" not in data:
        return "ok"

    message = data["message"]

    chat_id = message["chat"]["id"]

    # START COMMAND GREETING
    if "text" in message and message["text"] == "/start":
        send_message(chat_id,
"""Hi! Main ReplyShastra hoon 🙂

Main help kar sakta hoon:
GF ignore
GF naraz
Crush approach
Seen ignore
Breakup

Samne wali ne kya socha + tumhe kya karna hai + ready messages sab dunga.

Apni situation detail me bata 👇""")
        return "ok"

    # NORMAL MESSAGE
    if "text" in message:
        user_message = message["text"]
        reply = get_ai_reply(user_message)
        send_message(chat_id, reply)

    return "ok"


# ============ HEALTH CHECK ============
@app.route("/")
def home():
    return "ReplyShastra Running"


# ============ RUN ============
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
