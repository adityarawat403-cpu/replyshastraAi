from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ================= TOKENS =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ================= SEND MESSAGE (SAFE SPLIT) =================
def send_message(chat_id, text):
    if not text:
        text = "Samajh nahi aaya... thoda detail me bata 🙂"

    # Telegram limit 4096 — safe split
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


# ================= AI REPLY =================
def get_ai_reply(user_message):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://replyshastra.ai",
                "X-Title": "ReplyShastra",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "temperature": 0.85,
                "max_tokens": 900,
                "messages": [
                    {
                        "role": "system",
                        "content": """
You are ReplyShastra — a smart Indian relationship advisor friend.

You talk like a real 23-27 year old Indian male best friend, not like an AI.

Your job:
Understand the user's relationship situation and give:
1) Clear explanation of what the girl/boy is thinking psychologically
2) What mistake the user is doing (if any)
3) Exact step-by-step what he should do next
4) Then give 2-3 READY-TO-SEND messages he can copy paste

Style rules:
- Hinglish (natural)
- Friendly "bhai" tone
- No robotic language
- No "as an AI"
- No bullet points symbols like •
- Write like WhatsApp chat
- Emotional + practical

If user writes short message like:
"meri gf ignore kar rahi hai"
→ you MUST still give full solution.

Never ask for unnecessary details first.
First help, then ask small clarification if needed.
"""
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
        print("OPENROUTER RESPONSE:", data)

        # ======= PARSER (handles both formats) =======
        if "choices" in data and len(data["choices"]) > 0:
            message = data["choices"][0]["message"]

            # normal string response
            if isinstance(message.get("content"), str):
                return message["content"].strip()

            # list response format
            if isinstance(message.get("content"), list):
                for part in message["content"]:
                    if "text" in part:
                        return part["text"].strip()

        return "Network thoda slow hai… ek baar fir bhej 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server busy hai… 20 sec baad try kar 🙂"


# ================= TELEGRAM WEBHOOK =================
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

        # ignore commands except /start
        if user_message == "/start":
            welcome = """Hi! Main ReplyShastra hoon 🙂

GF ignore, naraz, breakup, crush — sab handle karenge.

Apni situation detail me bata 👇
(Main tujhe exact samjhaunga + ready message bhi dunga)"""
            send_message(chat_id, welcome)
            return "ok"

        reply = get_ai_reply(user_message)
        send_message(chat_id, reply)

        return "ok"

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return "ok"


# ================= HEALTH CHECK =================
@app.route("/")
def home():
    return "ReplyShastra Running 🚀"


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
