import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")

# ----------- AI FUNCTION -----------
def generate_reply(user_message):
    API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    payload = {
        "inputs": user_message
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        data = response.json()

        if isinstance(data, list):
            return data[0]["generated_text"]
        else:
            return "Soch raha hu... phir se bhejo 🤔"
    except:
        return "Server busy hai, thodi der me try karo 😅"

# ----------- TELEGRAM WEBHOOK -----------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        reply = "ReplyShastra Bot Active 🔥\nMujhse kuch bhi baat karo 😎"
    else:
        reply = generate_reply(text)

    send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    requests.post(send_url, json={
        "chat_id": chat_id,
        "text": reply
    })

    return "ok"

# ----------- RAILWAY PORT -----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
