import os
import requests
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
SITE_URL = os.getenv("SITE_URL")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ---------------- TELEGRAM SEND ---------------- #

def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)


def typing(chat_id, sec=2):
    requests.post(f"{TELEGRAM_API}/sendChatAction",
                  json={"chat_id": chat_id, "action": "typing"})
    time.sleep(sec)

# ---------------- AI BRAIN ---------------- #

SYSTEM_PROMPT = """
You are ReplyShastra.

You are NOT an assistant.
You are a real Indian male best friend ("bhai").

Your job:
First deeply understand user's relationship problem.
Then emotionally support him.
Then give smart practical guidance.
Then write ONE exact message the user can copy paste to send to his girlfriend.

Rules:
- Talk in natural Hinglish (Hindi + simple English).
- No cringe poetry.
- No long lectures.
- No robotic language.
- Do NOT repeat user's words.
- Focus on saving the relationship.
- Message for girlfriend must be ONE clean message only.
- Never write multiple options.
- Never act like a therapist.
- Act like an experienced older brother.

Response format STRICTLY:

[Understanding]
(short 2-3 lines what actually happened emotionally)

[What she felt]
(why she reacted)

[What you should do]
(clear practical steps)

[Send this message]
(ONLY the message to copy paste, nothing else)
"""

def ask_ai(user_text):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": SITE_URL,
        "X-Title": "ReplyShastra"
    }

    data = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        result = response.json()
        return result["choices"][0]["message"]["content"]

    except Exception as e:
        print("AI ERROR:", e)
        return "Bhai thoda server busy hai, 10 sec baad fir bhej."

# ---------------- WEBHOOK ---------------- #

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" not in data:
        return jsonify({"ok": True})

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    # /start
    if text == "/start":
        send_message(chat_id,
        "Bhai welcome 🤝\nApni problem simple likh.\nMain tujhe exact message dunga jo tu usse bhejega.")
        return jsonify({"ok": True})

    # show typing
    typing(chat_id, 3)

    # AI reply
    ai_reply = ask_ai(text)

    send_message(chat_id, ai_reply)

    return jsonify({"ok": True})


@app.route("/")
def home():
    return "ReplyShastra Running"
