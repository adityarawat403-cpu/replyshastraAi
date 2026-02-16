import os
import time
import requests
from flask import Flask, request

# ====== CONFIG ======
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

app = Flask(__name__)

# simple memory (per user)
user_memory = {}

# ====== SYSTEM PROMPT ======
SYSTEM_PROMPT = """
You are ReplyShastra.

You are NOT the girlfriend.
You are the boy’s close male friend helping him reply.

Your job:
Understand his relationship problem and write the exact WhatsApp message he should send to his girlfriend.

Rules:
- Output ONLY the message to send
- Max 2 short lines
- Natural Hinglish (Indian texting style)
- Soft, calm, emotionally mature tone
- No lecture
- No explanation
- No bullet points
- No coaching
- No asking user questions

Never act like therapist.
Never talk to user.
Never say "bro" in the final message.

Only generate the message he will copy-paste to her.
"""

# ====== TELEGRAM FUNCTIONS ======
def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def send_typing(chat_id):
    requests.post(f"{TELEGRAM_URL}/sendChatAction", json={
        "chat_id": chat_id,
        "action": "typing"
    })

# ====== GROQ CALL ======
def generate_reply(chat_id, user_text):

    if chat_id not in user_memory:
        user_memory[chat_id] = []

    user_memory[chat_id].append({"role": "user", "content": user_text})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += user_memory[chat_id][-8:]  # last few messages only

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 120
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
        data = response.json()

        reply = data["choices"][0]["message"]["content"].strip()

        user_memory[chat_id].append({"role": "assistant", "content": reply})

        return reply

    except Exception as e:
        print("GROQ ERROR:", e)
        return "Sorry thoda late ho gaya, ek baar fir bhejna 🙂"


# ====== TELEGRAM WEBHOOK ======
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    # /start command
    if text == "/start":
        send_message(chat_id,
            "Hi! Main ReplyShastra hoon 🙂\n\n"
            "GF ignore, naraz, breakup, late reply — sab handle karenge.\n\n"
            "Apni situation simple likh 👇"
        )
        return "ok"

    # typing animation
    send_typing(chat_id)
    time.sleep(5)

    reply = generate_reply(chat_id, text)

    send_message(chat_id, reply)

    return "ok"


@app.route("/", methods=["GET"])
def home():
    return "ReplyShastra Running"
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
