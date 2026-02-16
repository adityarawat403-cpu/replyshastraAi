from flask import Flask, request
import requests
import os
import time
import threading

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ========= MEMORY =========
user_memory = {}

# ========= TELEGRAM SEND =========
def send_message(chat_id, text):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    try:
        requests.post(url, json=payload, timeout=20)
    except:
        pass


# ========= TYPING ANIMATION =========
def typing(chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
    payload = {
        "chat_id": chat_id,
        "action": "typing"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass


# ========= AI REPLY =========
def get_ai_reply(chat_id, user_message):

    # save user message
    if chat_id not in user_memory:
        user_memory[chat_id] = []

    user_memory[chat_id].append({"role": "user", "content": user_message})

    # keep last 10 messages
    user_memory[chat_id] = user_memory[chat_id][-10:]


    system_prompt = """
You are ReplyShastra.

A boy will tell you his situation about a girl.

Your job:
Write the exact WhatsApp message he should send her.

Rules:
- Only the message to send
- Maximum 2 short lines
- Natural Hinglish
- Soft respectful tone
- No explanation
- No advice
- No coaching

Never ask questions to the user.
Never write paragraphs.
Just the sendable message.
"""


    messages = [{"role": "system", "content": system_prompt}] + user_memory[chat_id]

    try:

        # typing animation while thinking
        for i in range(3):
            typing(chat_id)
            time.sleep(2)

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 120,
                "top_p": 1
            },
            timeout=90
        )

        data = response.json()

        reply = data["choices"][0]["message"]["content"].strip()

        # save AI reply
        user_memory[chat_id].append({"role": "assistant", "content": reply})

        return reply

    except Exception as e:
        print("GROQ ERROR:", e)
        return "Thoda network slow hai, 20 sec baad try kar 🙂"


# ========= WEBHOOK =========
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

GF ignore, naraz, late reply — sab handle karenge.

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
