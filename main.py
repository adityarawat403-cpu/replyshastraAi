from flask import Flask, request
import requests
import os
import threading
import time

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ===== MEMORY (per user chat history) =====
user_memory = {}

# ================= TELEGRAM SEND =================
def send_message(chat_id, text):
    if not text:
        text = "Samajh nahi aya bhai, thoda simple likh 🙂"

    parts = [text[i:i+3500] for i in range(0, len(text), 3500)]

    for part in parts:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": part}
        try:
            requests.post(url, json=payload, timeout=15)
        except:
            pass


# ================= TYPING ANIMATION =================
def typing(chat_id, stop_event):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
    payload = {"chat_id": chat_id, "action": "typing"}

    while not stop_event.is_set():
        try:
            requests.post(url, json=payload, timeout=10)
        except:
            pass
        time.sleep(4)


# ================= AI REPLY =================
def get_ai_reply(chat_id, user_message):

    # ---------- MEMORY ----------
    if chat_id not in user_memory:
        user_memory[chat_id] = []

    user_memory[chat_id].append({"role": "user", "content": user_message})
    user_memory[chat_id] = user_memory[chat_id][-10:]  # keep last 10 messages

    messages = [
        {
            "role": "system",
            "content": """
You are ReplyShastra.

You are a real Indian guy helping a friend handle girlfriend texting situations.

You do 2 jobs:

If user asks what to DO:
→ Give short friendly guidance (max 3 lines)

If user asks what to SEND (msg de / kya bheju / reply kya du):
→ Write ONLY the exact WhatsApp message.

Message rules:
• Max 2 lines
• Natural Hinglish
• Emotional but calm
• No lectures
• No psychology
• No bullet points
• No long explanation

Never sound like therapist.
Never sound formal.
Sound like a trusted elder brother.
"""
        }
    ] + user_memory[chat_id]

    stop_event = threading.Event()
    typing_thread = threading.Thread(target=typing, args=(chat_id, stop_event))
    typing_thread.start()

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 180
            },
            timeout=60
        )

        stop_event.set()

        data = response.json()

        if "choices" in data:
            reply = data["choices"][0]["message"]["content"]

            user_memory[chat_id].append({"role": "assistant", "content": reply})
            return reply

        return "Net slow lag raha... 20 sec baad fir bhej 🙂"

    except Exception as e:
        stop_event.set()
        print("AI ERROR:", e)
        return "Server busy hai bhai... 1 min baad try kar 🙂"


# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        if user_message:

            # RESET MEMORY
            if user_message.lower() == "/start":
                user_memory[chat_id] = []
                send_message(chat_id,
"""Hi! Main ReplyShastra hoon 🙂

GF ignore, naraz, breakup, late reply — sab handle karenge.

Apni situation simple likh 👇""")
                return "ok"

            reply = get_ai_reply(chat_id, user_message)
            send_message(chat_id, reply)

    return "ok"


@app.route("/")
def home():
    return "ReplyShastra Running 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
