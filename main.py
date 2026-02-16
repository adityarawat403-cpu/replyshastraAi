from flask import Flask, request
import requests
import os
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
def show_typing(chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
    payload = {
        "chat_id": chat_id,
        "action": "typing"
    }
    try:
        for _ in range(5):   # ~5 seconds typing
            requests.post(url, json=payload, timeout=10)
            time.sleep(1)
    except:
        pass


# ================= AI REPLY (GROQ) =================
def get_ai_reply(chat_id, user_message):

    if chat_id not in user_memory:
        user_memory[chat_id] = []

    # store user msg
    user_memory[chat_id].append({"role": "user", "content": user_message})

    # keep last context
    user_memory[chat_id] = user_memory[chat_id][-12:]

    system_prompt = """
You are ReplyShastra.

A boy will tell you what happened with his girlfriend.

First understand the situation and her emotions.

Then write the exact WhatsApp message he should send her.

Rules:
- Only the message
- Maximum 2 short lines
- Natural Hinglish (real Indian texting)
- Soft, calm, emotionally mature tone

Never:
- give advice
- explain anything
- ask the user questions
- act like a coach

Allowed emoji: ❤️ or 🙂
Maximum one emoji.

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
                "temperature": 0.9,
                "max_tokens": 120
            },
            timeout=60
        )

        data = response.json()

        reply = data["choices"][0]["message"]["content"].strip()

        # save AI reply
        user_memory[chat_id].append({"role": "assistant", "content": reply})

        return reply

    except Exception as e:
        print("GROQ ERROR:", e)
        return "Ek sec… fir bhej 🙂"


# ================= WEBHOOK =================
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

GF ignore, naraz, breakup, late reply — sab handle karenge.

Apni situation simple likh 👇""")
                return "ok"

            # typing animation
            show_typing(chat_id)

            # AI reply
            reply = get_ai_reply(chat_id, user_message)

            send_message(chat_id, reply)

    return "ok"


@app.route("/")
def home():
    return "ReplyShastra Groq Running 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
