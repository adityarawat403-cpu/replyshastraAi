from flask import Flask, request
import requests
import os
import threading
import time

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ===== MEMORY STORE =====
user_memory = {}

# ================= TELEGRAM SEND =================
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        requests.post(url, json=payload, timeout=15)
    except:
        pass


# ================= TYPING ANIMATION =================
def typing_action(chat_id, stop_event):
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

    # store user message
    user_memory[chat_id].append({"role": "user", "content": user_message})
    user_memory[chat_id] = user_memory[chat_id][-12:]

    system_prompt = """
You are ReplyShastra.

A boy tells you what happened with his girlfriend.
Understand the situation and write the exact WhatsApp message he should send.

Rules:
- Only the final message
- Maximum 2 short lines
- Natural Hinglish
- Soft and respectful tone
- No advice
- No explanation
- No bullet points

Allowed emoji: ❤️ 🙂

Output must look exactly like a WhatsApp message.
"""

    messages = [{"role": "system", "content": system_prompt}] + user_memory[chat_id]

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-70b-8192",
                "messages": messages,
                "temperature": 0.85,
                "max_tokens": 120
            },
            timeout=60
        )

        # अगर Groq error दे
        if response.status_code != 200:
            print("STATUS ERROR:", response.text)
            return "Dubara bhej zara 🙂"

        data = response.json()

        # अगर choices missing
        if "choices" not in data:
            print("GROQ RAW:", data)
            return "Ek baar aur bhej 🙂"

        reply = data["choices"][0]["message"]["content"].strip()

        # blank reply protection
        if not reply or len(reply) < 2:
            return "Dubara likh 🙂"

        # save AI reply
        user_memory[chat_id].append({"role": "assistant", "content": reply})

        return reply

    except Exception as e:
        print("FULL ERROR:", e)
        return "Thoda network issue, fir bhej 🙂"


# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    user_message = data["message"].get("text", "")

    if not user_message:
        return "ok"

    # ===== START COMMAND =====
    if user_message.lower() == "/start":
        user_memory[chat_id] = []
        send_message(chat_id,
"""Hi! Main ReplyShastra hoon 🙂

GF ignore, naraz, breakup, late reply — sab handle karenge.

Apni situation simple likh 👇""")
        return "ok"

    # ===== TYPING THREAD START =====
    stop_event = threading.Event()
    t = threading.Thread(target=typing_action, args=(chat_id, stop_event))
    t.start()

    # ===== AI REPLY =====
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
