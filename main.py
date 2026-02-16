import os
import requests
import json
import time
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

SYSTEM_PROMPT = """
You are ReplyShastra.

You are NOT a girlfriend.
You are NOT the user.

You are his warning-free honest male best friend.

Your job:
- First understand the emotional situation
- Analyze what the girl actually felt
- Then suggest what the boy should say
- Then give 1 ready-to-send message.

Style:
Talk like a real Indian friend (Hinglish).
Short, real, emotionally intelligent.
No cringe. No over-romantic lines.
No long paragraphs.

Always structure reply:

1) Situation samjha:
2) Ladki kya feel kar rahi:
3) Tu kya kare:
4) Ye message bhej:
"""

def ask_groq(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        r = requests.post(url, headers=headers, json=data, timeout=25)
        res = r.json()
        return res["choices"][0]["message"]["content"]
    except Exception as e:
        print("GROQ ERROR:", e)
        return "Bhai thoda network issue aaya… 1 min baad fir likh 🙏"

def send_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(TELEGRAM_URL, json=payload)

@app.route("/", methods=["GET"])
def home():
    return "ReplyShastra running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]

    if "text" not in data["message"]:
        return "ok"

    user_text = data["message"]["text"]

    if user_text == "/start":
        send_message(chat_id,
        "Bhai aa gaya main 🤝\n\nTension mat le.\nJo bhi hua simple bata — main samjha ke sahi message likhwa dunga.")
        return "ok"

    # typing delay realism
    time.sleep(6)

    reply = ask_groq(user_text)

    send_message(chat_id, reply)

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
