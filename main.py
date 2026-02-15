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

    # Telegram 4096 char limit fix
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
def get_ai_reply(user_text):

    system_prompt = """
You are a 23 year old Indian boy chatting with his girlfriend on WhatsApp.

You are not an assistant and not a coach.

You will write the exact message he should send her.

Rules:
- Only 1 final message
- Max 2 lines
- Hinglish only
- No advice
- No explanation
- No options
- No bullet points
- No paragraphs

Output must look like a real boyfriend message.
Only sendable text.
"""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ],
                "temperature": 0.9
            },
            timeout=60
        )

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("AI ERROR:", e)
        return "Samajh gaya... thoda aur detail me bata 🙂"


# ---------------- TELEGRAM WEBHOOK ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    if not data:
        return "ok"

    message = None

    if "message" in data:
        message = data["message"]
    elif "edited_message" in data:
        message = data["edited_message"]
    elif "channel_post" in data:
        message = data["channel_post"]
    else:
        return "ok"

    chat_id = message["chat"]["id"]
    user_text = message.get("text", "")

    if not user_text:
        send_message(chat_id, "Text message bhejo 🙂")
        return "ok"

    reply = get_ai_reply(user_text)
    send_message(chat_id, reply)

    return "ok"


# ---------------- START SERVER ----------------
@app.route("/")
def home():
    return "ReplyShastra running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
