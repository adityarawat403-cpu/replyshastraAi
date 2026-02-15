from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ===== MEMORY STORE =====
user_memory = {}

# ================= SEND MESSAGE =================
def send_message(chat_id, text):
    if not text:
        text = "Samajh nahi aya... thoda simple likh 🙂"

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

    # ---- MEMORY ADD ----
    if chat_id not in user_memory:
        user_memory[chat_id] = []

    user_memory[chat_id].append({"role": "user", "content": user_message})
    user_memory[chat_id] = user_memory[chat_id][-8:]

    messages = [
        {
            "role": "system",
            "content": """
You are ReplyShastra — a WhatsApp reply writer.

Your job is ONLY to write the exact message the user should send to his girlfriend.

Important Behaviour Rules:
1. Never abuse the girl
2. Never insult the girl
3. Never use words like chutiya, toxic, game, ego, alpha
4. Never lecture the user
5. Never explain psychology
6. Never give long advice

You are NOT a dating coach.
You are NOT a love guru.
You only write the message to send.

Response Style:

If user says:
msg de
what should I send
gf ignore kar rahi hai
wo naraz hai

→ Reply with ONLY ONE WhatsApp message
→ Maximum 2 lines
→ Soft calm tone
→ No emojis except ❤️ or 🙂 (max 1)

If girl said "sham ko baat karte"
→ Tell him to wait
→ Do NOT write a message

Do not add explanation
Do not add bullet points
Output must look exactly like a WhatsApp message only.
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
                "temperature": 0.5
            },
            timeout=90
        )

        data = response.json()

        if "choices" in data:
            reply = data["choices"][0]["message"]["content"].strip()

            # safety cleanup
            if len(reply) > 400:
                reply = reply[:400]

            user_memory[chat_id].append({"role": "assistant", "content": reply})
            return reply

        return "Network slow hai... 20 sec baad bhej 🙂"

    except Exception as e:
        print("ERROR:", e)
        return "Server busy hai... thoda baad try kar 🙂"


# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        user_message = message.get("text", "")

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
