import os
import requests
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# ================= ENV =================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SITE_URL = os.environ.get("SITE_URL")


# ================= TELEGRAM =================
def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })


def send_typing(chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendChatAction"
    requests.post(url, json={
        "chat_id": chat_id,
        "action": "typing"
    })


# ================= GROQ CORE =================
def ask_groq(prompt, temperature=0.5, max_tokens=400):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=40
    )

    res_json = response.json()
    return res_json["choices"][0]["message"]["content"]


# ================= SMART BRAIN =================
def detect_need_more_info(msg):
    msg = msg.lower()

    short_msgs = [
        "ignore", "gussa", "naraz", "block",
        "baat nahi", "reply nahi", "problem",
        "fight", "ladai"
    ]

    if len(msg.split()) <= 5:
        return True

    for word in short_msgs:
        if word in msg and len(msg.split()) < 12:
            return True

    return False


def ask_clarifying_question(user_message):
    prompt = f"""
You are a real Indian boy best friend.

User ne problem adhi batayi hai.
Abhi solution mat do.

Sirf 2-3 smart relevant questions pucho
taaki situation samajh aaye.

No advice
No lecture
No long text

User:
{user_message}

Speak Hinglish. Friendly bhai tone.
"""

    return ask_groq(prompt, 0.4, 150)


def get_ai_reply(user_message):

    # agar info kam hai → pehle pucho
    if detect_need_more_info(user_message):
        return ask_clarifying_question(user_message)

    master_prompt = f"""
You are ReplyShastra.

You are NOT an AI assistant.
You are a practical Indian male friend helping his bro fix relationship.

RULES:
- No long paragraphs
- No philosophy
- No poetry
- No therapist tone
- Talk like real caring friend
- Short but sharp

You must:

1 Understand what happened
2 Decode girl's emotions
3 Give clear steps
4 Write exact message to send her

User problem:
{user_message}

OUTPUT FORMAT:

Samjha kya hua:
(max 2 lines)

Ladki kyu react kar rahi:
(max 2 lines psychological reasoning)

Ab kya kar:
(bullet points, practical)

Usko ye message bhej:
(2-4 lines, natural Hinglish, copy paste ready)
"""

    try:
        return ask_groq(master_prompt, 0.5, 500)
    except Exception as e:
        print("AI ERROR:", e)
        return "Bhai thoda network slow ho gaya 😅 15 sec baad fir likh."


# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" not in data:
        return jsonify({"status": "ok"})

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    if text == "/start":
        send_telegram_message(chat_id, "Bhai welcome 😎\nApni problem detail me bata, main hoon na.")
        return jsonify({"status": "ok"})

    # typing feel
    send_typing(chat_id)
    time.sleep(2)

    reply = get_ai_reply(text)
    send_telegram_message(chat_id, reply)

    return jsonify({"status": "ok"})


# ================= ROOT =================
@app.route("/")
def home():
    return "ReplyShastra Running"


# ================= SET WEBHOOK =================
@app.route("/setwebhook")
def set_webhook():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={SITE_URL}/webhook"
    r = requests.get(url)
    return r.text


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
