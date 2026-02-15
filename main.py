from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ===== MEMORY STORE =====
user_memory = {}
last_message_id = {}

# ================= SEND MESSAGE =================
def send_message(chat_id, text):

    if not text or text.strip() == "":
        text = "Samajh nahi aya bhai, thoda simple likh 🙂"

    parts = [text[i:i+3500] for i in range(0, len(text), 3500)]

    for part in parts:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": part,
            "parse_mode": "HTML"
        }
        try:
            requests.post(url, json=payload, timeout=20)
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
You are a real Indian 23-year-old boyfriend helping a friend handle his girlfriend texting situation.

Talk in natural Hinglish like a real guy.

Rules:
- No lectures
- No psychology explanation
- No long paragraphs
- Be practical
- Calm him first if he is anxious

If he asks what to send:
→ Give ONE exact WhatsApp message only (max 2 lines)

If girl said "sham ko baat karte":
→ tell him to wait and not double text
"""
        }
    ] + user_memory[chat_id]

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://telegram.org",
                "X-Title": "ReplyShastra"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 400
            },
            timeout=60
        )

        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            reply = data["choices"][0]["message"]["content"]

            user_memory[chat_id].append({"role": "assistant", "content": reply})
            return reply

        print("AI RAW:", data)
        return "Network slow hai bhai... 15 sec baad bhej 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server busy hai... thoda baad try kar 🙂"


# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json

        if not data:
            return "ok"

        if "message" not in data:
            return "ok"

        message = data["message"]
        chat_id = message["chat"]["id"]
        message_id = message["message_id"]

        # ---- DUPLICATE MESSAGE FIX ----
        if chat_id in last_message_id and last_message_id[chat_id] == message_id:
            return "ok"
        last_message_id[chat_id] = message_id

        user_message = message.get("text", "")

        if not user_message:
            send_message(chat_id, "Sirf text bhej bhai 🙂")
            return "ok"

        # ---- START COMMAND ----
        if user_message.lower() == "/start":
            user_memory[chat_id] = []
            send_message(chat_id,
"""Hi! Main ReplyShastra hoon 🙂

GF ignore, naraz, late reply — sab handle karenge.

Apni situation simple likh 👇""")
            return "ok"

        reply = get_ai_reply(chat_id, user_message)
        send_message(chat_id, reply)

    except Exception as e:
        print("WEBHOOK ERROR:", e)

    return "ok"


@app.route("/")
def home():
    return "ReplyShastra Running 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
