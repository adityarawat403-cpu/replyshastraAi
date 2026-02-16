from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ===== MEMORY =====
user_memory = {}

# ================= SEND MESSAGE =================
def send_message(chat_id, text):

    if not text:
        text = "Samajh nahi aya... thoda simple likh 🙂"

    # Telegram 4096 char limit
    parts = [text[i:i+3500] for i in range(0, len(text), 3500)]

    for part in parts:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": part}
        try:
            requests.post(url, json=payload, timeout=15)
        except:
            pass


# ================= AI REPLY =================
def get_ai_reply(chat_id, user_message):

    # ---- MEMORY STORE ----
    if chat_id not in user_memory:
        user_memory[chat_id] = []

    user_memory[chat_id].append({"role": "user", "content": user_message})

    # keep only last 8 messages
    user_memory[chat_id] = user_memory[chat_id][-8:]


    messages = [
        {
            "role": "system",
            "content": """
You are ReplyShastra.

A boy will come to you with his chat situation with a girl.

You read his situation and write the exact WhatsApp message he should send her.

Write like a real Indian boy texting on WhatsApp.

Rules:
- Only final sendable message
- Max 2 short lines
- Natural Hinglish
- Soft respectful tone
- No explanation
"""
        }
    ] + user_memory[chat_id]


    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://telegram.org",
                "X-Title": "ReplyShastra"
            },
            json={
                "model": "openrouter/auto",
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 120
            },
            timeout=90
        )

        data = response.json()
        print("RAW AI:", data)

        # ===== SMART PARSER =====
        if "choices" in data and len(data["choices"]) > 0:

            msg = data["choices"][0]["message"]

            # normal string
            if isinstance(msg.get("content"), str) and msg["content"].strip() != "":
                reply = msg["content"].strip()

            # array response (openrouter bug fix)
            elif isinstance(msg.get("content"), list):
                reply = ""
                for part in msg["content"]:
                    if isinstance(part, dict) and "text" in part:
                        reply = part["text"].strip()
                        break
            else:
                reply = ""

            if reply:
                user_memory[chat_id].append({"role": "assistant", "content": reply})
                return reply

        return "Network slow hai... 10 sec baad bhej 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server busy hai... thoda baad try kar 🙂"


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

    # START COMMAND
    if user_message.lower() == "/start":
        user_memory[chat_id] = []
        send_message(chat_id,
"""Hi! Main ReplyShastra hoon 🙂

GF ignore, naraz, late reply — sab handle karenge.

Apni situation simple likh 👇""")
        return "ok"

    reply = get_ai_reply(chat_id, user_message)
    send_message(chat_id, reply)

    return "ok"


# ================= HEALTH CHECK =================
@app.route("/")
def home():
    return "ReplyShastra Running 🚀"


# ================= RUN SERVER =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
