from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ===== TOKENS =====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ===== MEMORY =====
users = {}
last_update_id = None


# ===== TELEGRAM SEND =====
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)


# ===== AI ADVICE FUNCTION =====
def get_advice(user_message):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "temperature": 0.8,
                "max_tokens": 400,
                "messages": [
                    {
                        "role": "system",
                        "content": """You are ReplyShastra AI — a smart Indian relationship expert.

You talk like a real elder brother/friend, not an AI assistant.

Your job:
Understand the boy's situation and give him:
1) Clear explanation of what is happening with the girl
2) Exact steps he should take
3) 2-3 ready-to-send messages he can copy paste

Rules:
- Write in natural Hinglish
- Emotional and practical tone
- Not robotic
- No disclaimers
- No AI talk
- Structured but simple
- Avoid long paragraphs
"""
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            },
            timeout=60
        )

        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()

        return "Network thoda slow hai… 10 sec baad fir bhej 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server busy hai… thodi der baad try kar 🙂"


# ===== WEBHOOK =====
@app.route("/webhook", methods=["POST"])
def webhook():
    global last_update_id

    data = request.json

    # ---- DUPLICATE PROTECTION ----
    if "update_id" in data:
        if last_update_id == data["update_id"]:
            return "ok"
        last_update_id = data["update_id"]

    if "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = message["chat"]["id"]

    if "text" not in message:
        return "ok"

    text = message["text"].lower()

    # ===== START COMMAND =====
    if text == "/start":
        users[chat_id] = "waiting_problem"

        send_message(chat_id,
"""Hi! Main ReplyShastra AI hoon 😊

Main help kar sakta hoon:
• GF ignore
• GF naraz
• Crush approach
• Seen problem
• Breakup situation

Apni situation detail me batao 👇
(Main exact solution + ready messages dunga)""")

        return "ok"

    # ===== USER PROBLEM =====
    if chat_id in users and users[chat_id] == "waiting_problem":

        send_message(chat_id, "Samajh gaya... thoda soch ke proper solution de raha hoon ✍️")

        advice = get_advice(text)

        send_message(chat_id, advice)

        return "ok"

    return "ok"


# ===== HEALTH CHECK =====
@app.route("/")
def home():
    return "ReplyShastra AI Running"


# ===== RUN =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
