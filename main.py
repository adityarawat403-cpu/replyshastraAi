import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# ---------- Telegram Send ----------
def send_message(chat_id, text):
    try:
        requests.post(TELEGRAM_URL, json={
            "chat_id": chat_id,
            "text": text
        })
    except Exception as e:
        print("Telegram Send Error:", e)

# ---------- AI Reply ----------
def get_ai_reply(user_message):

    prompt = f"""
Tu ek real Indian ladka dost hai.

User relationship problem leke aaya hai.
Pehle usko samajh,
fir emotional support,
fir practical advice,
aur last me exact message likh jo wo ladki ko bhej sake.

Hinglish me bol.

User: {user_message}
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 700
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=25
        )

        res_json = response.json()
        print("GROQ RESPONSE:", res_json)

        return res_json["choices"][0]["message"]["content"]

    except Exception as e:
        print("AI ERROR:", e)
        return "Bhai AI thoda soch raha hai 🤯 20 sec baad fir likh."

# ---------- Webhook ----------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" not in data:
        return jsonify({"status": "no message"})

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    # start command
    if text == "/start":
        send_message(chat_id,
        "Bhai aa gaya tu 🤝\n"
        "Apni problem likh — main help karta hu.")
        return "ok"

    # typing message
    send_message(chat_id, "Soch raha hu bhai... 🤔")

    reply = get_ai_reply(text)

    send_message(chat_id, reply)

    return "ok"

@app.route("/")
def home():
    return "ReplyShastra Running"
