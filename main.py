from flask import Flask, request
import requests
import os
import time

app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API = os.environ.get("GROQ_API")

TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# ----------- AI Brain -------------
def ask_ai(user_text):

    prompt = f"""
Tu ek AI nahi hai.

Tu ek real ladka dost hai.
User tera bhai hai.
Wo apni relationship bachane ke liye tere paas aaya hai.

Rules:
- Pehle situation samajh
- Usko judge nahi karna
- Ladki ban ke reply nahi dena
- Sirf usse samjha aur solution de
- Phir LAST me ek ready-to-send message bhi likh de

User problem:
{user_text}
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=25
        )

        result = r.json()

        reply = result["choices"][0]["message"]["content"]
        return reply

    except Exception as e:
        print("GROQ ERROR:", e)
        return "Bhai thoda network issue aa gaya… 10 sec baad fir likh 🙏"


# -------- Telegram Webhook ----------
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    if "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    if text == "/start":
        welcome = """
Bhai aa gaya tu 🤝

Main ReplyShastra hu — tera relationship dost.

Apni problem normal language me likh:
jaise — "meri gf ignore kar rahi hai"
"""
        requests.post(TELEGRAM_URL, json={"chat_id": chat_id, "text": welcome})
        return "ok"

    # typing delay realism
    time.sleep(1)

    reply = ask_ai(text)

    requests.post(
        TELEGRAM_URL,
        json={
            "chat_id": chat_id,
            "text": reply
        }
    )

    return "ok"


@app.route("/")
def home():
    return "ReplyShastra running"
