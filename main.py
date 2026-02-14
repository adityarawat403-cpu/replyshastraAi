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
                "messages": [
                    {
                        "role": "system",
                        "content": """You are NOT the boyfriend.

You help a boy write a WhatsApp message to send to his girlfriend.

Write ONLY the exact message he should send.

Tone:
Normal Indian boy. Simple, natural and real. Slight caring but not dramatic.

Strict Rules:
- Only 1 message
- Maximum 2 lines
- Hinglish only
- No "baby", "jaan", "shona", "cutie"
- No poetry
- No long emotional paragraphs
- No advice
- No explanation
- No options
- No lists

It must look like a real human typed WhatsApp message.
Only sendable text."""
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 120
            },
            timeout=90
        )

        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
        else:
            return "Net slow lag raha... 10 sec baad fir bhej 🙂"

    except Exception as e:
        print("ERROR:", e)
        return "Server busy hai... 1 min baad try kar 🙂"


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
