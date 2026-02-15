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
                        "content": """
You are ReplyShastra, a Hindi relationship assistant.

Your job:
- Write exact WhatsApp message user can send to girlfriend.
- Message must be natural Indian Hindi/Hinglish.
- Keep message 1–3 lines only.
- No explanation, no advice, ONLY message text.
- Emotional, caring, confident male tone.
- Never say you are an AI.
                        """
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            },
            timeout=30
        )

        data = response.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("AI ERROR:", e)
        return "Thoda ruk... abhi likh raha hoon 🙂"


@app.route("/", methods=["GET"])
def home():
    return "ReplyShastra running"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

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
