from flask import Flask, request
import requests
import os
import threading
import time

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ===== USER MEMORY =====
user_memory = {}


# ================= TELEGRAM SEND =================
def send_message(chat_id, text):
    if not text:
        text = "Thoda clear likh 🙂"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    try:
        requests.post(url, json=payload, timeout=20)
    except:
        pass


# ================= TYPING ANIMATION =================
def typing_indicator(chat_id, stop_event):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"

    while not stop_event.is_set():
        try:
            requests.post(url, json={
                "chat_id": chat_id,
                "action": "typing"
            }, timeout=10)
        except:
            pass

        time.sleep(4)


# ================= AI REPLY =================
def get_ai_reply(chat_id, user_message):

    if chat_id not in user_memory:
        user_memory[chat_id] = []

    # save user msg
    user_memory[chat_id].append({"role": "user", "content": user_message})
    user_memory[chat_id] = user_memory[chat_id][-12:]  # last 12 msgs

    messages = [
        {
            "role": "system",
            "content": """
You are ReplyShastra.

A boy will tell you his girlfriend chat situation.

You must write the EXACT WhatsApp message he should send her.

Rules:
- Only the sendable message
- Maximum 2 short lines
- Natural Hinglish
- Soft, respectful, emotionally mature tone
- No explanation
- No advice
- No bullet points
- No coaching

Never write poetry.
Write like a real 22 year old Indian boy texting.

Allowed emoji: ❤️ or 🙂
Maximum: one emoji.
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
                "model": "openai/gpt-4o-mini",
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 120
            },
            timeout=60
        )

        data = response.json()

        if "choices" in data:
            reply = data["choices"][0]["message"]["content"].strip()

            # save AI reply
            user_memory[chat_id].append({"role": "assistant", "content": reply})
            return reply

        return "Net slow hai… ek baar fir bhej 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server busy hai… 20 sec baad try kar 🙂"


# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "").strip()

        if not user_message:
            return "ok"

        # /start
        if user_message.lower() == "/start":
            user_memory[chat_id] = []
            send_message(chat_id,
"""Hi! Main ReplyShastra hoon 🙂

GF ignore, naraz, breakup, late reply — sab handle karenge.

Apni situation simple likh 👇""")
            return "ok"

        # typing thread start
        stop_event = threading.Event()
        t = threading.Thread(target=typing_indicator, args=(chat_id, stop_event))
        t.start()

        # AI reply
        reply = get_ai_reply(chat_id, user_message)

        # stop typing
        stop_event.set()
        t.join()

        # send reply
        send_message(chat_id, reply)

    return "ok"


@app.route("/")
def home():
    return "ReplyShastra Running 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
