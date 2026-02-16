from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ================= USER MEMORY =================
user_memory = {}

# ================= TELEGRAM SEND =================
def send_message(chat_id, text):
    if not text:
        text = "Hmm... dubara bhej 🙂"

    parts = [text[i:i+3500] for i in range(0, len(text), 3500)]

    for part in parts:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": part
        }
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
    user_memory[chat_id] = user_memory[chat_id][-10:]


    system_prompt = """
You are ReplyShastra.

A boy will share what his girlfriend said or what happened between them.

First understand her emotion:
angry, hurt, disappointed, missing him, testing him, or caring.

Then write the exact WhatsApp message he should send her.

Your job is NOT advice.
Your job is NOT coaching.

Your job is to make the girl feel:
understood, respected, and emotionally heard.

Rules:
- Only the final message
- Maximum 2 short lines
- Natural Hinglish
- Calm and genuine tone
- No explanation
- No bullet points
- No instructions to the user

Very important:
Do not change topic.
Reply directly to what she felt.

If she is hurt → acknowledge and take responsibility.
If she is angry → calm and soft.
If she is caring → appreciative.
If she is ignoring → light and non-needy.

Write like a real Indian boyfriend texting.

Allowed emoji: ❤️ or 🙂
Max: one emoji.
"""

    messages = [{"role": "system", "content": system_prompt}] + user_memory[chat_id]

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 140
            },
            timeout=90
        )

        data = response.json()

        # -------- SMART PARSER (important fix) --------
        if "choices" in data and len(data["choices"]) > 0:
            msg = data["choices"][0]["message"]

            if isinstance(msg.get("content"), str):
                reply = msg["content"].strip()

            elif isinstance(msg.get("content"), list):
                reply = ""
                for part in msg["content"]:
                    if "text" in part:
                        reply += part["text"]

            else:
                reply = "Ek sec… fir bhej 🙂"

            user_memory[chat_id].append({"role": "assistant", "content": reply})
            return reply

        return "Network slow hai… 20 sec baad bhej 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server busy hai… thoda baad try kar 🙂"


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

        # ---- start command ----
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

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return "ok"


# ================= HEALTH CHECK =================
@app.route("/")
def home():
    return "ReplyShastra Running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
