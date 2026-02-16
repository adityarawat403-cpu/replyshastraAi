import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

SYSTEM_PROMPT = """
You are ReplyShastra — a real caring male best friend.
You talk in Hinglish.
You understand emotions first, then give advice.
Never act like AI.
Always:
1) First understand situation
2) Then emotionally connect
3) Then give exact message user should send

Tone: real friend, protective, supportive.
Keep replies 6-10 lines.
"""

def ask_groq(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        llama-3.1-8b-instant
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.7
    }

    r = requests.post(url, headers=headers, json=data)

    print("GROQ RAW:", r.text)   # IMPORTANT debug

    try:
        return r.json()['choices'][0]['message']['content']
    except:
        return None


def send_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(TELEGRAM_URL, json=payload)


@app.route("/", methods=["GET"])
def home():
    return "Bot Running"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" not in data:
        return jsonify({"ok": True})

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    if text == "/start":
        send_message(chat_id, "Bhai aa gaya tu 🤝\nApni problem normal language me likh.")
        return jsonify({"ok": True})

    reply = ask_groq(text)

    if reply:
        send_message(chat_id, reply)
    else:
        send_message(chat_id, "Bhai thoda network issue aa gaya... 10 sec baad fir likh 🙏")

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
