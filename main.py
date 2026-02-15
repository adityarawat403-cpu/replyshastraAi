import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


def ask_ai(user_message):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://replyshastraai-production.up.railway.app",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-chat:free",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are ReplyShastra, a Hindi relationship assistant.
Write only the exact WhatsApp message user should send.
1-3 lines only.
No explanation.
Natural Hinglish.
Emotional and caring tone."""
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            },
            timeout=40
        )

        # DEBUG PRINT
        print("RAW AI:", response.text)

        data = response.json()

        # SAFE PARSE (IMPORTANT FIX)
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
        else:
            return "Sun na... thoda sa busy tha, par main yahin hoon. Baat karni ho to message kar dena 🙂"

    except Exception as e:
        print("AI FAILURE:", e)
        return "Thoda network slow hai... par main yahin hoon 🙂"


@app.route("/", methods=["GET"])
def home():
    return "ReplyShastra Working"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("TELEGRAM UPDATE:", data)

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "")

        ai_reply = ask_ai(user_text)

        requests.post(TELEGRAM_URL, json={
            "chat_id": chat_id,
            "text": ai_reply
        })

    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
