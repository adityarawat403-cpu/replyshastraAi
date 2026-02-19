import os
import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ================= ENV =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


# ================= TELEGRAM SEND =================
def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)


def typing(chat_id, seconds=2):
    url = f"{TELEGRAM_API}/sendChatAction"
    payload = {
        "chat_id": chat_id,
        "action": "typing"
    }
    requests.post(url, json=payload)
    time.sleep(seconds)


# ================= BOT BRAIN =================
SYSTEM_PROMPT = """
You are ReplyShastra.

You are not an AI assistant.
You are a real Indian male best friend who fixes relationship situations.

Your goal:
Understand the situation and produce a message that makes the girlfriend reply.

Rules:
- No lectures
- No therapy talk
- No long explanations
- Think internally, speak shortly
- Natural Hinglish
- No poetry
- Only useful talk

You must detect her emotion:
hurt / ego / disrespect / feeling ignored / trust break

Output format STRICTLY:

[Why she is angry]
(1-2 short lines max)

[Send this message]
(ONE single message only to copy paste)

Only 1 emoji allowed (🥺 or ❤️)
Do NOT give multiple options.
Do NOT talk to the user in long paragraphs.
"""

# ================= GROQ AI =================
def ask_ai(user_text):

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gemma2-9b-it",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.9,
        "max_tokens": 600
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=40)

        # DEBUG (IMPORTANT)
        print("RAW AI RESPONSE:", response.text)

        res = response.json()

        # ---- SAFE RESPONSE PARSER ----
        if "choices" in res:
            return res["choices"][0]["message"]["content"]

        if "error" in res:
            print("GROQ ERROR:", res["error"])
            return "Thoda busy tha server... ek baar detail me fir likh."

        return "Samjha nahi properly... ek baar clearly likh."

    except Exception as e:
        print("AI EXCEPTION:", str(e))
        return "Net unstable tha... ab fir se bhej."


# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" not in data:
        return jsonify({"status": "ok"})

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    # /start command
    if text == "/start":
        send_message(chat_id,
        "Bhai welcome 🤝\nApni situation simple likh.\nMain tujhe exact message dunga jo tu usse bhejega.")
        return jsonify({"status": "ok"})

    # typing animation realistic
    typing(chat_id, 3)

    # AI reply
    ai_reply = ask_ai(text)

    # send message
    send_message(chat_id, ai_reply)

    return jsonify({"status": "ok"})


# ================= HOME =================
@app.route("/", methods=["GET"])
def home():
    return "ReplyShastra Running"
