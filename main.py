import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# ---------- reply function ----------
def generate_reply(user_text):
    return f"Tumne bola: {user_text}"

# ---------- ROOT ----------
@app.route("/", methods=["GET"])
def home():
    return "Bot Alive"

# ---------- WEBHOOK ----------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return "no data"

    message = data.get("message")
    if not message:
        return "no message"

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        reply = "ReplyShastra Bot Active 🔥"
    else:
        reply = generate_reply(text)

    send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(send_url, json={
        "chat_id": chat_id,
        "text": reply
    })

    return "ok"

# ---------- RAILWAY PORT ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
