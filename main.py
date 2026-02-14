from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ---------------- TELEGRAM SEND ----------------
def send_message(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        requests.post(url, json=payload, timeout=20)
    except:
        pass


# ---------------- AI REPLY ----------------
def get_ai_reply(user_message):

    # fallback (VERY IMPORTANT)
    fallback = "Thoda ruk jaan… soch ke likh raha hu 🙂"

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "temperature": 0.8,
                "max_tokens": 120,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a 23 year old Indian boy chatting with his girlfriend on WhatsApp. You are NOT an assistant. Write the exact message he should send. Only ONE short Hinglish message. Max 2 lines. No advice. No explanation. No lists. No options. Only sendable WhatsApp text."
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            },
            timeout=45
        )

        data = response.json()
        print("OPENROUTER:", data)

        # -------- SMART PARSER (MAIN FIX) --------
        if "choices" in data and len(data["choices"]) > 0:
            msg = data["choices"][0]["message"]

            # normal response
            if "content" in msg and msg["content"]:
                return msg["content"].strip()

        return fallback

    except Exception as e:
        print("AI ERROR:", e)
        return fallback


# ---------------- WEBHOOK ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json

        if not data:
            return "ok"

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


# ---------------- HEALTH ----------------
@app.route("/")
def home():
    return "ReplyShastra Running"


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
