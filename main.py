from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SITE_URL = os.getenv("SITE_URL")


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
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": SITE_URL,
                "User-Agent": "ReplyShastraBot"
            },
            json={
                "model": "mistralai/mistral-7b-instruct:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a real human-like Indian chat assistant. Reply in natural Hinglish, emotional, short and practical like WhatsApp chat. Never long paragraphs."
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": 0.9,
                "max_tokens": 250
            },
            timeout=90
        )

        data = response.json()
        print("OPENROUTER RESPONSE:", data)

        if "choices" in data:
            return data["choices"][0]["message"]["content"]

        return "Network slow hai... ek baar aur bhejo 🙂"

    except Exception as e:
        print("ERROR:", e)
        return "Server thoda busy hai... 20 sec baad try karo 🙂"


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
