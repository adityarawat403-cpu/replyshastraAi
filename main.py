import os
import requests
from flask import Flask, request

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

app = Flask(__name__)

def generate_reply(user_text):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/llama-3.1-8b-instruct:free"
        "messages": [
            {
                "role": "system",
                "content": "You are ReplyShastra, an expert relationship advisor. Reply in Hinglish like a smart, emotional friend. Give practical message suggestions user can send."
            },
            {
                "role": "user",
                "content": user_text
            }
        ]
    }

    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        response = r.json()
        return response["choices"][0]["message"]["content"]

    except Exception as e:
        return "Server thoda busy hai... 1 min baad try karo 🙂"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        reply = generate_reply(text)

        send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(send_url, json={
            "chat_id": chat_id,
            "text": reply
        })

    return "ok"


@app.route("/", methods=["GET"])
def home():
    return "ReplyShastra AI Running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
