from flask import Flask, request
import requests
import os
import threading
import time

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ===== MEMORY STORE =====
user_memory = {}


# ================= TELEGRAM SEND =================
def send_message(chat_id, text):

    if not text:
        text = "Network issue... ek baar fir bhej 🙂"

    parts = [text[i:i+3500] for i in range(0, len(text), 3500)]

    for part in parts:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": part
        }
        try:
            requests.post(url, json=payload, timeout=20)
        except:
            pass


# ================= TYPING ANIMATION =================
def typing(chat_id, stop_event):
    while not stop_event.is_set():
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction",
                json={"chat_id": chat_id, "action": "typing"},
                timeout=10
            )
        except:
            pass
        time.sleep(4)


# ================= AI REPLY =================
def get_ai_reply(chat_id, user_message):

    # ---- MEMORY ----
    if chat_id not in user_memory:
        user_memory[chat_id] = []

    user_memory[chat_id].append({"role": "user", "content": user_message})
    user_memory[chat_id] = user_memory[chat_id][-12:]


    messages = [
        {
            "role": "system",
            "content": """
You are ReplyShastra.

A boy tells you his girlfriend chat situation.

Understand the situation and help him naturally like a real friend.

If he asks:
msg de / kya bheju / reply kya du
→ Write ONLY the exact WhatsApp message.

Rules:
• Max 2 lines
• Natural Hinglish
• Soft emotional tone
• No lecture
• No explanation

If he asks kya karu:
→ Give short friendly help (max 3 lines)
"""
        }
    ] + user_memory[chat_id]


    # typing animation
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
                "model": "mistralai/mistral-7b-instruct",
                "messages": messages,
                "temperature": 0.9,
                "max_tokens": 160
            },
            timeout=65
        )

        stop_event.set()

        data = response.json()

        # SAFE PARSE
        reply = None

        if "choices" in data and len(data["choices"]) > 0:

            choice = data["choices"][0]

            if "message" in choice and "content" in choice["message"]:
                reply = choice["message"]["content"]

            elif "text" in choice:
                reply = choice["text"]

        if not reply or len(reply.strip()) < 3:
            return "Net slow lag raha... ek baar fir bhej 🙂"

        # SAVE MEMORY
        user_memory[chat_id].append({"role": "assistant", "content": reply})

        return reply.strip()

    except Exception as e:
        stop_event.set()
        print("AI ERROR:", e)
        return "Server busy hai... 1 min baad try kar 🙂"


# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:

        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        if user_message:

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
