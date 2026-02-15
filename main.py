import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ---------------- SEND MESSAGE ----------------
def send_message(chat_id, text):
    if not text:
        text = "Samajh gaya... thoda aur detail me bata 🙂"

    parts = [text[i:i+3500] for i in range(0, len(text), 3500)]

    for part in parts:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": part
        }
        try:
            requests.post(url, json=payload, timeout=15)
        except:
            pass


# ---------------- AI REPLY ----------------
def get_ai_reply(user_message):

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
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
                        "content": """You are a 23 year old Indian boy chatting with his girlfriend on WhatsApp.

You are NOT an assistant.
You are NOT a coach.

You will write the EXACT message he should send her.

Rules:
- Only 1 final message
- Maximum 2 lines
- Hinglish only
- No explanation
- No advice
- No options
- Must look like real WhatsApp message
Only output the sendable message."""
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": 0.9,
                "max_tokens": 150
            },
            timeout=90
        )

        data = response.json()
        print("FULL AI:", data)

        reply = None

        # OpenAI style response
        if "choices" in data:
            choice = data["choices"][0]

            if "message" in choice and "content" in choice["message"]:
                reply = choice["message"]["content"]

            elif "text" in choice:
                reply = choice["text"]

        # Anthropic style response
        if not reply and "content" in data:
            if isinstance(data["content"], list):
                reply = data["content"][0].get("text")

        if not reply or reply.strip() == "":
            return "Thoda clearly bata na… kya hua exactly?"

        return reply.strip()

    except Exception as e:
        print("ERROR:", e)
        return "Network issue lag raha… 10 sec baad bhej 🙂"


# ---------------- TELEGRAM WEBHOOK ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "")

        if user_text == "/start":
            send_message(chat_id,
                "Hi! Main ReplyShastra hoon 🙂\n\nGF ignore, naraz, breakup, crush — sab handle karenge.\n\nApni situation detail me bata 👇\n(Main tujhe exact message likh ke dunga jo tu send karega)"
            )
            return "ok"

        ai_reply = get_ai_reply(user_text)
        send_message(chat_id, ai_reply)

    return "ok"


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
