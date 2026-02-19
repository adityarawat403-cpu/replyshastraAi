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


# ================= REAL BOT BRAIN =================
SYSTEM_PROMPT = """
You are ReplyShastra.

You are NOT an AI assistant.
You are a real Indian male best friend and relationship fixer.

Your only job:
Help the user handle his girlfriend situation and save the relationship.

IMPORTANT BEHAVIOR:
- No lectures
- No long advice
- No therapist talk
- Think deeply internally
- Speak shortly and smartly

You must internally detect:
• her emotion (hurt, ego, disrespect, insecurity, jealousy)
• what message will calm her and make her reply

USER DOES NOT WANT ADVICE.
USER WANTS A MESSAGE THAT WORKS.

OUTPUT RULES (STRICT):

1) First write 1-2 lines explaining why she is angry
2) Then write ONE single copy-paste message for girlfriend
3) Hinglish natural language only
4) No poetry
5) No multiple options
6) No long paragraphs
7) No robotic language
8) Only 1 emoji allowed (❤️ or 🥺)

FORMAT EXACTLY:

[Why she is angry]
(short explanation)

[Send this message]
(one single message only)

Never ask questions to the user.
Never behave like a counselor.
Behave like an experienced elder brother who fixes relationships.
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
        "temperature": 0.95,
        "max_tokens": 700
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        res = response.json()

        return res["choices"][0]["message"]["content"]

    except Exception as e:
        print("AI ERROR:", e)
        return "Bhai thoda network issue aaya... ek baar fir bhej."


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
                     "Bhai welcome 🤝\nApni problem simple likh.\nMain tujhe exact message dunga jo tu usse bhejega.")
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
