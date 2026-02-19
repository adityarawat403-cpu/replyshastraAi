from flask import Flask, request
import requests
import os
import time

app = Flask(__name__)

# ===== TOKENS =====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ===== MEMORY =====
user_memory = {}

# ================= TELEGRAM TYPING =================
def typing(chat_id):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
        requests.post(url, json={"chat_id": chat_id, "action": "typing"}, timeout=5)
    except:
        pass


# ================= SEND MESSAGE =================
def send_message(chat_id, text):

    if not text:
        text = "Samajh gaya... thoda simple likh 🙂"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass


# ================= AI REPLY =================
def get_ai_reply(chat_id, user_message):

    # store memory
    if chat_id not in user_memory:
        user_memory[chat_id] = []

    user_memory[chat_id].append({"role": "user", "content": user_message})
    user_memory[chat_id] = user_memory[chat_id][-6:]  # last 6 messages

    messages = [
        {
            "role": "system",
            "content": """
You are ReplyShastra.

You are NOT an assistant.
You are NOT a coach.

from flask import Flask, request
import requests
import os
import time

app = Flask(__name__)

# ===== TOKENS =====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ===== MEMORY =====
user_memory = {}

# ================= TELEGRAM TYPING =================
def typing(chat_id):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
        requests.post(url, json={"chat_id": chat_id, "action": "typing"}, timeout=5)
    except:
        pass


# ================= SEND MESSAGE =================
def send_message(chat_id, text):

    if not text:
        text = "Samajh gaya... thoda simple likh 🙂"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass


# ================= AI REPLY =================
def get_ai_reply(chat_id, user_message):

    # store memory
    if chat_id not in user_memory:
        user_memory[chat_id] = []

    user_memory[chat_id].append({"role": "user", "content": user_message})
    user_memory[chat_id] = user_memory[chat_id][-6:]  # last 6 messages

    messages = [
        {
            "role": "system",
            "content": """
You are ReplyShastra.

You are NOT an assistant.
You are NOT a coach.

You are a real Indian male friend helping a boy handle his girlfriend situation.

Your task:
Understand his situation and write the exact message he should send her.

Rules:
- Only the final message
- Maximum 2 lines
- Natural Hinglish
- Soft respectful tone
- No lecture
- No explanation
- No bullet points
- No advice paragraphs
- No psychology

If she is angry → apology style message
If she is ignoring → calm non-needy message
If she said don't talk → respectful message
If confused → neutral caring message

Output must be copy-paste WhatsApp message only.
Nothing else.
"""
        }
    ] + user_memory[chat_id]

    try:
        # show typing while thinking
        typing(chat_id)
        time.sleep(2)

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gemma2-9b-it",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 120
            },
            timeout=60
        )

        data = response.json()

        if "choices" in data:
            reply = data["choices"][0]["message"]["content"].strip()

            user_memory[chat_id].append({"role": "assistant", "content": reply})
            return reply

        return "Thoda network slow tha... ek baar fir bhej 🙂"

    except Exception as e:
        print("GROQ ERROR:", e)
        return "Thoda network slow tha... ek baar fir bhej 🙂"


# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json

        if "message" not in data:
            return "ok"

        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        if not user_message:
            return "ok"

        # START COMMAND
        if user_message.lower() == "/start":
            user_memory[chat_id] = []
            send_message(chat_id,
"""Hi! Main ReplyShastra hoon 🙂

Apni situation simple likh.
Main tujhe exact message dunga jo tu usse bhejega 👇""")
            return "ok"

        reply = get_ai_reply(chat_id, user_message)
        send_message(chat_id, reply)

        return "ok"

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return "ok"


@app.route("/")
def home():
    return "ReplyShastra Running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
