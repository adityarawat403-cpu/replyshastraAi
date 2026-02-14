from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# -------- USER MEMORY --------
users = {}


# -------- TELEGRAM SEND --------
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)


# -------- AI ADVICE --------
def get_advice(problem_text):

    prompt = f"""
You are an Indian relationship expert friend (not AI, not assistant).

Your job:
Help a boy handle his relationship situation.

Give:
1) Clear emotional understanding
2) Practical steps
3) 2–3 ready-to-send WhatsApp messages he can copy

Write in natural Hinglish.
Friendly tone.
Not robotic.
Not formal.

User problem:
{problem_text}
"""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "temperature": 0.9,
                "max_tokens": 600,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=60
        )

        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]

        return "Thoda network slow hai... dubara bhej 🙂"

    except:
        return "Server busy hai... 1 min baad fir try kar 🙂"


# -------- WEBHOOK --------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = message["chat"]["id"]

    if "text" not in message:
        return "ok"

    text = message["text"].lower()

    # -------- START --------
    if text == "/start":
        users[chat_id] = "waiting_problem"

        send_message(chat_id,
"""Hi! Main ReplyShastra AI hoon 😊

Main help kar sakta hoon:
• GF se baat kaise kare
• Crush ko kaise approach kare
• GF naraz ho to kaise manaye
• Breakup situation handle
• Seen ignore problem

Apni situation detail me batao 👇
(Main exact solution + ready messages dunga)""")

        return "ok"


    # -------- USER SENT PROBLEM --------
    if chat_id in users and users[chat_id] == "waiting_problem":

        send_message(chat_id, "Samajh raha hoon... 5 sec do, proper solution likh raha hoon ✍️")

        advice = get_advice(text)

        send_message(chat_id, advice)

        return "ok"


    # -------- DEFAULT --------
    send_message(chat_id, "Pehle /start likho 🙂")
    return "ok"


@app.route("/")
def home():
    return "ReplyShastra Running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
