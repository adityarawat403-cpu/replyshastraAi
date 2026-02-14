import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")

# HuggingFace FREE model
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

def generate_reply(user_text):

    prompt = f"""
Give a short WhatsApp reply message (1-2 lines only).
No explanation.
User message: {user_text}
Reply:
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 60,
            "temperature": 0.8
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    try:
        result = response.json()
        reply = result[0]["generated_text"].split("Reply:")[-1].strip()
        return reply if reply else "hmm samjha... thoda aur bata"
    except:
        return "hmm... network slow hai, ek baar aur bhejo"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        if text == "/start":
            reply = "ReplyShastra AI Ready 🔥\nMessage bhejo."
        else:
            reply = generate_reply(text)

        send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(send_url, json={
            "chat_id": chat_id,
            "text": reply
        })

    return "ok"

@app.route("/", methods=["GET"])
def home():
    return "Bot Running"
