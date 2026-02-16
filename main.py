from flask import Flask, request
import requests
import os
import threading
import time

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# typing animation
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


# send message
def send_message(chat_id, text):
    if not text:
        text = "phir se likh na 🙂"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})


# ===== AI REPLY =====
def get_ai_reply(user_message):

    system_prompt = """
You are ReplyShastra.

User will tell his situation with a girl.

You write ONLY the exact WhatsApp message he should send her.

Rules:
- max 2 lines
- natural Hinglish
- soft respectful tone
- no advice
- no explanation
- no coaching
Return only the message.
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
                "temperature": 0.7,
                "max_tokens": 120
            },
            timeout=60
        )

        data = response.json()
        print("RAW:", data)

        if "choices" in data:
            msg = data["choices"][0]["message"]["content"]

            # array case fix
            if isinstance(msg, list):
                return msg[0]["text"]

            return msg

        return None

    except Exception as e:
        print("AI ERROR:", e)
        return None


# webhook
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

Apni situation simple likh 👇""")
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
        send_message(chat_id, "thoda detail me likh 🙂")

    return "ok"


@app.route("/")
def home():
    return "running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
