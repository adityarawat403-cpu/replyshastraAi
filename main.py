from flask import Flask, request
import requests
import os
import time

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# -------- MEMORY --------
user_memory = {}

# -------- TELEGRAM SEND --------
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)


# -------- TYPING ANIMATION --------
def send_typing(chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
    payload = {"chat_id": chat_id, "action": "typing"}
    try:
        requests.post(url, json=payload, timeout=5)
    except:
        pass


# -------- AI REPLY --------
def get_ai_reply(chat_id, user_message):

    # memory create
    if chat_id not in user_memory:
        user_memory[chat_id] = []

    # save user message
    user_memory[chat_id].append({"role": "user", "content": user_message})

    # keep last 12 msgs
    user_memory[chat_id] = user_memory[chat_id][-12:]

    system_prompt = """
You are ReplyShastra.

A boy will tell you his situation with his girlfriend.

Your job:
Read his message and write the exact WhatsApp message he should send to her.

Rules:
- Only write the message he should send
- Max 2 short lines
- Natural Hinglish
- Soft calm tone
- Emotionally understanding
- No explanation
- No advice
- No coaching
- No bullet points
- No asking questions to the user

Write like a real Indian boyfriend texting.

Output only the final sendable message.
"""

    messages = [{"role": "system", "content": system_prompt}] + user_memory[chat_id]

    try:

        # show typing while AI thinks
        for _ in range(4):
            send_typing(chat_id)
            time.sleep(1.2)

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "temperature": 0.7
            },
            timeout=60
        )

        data = response.json()

        if "choices" in data:
            reply = data["choices"][0]["message"]["content"].strip()

            # save ai memory
            user_memory[chat_id].append({"role": "assistant", "content": reply})

            return reply

        return "Thoda network issue aa gaya, 10 sec baad bhej 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server thoda busy hai, 20 sec baad bhej 🙂"


# -------- WEBHOOK --------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        if user_message:

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


@app.route("/")
def home():
    return "ReplyShastra Running 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
