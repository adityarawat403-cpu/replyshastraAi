from flask import Flask, request
import requests
import os
import json

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
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://telegram.org",
                "X-Title": "ReplyShastra"
            },
            json={
                "model": "meta-llama/llama-3.1-8b-instruct:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a real Indian relationship advisor. Reply in natural Hinglish like a human. Short, emotional and practical. Give ready-to-send messages."
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 300
            },
            timeout=90
        )

        data = response.json()

        # DEBUG (important)
        print("OPENROUTER RESPONSE:", data)

        if "choices" in data:
            choice = data["choices"][0]

            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]

            if "text" in choice:
                return choice["text"]

        return "AI thoda soch raha hai… phir se bhejo 🙂"

    except Exception as e:
        print("ERROR:", e)
        return "AI server se reply nahi mila… 20 sec baad try karo 🙂"


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
