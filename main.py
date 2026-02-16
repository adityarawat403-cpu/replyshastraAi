from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ---------------- AI REPLY ----------------
def get_ai_reply(user_message):

    prompt = f"""
Tu ek real Indian ladka dost hai.

User relationship problem leke aaya hai.
Pehle usko samajh,
fir emotional support,
fir practical advice,
aur last me exact message likh jo wo ladki ko bhej sake.

Hinglish me bol.

User: {user_message}
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 700
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=25
        )

        res_json = response.json()
        return res_json["choices"][0]["message"]["content"]

    except Exception as e:
        print("AI ERROR:", e)
        return "Bhai thoda network/AI issue aa gaya 😅 20 sec baad fir likh."

# ---------------- TELEGRAM SEND ----------------
def send_telegram(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

# ---------------- WEBHOOK ----------------
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()

    if "message" not in data:
        return jsonify({"ok": True})

    chat_id = data["message"]["chat"]["id"]
    user_text = data["message"].get("text", "")

    print("USER:", user_text)

    # /start command
    if user_text == "/start":
        send_telegram(chat_id, "Bhai main hu 🤝\nApni problem bata, milke set karte hain.")
        return jsonify({"ok": True})

    # AI reply
    reply = get_ai_reply(user_text)

    # SEND BACK TO TELEGRAM
    send_telegram(chat_id, reply)

    return jsonify({"ok": True})

@app.route("/")
def home():
    return "ReplyShastra Running"
