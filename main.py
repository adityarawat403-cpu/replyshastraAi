import os
import requests
from flask import Flask, request

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

app = Flask(__name__)

def generate_reply(user_text):
    API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    payload = {
        "inputs": user_text,
        "parameters": {
            "max_new_tokens": 60,
            "temperature": 0.9,
            "do_sample": True
        }
    }

    try:
        r = requests.post(API_URL, headers=headers, json=payload, timeout=20)
        data = r.json()

        if isinstance(data, list) and "generated_text" in data[0]:
            reply = data[0]["generated_text"]
            return reply.strip()

        return "Hmm... samjh gaya 🙂 thoda aur batao"

    except:
        return "Network slow hai... 1 min baad try karo 🙂"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        reply = generate_reply(text)

        send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(send_url, json={
            "chat_id": chat_id,
            "text": reply
        })

    return "ok"


@app.route("/", methods=["GET"])
def home():
    return "ReplyShastra running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
