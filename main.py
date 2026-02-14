from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)


def get_ai_reply(user_message):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://telegram.org",
                "X-Title": "ReplyShastra"
            },
            json={
                "model": "mistralai/mistral-7b-instruct:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are ReplyShastra, a smart Indian relationship and chat assistant. You reply in natural Hinglish like a real human. Give short, practical, emotional replies that user can directly copy-paste."
                    },
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.7
            },
            timeout=60
        )

        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return "AI thoda busy hai... 1 min baad try karo 🙂"

    except:
        return "Server busy hai... 1 min baad try karo 🙂"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        if user_message:
            reply = get_ai_reply(user_message)
            send_message(chat_id, reply)

    return "ok"


@app.route("/")
def home():
    return "ReplyShastra AI Running 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
