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
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://telegram.org",
                "X-Title": "ReplyShastra"
            },
            json={
                "model": "openrouter/auto",
                "temperature": 0.7,
                "max_tokens": 120,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a confident Indian male friend helping a boy text a girl on WhatsApp. "
                            "Always reply in casual Hinglish. "
                            "Reply must be only ONE ready-to-send message. "
                            "Maximum 2 short lines. "
                            "No paragraphs, no lists, no options, no explanation. "
                            "Do not sound like a girl or counselor. "
                            "Keep tone simple, direct, slightly emotional and natural like a real guy texting."
                        )
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            },
            timeout=90
        )

        data = response.json()

        if "choices" in data:
            reply = data["choices"][0]["message"]["content"]

            # extra safety: agar AI lamba likh de to kaat do
            reply = reply.split("\n")[0]
            if len(reply) > 220:
                reply = reply[:220]

            return reply
        else:
            print("OPENROUTER ERROR:", data)
            return "AI thoda busy hai... 20 sec baad fir bhejo 🙂"

    except Exception as e:
        print("SERVER ERROR:", e)
        return "Server connect nahi ho pa raha... thodi der baad try karo 🙂"


# Telegram webhook
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


# Home check
@app.route("/")
def home():
    return "ReplyShastra AI Running 🚀"


# Run server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
