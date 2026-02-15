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
        text = "Thoda clear likh na 🙂"

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

    # ---- create memory ----
    if chat_id not in user_memory:
        user_memory[chat_id] = []

    user_memory[chat_id].append({"role": "user", "content": user_message})

    # keep last 8 msgs only
    user_memory[chat_id] = user_memory[chat_id][-8:]


    messages = [
        {
            "role": "system",
            "content": """
You are ReplyShastra.

A boy will come to you with his chat situation with a girl.

You read his situation and write the exact message he should send her.

Write like a real Indian boy texting on WhatsApp.

Output format:
• Only the final message to send
• Maximum 2 short lines
• Natural Hinglish
• Soft and respectful tone

Do not explain.
Do not give advice.
Do not act like a coach.

Only the sendable message.
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
                "temperature": 0.8,
                "max_tokens": 120
            },
            timeout=90
        )

        data = response.json()

        if "choices" in data:
            reply = data["choices"][0]["message"]["content"]

            # save AI reply in memory
            user_memory[chat_id].append({"role": "assistant", "content": reply})

            return reply

        return "Network slow hai... 10 sec baad bhej 🙂"

    except Exception as e:
        print("ERROR:", e)
        return "Server busy hai... thodi der baad try kar 🙂"


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

Apni situation simple likh,
main tujhe exact message likh ke dunga jo tu send karega.""")
                return "ok"

            reply = get_ai_reply(chat_id, user_message)
            send_message(chat_id, reply)

    return "ok"


@app.route("/")
def home():
    return "ReplyShastra Running 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
