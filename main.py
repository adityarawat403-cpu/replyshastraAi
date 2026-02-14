import os
import requests
from flask import Flask, request

app = Flask(__name__)

# ENV VARIABLES
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

# HuggingFace model
API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}


# -------- AI GENERATE REPLY --------
def generate_reply(user_text):

    prompt = f"""
Tum ek smart Indian relationship advisor ho.
Ladke ko apni girlfriend se kya bolna chahiye — usko natural Hinglish me suggest karo.
Short, realistic aur WhatsApp style reply dena.

User: {user_text}
Advisor:
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 120,
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        data = response.json()

        if isinstance(data, list):
            return data[0]["generated_text"].replace(prompt, "").strip()

        return "Thoda wait karo... soch raha hu 🤔"

    except Exception as e:
        return "Network slow hai... phir bhejo 🙂"


# -------- TELEGRAM WEBHOOK --------
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()

    if "message" not in data:
        return "ok"

    message = data["message"]

    if "text" not in message:
        return "ok"

    chat_id = message["chat"]["id"]
    text = message["text"]

    send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    # INSTANT RESPONSE (Telegram timeout fix)
    requests.post(send_url, json={
        "chat_id": chat_id,
        "text": "Soch raha hu... 🤔"
    })

    if text == "/start":
        requests.post(send_url, json={
            "chat_id": chat_id,
            "text": "ReplyShastra AI Active 🔥\nApni problem bhejo."
        })
        return "ok"

    # AI reply
    reply = generate_reply(text)

    requests.post(send_url, json={
        "chat_id": chat_id,
        "text": reply
    })

    return "ok"


# -------- RAILWAY PORT --------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
