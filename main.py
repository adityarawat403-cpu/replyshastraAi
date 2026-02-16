import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ENV VARIABLES
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# -------------------- AI REPLY FUNCTION --------------------
def get_ai_reply(user_message):

    prompt = f"""
Tu ek real Indian ladka dost hai (best friend vibe).

User apni relationship problem leke aaya hai.

Tera kaam:
1) Pehle uski baat samajh
2) Thoda emotional support de (bhai wali tone)
3) Fir practical advice de
4) Aur LAST me exact message likh jo wo ladki ko copy paste bhej sake

Rules:
- Hinglish me bol
- Real lagna chahiye, AI nahi
- Judge nahi karna
- Uski side lena
- Short nahi — proper helpful reply dena

User ki baat:
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

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )

        res_json = response.json()
        print("GROQ:", res_json)

        return res_json["choices"][0]["message"]["content"]

    except Exception as e:
        print("AI ERROR:", e)
        return "Bhai thoda network ya AI issue aa gaya 😅 20 sec baad fir likh."


# -------------------- TELEGRAM SEND --------------------
def send_message(chat_id, text):

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("TELEGRAM ERROR:", e)


# -------------------- WEBHOOK --------------------
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()

    if "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    print("USER:", text)

    # START COMMAND
    if text == "/start":
        send_message(chat_id, "Bhai welcome 😎\nApni problem detail me bata, main hoon na.")
        return "ok"

    # AI reply
    ai_reply = get_ai_reply(text)

    # send back to telegram
    send_message(chat_id, ai_reply)

    return "ok"


# -------------------- HOME --------------------
@app.route("/")
def home():
    return "ReplyShastra Running"


# -------------------- RUN --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
