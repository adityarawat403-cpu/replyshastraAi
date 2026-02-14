from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Tokens
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# Telegram ko reply bhejne ka function
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)


# AI se reply lene ka function
def get_ai_reply(user_message):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "temperature": 0.7,
                "max_tokens": 120,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a 23 year old Indian boy chatting with his girlfriend on WhatsApp. You are NOT an assistant. You write the exact message he should send her. Only 1 message, maximum 2 lines, Hinglish only, emotional, natural human texting style. No advice, no explanation, no lists, no options. Only sendable WhatsApp text."
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            },
            timeout=60
        )

        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()

        return "Thoda network slow hai… 10 sec baad fir bhejo 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server busy hai… 20 sec baad try karo 🙂"


# Telegram webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json

        if "message" not in data:
            return "ok"

        message = data["message"]

        if "text" not in message:
            return "ok"

        chat_id = message["chat"]["id"]
        user_message = message["text"]

        reply = get_ai_reply(user_message)
        send_message(chat_id, reply)

        return "ok"

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return "ok"


# Health check
@app.route("/")
def home():
    return "ReplyShastra running"


# Run server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
