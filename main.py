from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# -------- SEND MESSAGE (ANTI LOOP) ----------
def send_message(chat_id, text):
    if not text:
        text = "Samajh nahi aya, ek baar aur simple me bata 🙂"

    parts = [text[i:i+3500] for i in range(0, len(text), 3500)]

    for part in parts:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": part
        }
        try:
            requests.post(url, json=payload, timeout=20)
        except:
            pass


# -------- AI REPLY ----------
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
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": """
You are ReplyShastra AI.

You talk like a real experienced Indian friend (not assistant).
You help boys handle relationship situations.

Your job:
1) First understand his situation
2) Explain what girl is thinking (psychology)
3) Tell what he should do
4) Then give ready-to-send WhatsApp message

Style:
- Hinglish
- Friendly
- Supportive
- Realistic
- No bullet point formatting
- No robotic tone
"""
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

        # DEBUG (very important)
        print("OPENROUTER RESPONSE:", data)

        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]

        return "Network thoda unstable lag raha... ek baar aur bhej 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server AI se connect nahi ho pa raha... 10 sec baad fir try karo 🙂"


# -------- WEBHOOK ----------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        if user_message:

            # /start greeting
            if user_message.lower() == "/start":
                greeting = """Hi! Main ReplyShastra hoon 🙂

GF ignore, naraz, breakup, crush — sab handle karenge.

Apni situation detail me bata 👇
(Main tujhe exact samjhaunga + ready message bhi dunga)"""
                send_message(chat_id, greeting)
                return "ok"

            reply = get_ai_reply(user_message)
            send_message(chat_id, reply)

    return "ok"


@app.route("/")
def home():
    return "ReplyShastra AI Running 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
