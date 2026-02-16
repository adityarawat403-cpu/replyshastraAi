import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API = os.environ.get("GROQ_API_KEY")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"


# ---------------- TELEGRAM SEND ---------------- #

def send_message(chat_id, text):
    requests.post(
        TELEGRAM_URL + "sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        },
        timeout=20
    )


def send_typing(chat_id):
    requests.post(
        TELEGRAM_URL + "sendChatAction",
        json={
            "chat_id": chat_id,
            "action": "typing"
        },
        timeout=10
    )


# ---------------- AI BRAIN ---------------- #

def ask_ai(user_text):

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {GROQ_API}",
            "Content-Type": "application/json"
        }

        system_prompt = f"""
Tu ek AI chatbot nahi hai.

Tu ek real dost hai — ek experienced ladka jo relationship situations samajhta hai.

Tera kaam:
1) Pehle user ki situation ko samajh
2) Ladki ki psychology explain kar
3) User ki galti ya issue identify kar
4) Phir exact message likh jo user ladki ko bheje

Rules:
- User ko 'bhai' bol
- Hinglish me likh
- Short realistic lines
- No cringe shayari
- No motivational speech
- Ladki ban kar reply mat dena
- Practical advice dena
- End me COPY PASTE message alag line me clearly likh

User situation:
{user_text}
"""

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()

        if "choices" not in data:
            print("GROQ RAW RESPONSE:", data)
            return "Bhai thoda soch raha hu situation... 5 sec baad fir likh 🤔"

        reply = data["choices"][0]["message"]["content"]
        return reply

    except Exception as e:
        print("AI ERROR:", e)
        return "Bhai thoda network lag gaya dimag pe 😅 5 sec baad fir likh"


# ---------------- WEBHOOK ---------------- #

@app.route("/", methods=["GET"])
def home():
    return "ReplyShastra running"


@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    if "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    user_text = data["message"].get("text", "")

    if not user_text:
        return "ok"

    # Start command
    if user_text.lower() == "/start":
        send_message(chat_id,
                     "Bhai aa gaya tu 🤝\n\nMain ReplyShastra hu — tera relationship dost.\n\nApni problem normal language me likh:\nExample: 'meri gf gussa hai' ")
        return "ok"

    # typing animation
    send_typing(chat_id)

    # AI reply
    reply = ask_ai(user_text)

    send_message(chat_id, reply)

    return "ok"


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
