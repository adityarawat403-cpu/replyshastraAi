import os
import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ================= ENV VARIABLES =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SITE_URL = os.getenv("SITE_URL")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


# ================= TELEGRAM FUNCTIONS =================
def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        requests.post(url, json=payload, timeout=15)
    except:
        pass


def typing(chat_id, seconds=2):
    url = f"{TELEGRAM_API}/sendChatAction"
    payload = {
        "chat_id": chat_id,
        "action": "typing"
    }
    try:
        requests.post(url, json=payload, timeout=10)
        time.sleep(seconds)
    except:
        pass


# ================= BOT BRAIN =================
SYSTEM_PROMPT = """
You are ReplyShastra.

You are NOT an AI assistant.
You are a real Indian male best friend and relationship fixer.

Goal:
Help the user handle his girlfriend situation and save the relationship.

Behavior rules:
- No lectures
- No psychology terms
- No long paragraphs
- No therapist style
- Think deeply internally but speak short
- Talk like a calm experienced elder brother

You must internally detect:
• why she reacted
• what emotion she felt (hurt, ego, disrespect, insecurity)
• what message will calm her

User DOES NOT want advice.
User ONLY wants a message that works.

STRICT OUTPUT FORMAT:

[Why she is angry]
(short 1-2 line explanation in Hinglish)

[Send this message]
(one single copy-paste message only, natural Hinglish, max 3 lines)

Rules for the message:
- Only ONE message
- No multiple options
- No poetry
- No big paragraphs
- No robotic language
- Only 1 emoji allowed (❤️ or 🥺)
- Message must bring her closer, not defensive
- Do NOT ask the user any question

Never break format.
"""


# ================= AI FUNCTION (OPENROUTER) =================
def ask_ai(user_text):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": SITE_URL,
        "X-Title": "ReplyShastra",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.85,
        "max_tokens": 500
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        res = response.json()

        if "choices" in res:
            return res["choices"][0]["message"]["content"].strip()

        if "error" in res:
            print("OPENROUTER ERROR:", res)
            return "AI thoda busy hai... 10 sec baad fir bhej."

        return "Mujhe properly samajh nahi aaya... ek baar clearly likh."

    except Exception as e:
        print("AI EXCEPTION:", str(e))
        return "Connection drop ho gaya... fir se bhej."


# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" not in data:
        return jsonify({"status": "ok"})

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    # START COMMAND
    if text == "/start":
        send_message(chat_id,
                     "Bhai welcome 🤝\nApni situation simple likh.\nMain tujhe exact message dunga jo tu usse bhejega.")
        return jsonify({"status": "ok"})

    # typing animation
    typing(chat_id, 3)

    # AI reply
    ai_reply = ask_ai(text)

    # send
    send_message(chat_id, ai_reply)

    return jsonify({"status": "ok"})


@app.route("/", methods=["GET"])
def home():
    return "ReplyShastra Running"
