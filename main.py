from flask import Flask, request
import requests
import os
import threading
import time

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# -------------------- TYPING ANIMATION --------------------
def send_typing(chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
    payload = {"chat_id": chat_id, "action": "typing"}
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def typing_loop(chat_id, stop_flag):
    while not stop_flag["stop"]:
        send_typing(chat_id)
        time.sleep(4)


# -------------------- SEND MESSAGE --------------------
def send_message(chat_id, text):
    if not text:
        text = "thoda aur clear likh 🙂"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})


# -------------------- AI REPLY --------------------
def get_ai_reply(user_message):

    system_prompt = """
You are ReplyShastra — a conversation repair expert.

A boy will tell you what happened between him and a girl.
Your job is to fix the conversation and help him emotionally reconnect.

You must understand BOTH:
• what the girl is feeling
• what the boy actually wants

Then write the exact WhatsApp message he should send her.

Your reply must feel like a real Indian boy texting — not an AI.

STYLE:
- Natural Hinglish
- Emotionally intelligent
- Calm, caring and mature
- Soft reassuring tone

RULES:
- ONLY the final sendable message
- Maximum 2 short lines
- No advice
- No explanation
- No coaching
- No bullet points
- No lecture
- No over romantic cheesy lines

BEHAVIOR:
If girl is hurt → acknowledge her feelings
If girl is angry → calm + responsibility
If boy made mistake → sincere acceptance
If she said bye/don’t talk → low pressure respectful message
If she feels unimportant → reassure value

Goal: rebuild comfort and trust.

Return only the message text.
"""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.5,
                "max_tokens": 120
            },
            timeout=60
        )

        data = response.json()
        print("AI:", data)

        if "choices" in data:
            reply = data["choices"][0]["message"]["content"]
            return reply.strip()

        return None

    except Exception as e:
        print("AI ERROR:", e)
        return None


# -------------------- WEBHOOK --------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = message["chat"]["id"]
    user_message = message.get("text","")

    if user_message == "/start":
        send_message(chat_id,
"""Hi! Main ReplyShastra hoon 🙂

Apni situation likh — mai tujhe exact message likh ke dunga jo tu send karega 👇""")
        return "ok"

    # typing start
    stop_flag = {"stop": False}
    t = threading.Thread(target=typing_loop, args=(chat_id, stop_flag))
    t.start()

    reply = get_ai_reply(user_message)

    stop_flag["stop"] = True

    if reply:
        send_message(chat_id, reply)
    else:
        send_message(chat_id, "samajh gaya… thoda detail me likh 🙂")

    return "ok"


@app.route("/")
def home():
    return "ReplyShastra Running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
