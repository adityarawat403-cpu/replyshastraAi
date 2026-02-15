from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ================= TOKENS =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ================= SEND TELEGRAM MESSAGE =================
def send_message(chat_id, text):
    if not text:
        text = "Thoda detail me bata bhai 🙂"

    # telegram max 4096 chars -> split safety
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


# ================= AI REPLY FUNCTION =================
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
                        "content": """
You are NOT an AI assistant.

You are a 23 year old Indian boyfriend helping another boy handle his girlfriend texting situation on WhatsApp.

Your personality:
- calm
- experienced
- emotionally intelligent
- practical
- protective like an older brother

You do NOT behave like a coach, therapist, teacher, counselor or article writer.

You talk like a real Indian guy in natural Hinglish.

VERY IMPORTANT BEHAVIOR RULES:

1) Girls delaying replies usually does NOT mean loss of interest.
It is usually:
- emotional processing
- overthinking what to say
- needing space
- testing emotional pressure
- avoiding conflict

2) If the user sounds desperate or anxious:
First calm him.

3) Neediness pushes girls away.
Stop the user from:
- double texting
- repeated calling
- asking "kya hua", "reply kyu nahi"

4) When girl says:
"baad me baat karte hain"
"sham ko batati hu"
It means she needs space.
Correct action = wait + one supportive message only.

5) Always give clear action.

6) If user asks for a message:
Give ONLY ONE ready-to-send WhatsApp message.

Message rules:
- Hinglish
- max 2 lines
- no options
- no numbering
- no explanation
- must feel human
- caring but not needy

7) Never write long lectures.

8) No psychology terms.

Goal:
stabilize situation,
prevent panic texting,
restart conversation naturally.

When giving sendable message → output ONLY the message text.
"""
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 180
            },
            timeout=90
        )

        data = response.json()
        print("OPENROUTER:", data)

        # ===== SMART PARSER (VERY IMPORTANT FIX) =====
        if "choices" in data:
            msg = data["choices"][0]["message"]

            # normal
            if isinstance(msg.get("content"), str):
                return msg["content"].strip()

            # array case (some models)
            if isinstance(msg.get("content"), list):
                for part in msg["content"]:
                    if "text" in part:
                        return part["text"].strip()

        return "Network slow hai... 10 sec baad fir bhej 🙂"

    except Exception as e:
        print("ERROR:", e)
        return "Server busy hai... 1 min baad try karo 🙂"


# ================= TELEGRAM WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        if user_message:

            # /start greeting
            if user_message.lower() == "/start":
                send_message(chat_id,
"""Hi! Main ReplyShastra hoon 🙂

GF ignore, naraz, breakup — sab handle karenge.

Apni situation simple likh 👇
(Main tujhe kya karna hai + exact message dunga)""")
                return "ok"

            reply = get_ai_reply(user_message)
            send_message(chat_id, reply)

    return "ok"


# ================= HOME =================
@app.route("/")
def home():
    return "ReplyShastra AI Running 🚀"


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
