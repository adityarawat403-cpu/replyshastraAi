import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# -------- Telegram Send Function --------
def send_message(chat_id, text):
    requests.post(TELEGRAM_URL, json={
        "chat_id": chat_id,
        "text": text
    })

# -------- GROQ AI Reply --------
def get_ai_reply(user_message):

    prompt = f"""
Tu ek real Indian ladka dost hai — relationship expert nahi, dost.

User apni girlfriend/relationship problem leke aata hai.
Tera kaam:
1) Pehle uski situation samajh
2) Emotional support de
3) Fir practical advice de
4) Fir EXACT message likh jo wo ladki ko bhej sake

Rules:
- Hinglish me baat kar
- Human jaisa lagna chahiye (AI nahi)
- Kabhi mat bolna "as an AI"
- Short nahi — detailed helpful reply
- Ladke ki side samajh

User problem:
{user_message}
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
        "max_tokens": 800
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data
    )

    try:
        return response.json()["choices"][0]["message"]["content"]
    except:
        print("GROQ RESPONSE:", response.text)
        return "Bhai thoda network issue aa gaya... 10 sec baad fir likh 🙏"

# -------- Telegram Webhook --------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(chat_id,
            "Bhai aa gaya tu 🤝\n\n"
            "Main ReplyShastra hu — tera relationship dost.\n\n"
            "Apni problem normal language me likh:\n"
            "jaise — 'meri gf ignore kar rahi hai'")
            return "ok"

        reply = get_ai_reply(text)
        send_message(chat_id, reply)

    return "ok"

@app.route("/")
def home():
    return "ReplyShastra Running"
