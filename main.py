from flask import Flask, request
import requests
import os
import threading
import time

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ===== MEMORY =====
user_memory = {}


# ================= TELEGRAM TYPING =================
def send_typing(chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
    payload = {
        "chat_id": chat_id,
        "action": "typing"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass


# typing loop while AI thinking
def typing_loop(chat_id, stop_flag):
    while not stop_flag["stop"]:
        send_typing(chat_id)
        time.sleep(4)


# ================= SEND MESSAGE =================
def send_message(chat_id, text):
    if not text:
        text = "Samajh nahi aya, thoda aur simple likh 🙂"

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

    if chat_id not in user_memory:
        user_memory[chat_id] = []

    user_memory[chat_id].append({"role": "user", "content": user_message})
    user_memory[chat_id] = user_memory[chat_id][-8:]

    messages = [
        {
            "role": "system",
            "content": """
You are ReplyShastra.

A boy will tell you his chat situation with a girl.

You must write the exact WhatsApp message he should send her.

Rules:
- Only the final sendable message
- Maximum 2 lines
- Natural Hinglish
- Soft respectful tone
- No explanation
- No advice
- No coaching
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
                "temperature": 0.7,
                "max_tokens": 80,
                "provider": {
                    "order": ["together","deepinfra","fireworks"],
                    "allow_fallbacks": True
                }
            },
            timeout=90
        )

        data = response.json()

        if "choices" in data:
            reply = data["choices"][0]["message"]["content"]
            user_memory[chat_id].append({"role": "assistant", "content": reply})
            return reply

        return "Thoda slow chal raha... fir se bhej 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server busy hai, 1 min baad bhej 🙂"


# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = message["chat"]["id"]
    user_message = message.get("text","")

    # ignore small msgs
    small_msgs = ["ok","okk","k","hmm","hmmm","hnn","hn","h"]
    if user_message.lower().strip() in small_msgs:
        return "ok"

    if user_message == "/start":
        user_memory[chat_id] = []
        send_message(chat_id,
"""Hi! Main ReplyShastra hoon 🙂

GF ignore, naraz, late reply — sab handle karenge.

Apni situation simple likh 👇""")
        return "ok"

    # ---- START TYPING THREAD ----
    stop_flag = {"stop": False}
    t = threading.Thread(target=typing_loop, args=(chat_id, stop_flag))
    t.start()

    # ---- AI CALL ----
    reply = get_ai_reply(chat_id, user_message)

    # stop typing
    stop_flag["stop"] = True

    send_message(chat_id, reply)

    return "ok"


@app.route("/")
def home():
    return "ReplyShastra Running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
